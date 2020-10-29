import argparse
import os
import pickle
import json
import sys
import time
import signal
from signal import SIGINT, SIG_IGN

import nltk
from nltk.util import ngrams
from datasketch import MinHash, LeanMinHash, MinHashLSH
import tqdm
from tqdm_multiprocess import TqdmMultiProcessPool

from the_pile.datasets import CommonCrawlDataset
from the_pile.utils import sha256str

import logging
from the_pile.logger import setup_logger_tqdm
logger = logging.getLogger(__name__)

def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]

def generate_minhash(document, tqdm_func, global_tqdm):

    n_grams = extract_ngrams(document, 5)
    five_gram_set = set(n_grams)
    minhash = MinHash(num_perm=10)
    for five_gram in five_gram_set:
        minhash.update(five_gram.encode('utf8'))

    return LeanMinHash(minhash)

def minhash_lsh_dedupe(lsh, minhash, priority, offset, sha256sum):
    # start = time.perf_counter()
    results = lsh.query(minhash)
    # elapsed = time.perf_counter() - start
    # print(f"Query took {elapsed:0.5f} seconds.")

    for json_results in results:
        found_priority, found_offset, found_sha256sum = json.loads(json_results)

        if priority < found_priority:
            return (priority, offset, sha256sum)

        if priority == found_priority:
            if offset == found_offset: # Self
                return None
            else:
                return (priority, offset, sha256sum)

        # Want to keep document from higher priority set
        if priority > found_priority:
            # start = time.perf_counter()
            lsh.remove(json_results)
            lsh.insert(json.dumps((priority, offset, sha256sum)), minhash)
            # elapsed = time.perf_counter() - start
            # print(f"Remove and insert took {elapsed:0.5f} seconds.")
            return json_results

    # Duplicate not found, insert self
    # start = time.perf_counter()
    lsh.insert(json.dumps((priority, offset, sha256sum)), minhash)   
    # elapsed = time.perf_counter() - start
    # print(f"Insert took {elapsed:0.5f} seconds.")

def docs_for_dedupe():
    # format: ((priority, offset, sha256sum), document)
    dset = CommonCrawlDataset()
    i = -1
    for doc in dset.documents():
        i += 1
        yield (100, i, sha256str(doc.encode('utf-8'))), doc

from pathlib import Path

def main(working_directory, process_count):

    nltk.download('punkt')

    total_file_size = CommonCrawlDataset().size()
    checkpoint_file = os.path.join(working_directory, "checkpoint.pkl")
    checkpoint_old_file = os.path.join(working_directory, "checkpoint_old.pkl")    
    transaction_lock = os.path.join(working_directory, ".transaction_lock")

    if os.path.exists(transaction_lock):
        logger.info("Program crashed during transaction, you need to fix the files...")

    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit_scale=1) as progress:
        if os.path.exists(checkpoint_file):
            lsh, checkpoint_offset = pickle.load(open(checkpoint_file, "rb"))
            logger.info(f"Checkpoint found, starting from offset {checkpoint_offset}")            
        else:
            logger.info("No checkpoint found, starting from offset 0")
            lsh = MinHashLSH(threshold=0.5, num_perm=10)
            checkpoint_offset = 0

        batch_size = 1000
        batch = []
        pool = TqdmMultiProcessPool(process_count)

        for doc in docs_for_dedupe():
            ((priority, offset, sha256sum), document) = doc

            if offset < checkpoint_offset:
                progress.update(len(document))
                continue

            batch.append(doc)

            if len(batch) == batch_size:
                # Generate minhashes with pool
                tasks = []
                for ((priority, offset, sha256sum), document) in batch:
                    task = (generate_minhash, (document,))
                    tasks.append(task)

                on_done = lambda _ : None
                on_error = on_done
                minhashes = pool.map(progress, tasks, on_error, on_done)

                # Commence Transaction
                previous_signal_int = signal.signal(SIGINT, SIG_IGN)
                Path(transaction_lock).touch()

                # Operate On LSH                
                start_offset = batch[0][0][1]
                last_offset = batch[-1][0][1]
                duplicate_file = os.path.join(working_directory, f"duplicates_{start_offset}.txt")
                duplicate_file_temp = os.path.join(working_directory, f"duplicates_{start_offset}_temp.txt")
                with open(duplicate_file_temp,"w") as fh:
                    for i, minhash in enumerate(minhashes):
                        ((priority, offset, sha256sum), document) = batch[i]
                        result = minhash_lsh_dedupe(lsh, minhash, priority, offset, sha256sum)
                        if result:
                            priority, offset, sha256sum = result
                            fh.write(f"{priority} {offset} {sha256sum}\n")

                        progress.update(len(document))

                # Dump Checkpoint
                checkpoint_temp = os.path.join(working_directory, "checkpoint_temp.pkl")
                pickle.dump((lsh, last_offset), open(checkpoint_temp, "wb"))

                # Move stuff around safely in case of failure
                if os.path.exists(checkpoint_file):
                    os.rename(checkpoint_file, checkpoint_old_file)
                os.rename(checkpoint_temp, checkpoint_file)
                os.rename(duplicate_file_temp, duplicate_file)

                # Transaction Finished
                os.remove(transaction_lock)
                signal.signal(SIGINT, previous_signal_int)
                batch = []

parser = argparse.ArgumentParser(description='Dedupe from provided indexes.')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count)