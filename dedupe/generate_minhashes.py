import argparse
import os
import pickle
import json
import sys
import time
import signal
from signal import SIGINT, SIG_IGN
import multiprocessing

import nltk
from nltk.util import ngrams
from datasketch import MinHash, LeanMinHash
import tqdm
from tqdm_multiprocess import TqdmMultiProcessPool

from the_pile.datasets import CommonCrawlDataset
from the_pile.utils import sha256str

import logging
from the_pile.logger import setup_logger_tqdm
logger = logging.getLogger(__name__)

# class CustomPickleDump():
#     def init(self, file_name):
#         self.file_name = file_name

#     def __enter__(self):
#         self.fh = open(self.file_name,"wb")

#     def add(self, object_to_pickle):
#         pickled = pickle.dumps(object_to_pickle)
#         self.fh.write(bytearray(len(pickled)))
#         self.fh.write(pickled)

#     def __exit__(self):
#         self.fh.close()

def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]

# Multiprocessing
def generate_minhash(document, tqdm_func, global_tqdm):
    n_grams = extract_ngrams(document, 5)
    five_gram_set = set(n_grams)
    minhash = MinHash(num_perm=10)
    for five_gram in five_gram_set:
        minhash.update(five_gram.encode('utf8'))

    return LeanMinHash(minhash)

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
    checkpoint_temp_file = os.path.join(working_directory, "checkpoint_temp.pkl")
    checkpoint_old_file = os.path.join(working_directory, "checkpoint_old.pkl")    
    transaction_lock = os.path.join(working_directory, ".transaction_lock")

    if os.path.exists(transaction_lock):
        logger.info("Program crashed during transaction, fixing files...")
        # Just re-do from last safe checkpoint (overwrite minhashes)
        if os.path.exists(checkpoint_temp_file):
            if os.path.exists(checkpoint_old_file):
                os.rename(checkpoint_old_file, checkpoint_file)
            os.remove(checkpoint_temp_file)
        else:
            pass

        os.remove(transaction_lock)        

    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
        if os.path.exists(checkpoint_file):
            checkpoint_offset = pickle.load(open(checkpoint_file, "rb"))
            logger.info(f"Checkpoint found, starting from offset {checkpoint_offset}")            
        else:
            logger.info("No checkpoint found, starting from offset 0")
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
                start_offset = batch[0][0][1]
                last_offset = batch[-1][0][1]

                # Dump Minhashes
                minhashes_and_meta = []               

                for i, minhash in enumerate(minhashes):
                    ((priority, offset, sha256sum), document) = batch[i]
                    minhashes_and_meta.append((priority, offset, sha256sum, minhash))
                    progress.update(len(document))

                minhashes_file = os.path.join(working_directory, f"minhashes_{start_offset}.pkl")
                pickle.dump(minhashes_and_meta, open(minhashes_file, "wb"))

                # Dump Checkpoint                
                pickle.dump(last_offset, open(checkpoint_temp_file, "wb"))

                # Move stuff around safely in case of failure
                if os.path.exists(checkpoint_file):
                    os.rename(checkpoint_file, checkpoint_old_file)
                os.rename(checkpoint_temp_file, checkpoint_file)

                # Transaction Finished
                os.remove(transaction_lock)
                signal.signal(SIGINT, previous_signal_int)
                batch = []

parser = argparse.ArgumentParser(description='Generating minhashes for cc')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count)