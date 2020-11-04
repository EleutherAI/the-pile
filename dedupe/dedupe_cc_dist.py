import argparse
import os
import pickle
import signal
from signal import SIGINT, SIG_IGN
import sys
import glob

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

from pathlib import Path

# Multiprocessing
def compare_pair(m1, m2, tqdm_func, global_tqdm):
    return m1.jaccard(m2) > 0.5

def process_batch(pool, batch, start_offset, working_directory): 
    checkpoint_file = os.path.join(working_directory, "checkpoint.pkl")
    checkpoint_temp_file = os.path.join(working_directory, "checkpoint_temp.pkl")
    checkpoint_old_file = os.path.join(working_directory, "checkpoint_old.pkl")    
    transaction_lock = os.path.join(working_directory, ".transaction_lock")

    # Generate minhashes with pool
    tasks = []
    for (pair, m1, m2) in batch:
        task = (compare_pair, (pair, m1, m2))
        tasks.append(task)

    on_done = lambda _ : None
    on_error = lambda _ : None
    results = pool.map(None, tasks, on_error, on_done)

    # Commence Transaction
    previous_signal_int = signal.signal(SIGINT, SIG_IGN)
    Path(transaction_lock).touch()
    last_offset = start_offset + len(batch)

    # Dump Duplicates
    duplicates = []

    for i, is_duplicate in enumerate(results):
        if not is_duplicate:
            continue

        pair, _, _ = batch[i]
        duplicates.append(pair)

    duplicates_file = os.path.join(working_directory, f"duplicates_{start_offset}.pkl")
    pickle.dump(duplicates, open(duplicates_file, "wb"))

    # Dump Checkpoint                
    pickle.dump(last_offset, open(checkpoint_temp_file, "wb"))

    # Move stuff around safely in case of failure
    if os.path.exists(checkpoint_file):
        os.rename(checkpoint_file, checkpoint_old_file)
    os.rename(checkpoint_temp_file, checkpoint_file)

    # Transaction Finished
    os.remove(transaction_lock)
    signal.signal(SIGINT, previous_signal_int)    

def load_minhashes(working_directory):
    document_count = CommonCrawlDataset().num_docs()

    files = glob.glob(os.path.join(working_directory, "minhashes*"))

    total_file_size = 0
    for file in files:
        total_file_size += (os.path.getsize(file))

    count = 0
    minhashes = [None] * document_count
    logger.info(f"minhash array length {len(minhashes):,}")
    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
        for file in files:
            document_data = pickle.load(open(file, "rb"))
            for document in document_data:
                (priority, offset, sha256sum, minhash) = document
                if not minhashes[offset]:
                    count += 1

                minhashes[offset] = document

            progress.update(os.path.getsize(file))

    difference = document_count - count
    logger.info(f"Expected document count: {document_count:,}")
    logger.info(f"Loaded documents with minhashes count: {count:,}")
    logger.info(f"Difference {difference:,}")

    return minhashes

def get_pair_count(working_directory):
    pair_count_file = os.path.join(working_directory, "pair_count.pkl")
    if os.path.exists(pair_count_file):
        return pickle.load(open(pair_count_file, "rb"))

    document_count = CommonCrawlDataset().num_docs()
    pair_count = 0
    for i in range(document_count):
        for j in range(i+1, document_count):
            pair_count += 1

    pickle.dump(pair_count, open(pair_count_file, "wb"))
    return pair_count

def main(working_directory, process_count, instance_count, instance):  
    # Load All Minhashes
    logger.info(f"Loading minhashes")
    minhashes = load_minhashes(working_directory)

    # Batching
    pair_count = get_pair_count(working_directory)
    pairs_per_instance = int(pair_count / instance_count)
    offset_start = pairs_per_instance * instance
    next_offset = offset_start + pairs_per_instance
    logger.info(f"Total pairs: {pair_count:,}")
    logger.info(f"Number of instances: {instance_count}")
    logger.info(f"Pairs per instance: {pairs_per_instance:,}")
    logger.info(f"Currently running instance: {instance}")
    logger.info(f"Offset Start: {offset_start:,}")
    logger.info(f"Next Offset Start: {next_offset:,}")

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

    if os.path.exists(checkpoint_file):
        checkpoint_offset = pickle.load(open(checkpoint_file, "rb")) + 1 
        logger.info(f"Checkpoint found, starting from offset {checkpoint_offset:,}")            
    else:
        logger.info(f"No checkpoint found, starting from offset {offset_start:,}")
        checkpoint_offset = offset_start

    batch_size = 100000 # Pair batch size, not minhash batch size
    batch = []
    pool = TqdmMultiProcessPool(process_count)

    with tqdm.tqdm(total=checkpoint_offset, dynamic_ncols=True, unit="pairs") as progress:
        offset = -1
        document_count = CommonCrawlDataset().num_docs()
        for i in range(document_count):
            for j in range(i+1, document_count):
                offset += 1

                if offset < checkpoint_offset:
                    progress.update()
                    continue

                if offset == checkpoint_offset:
                    progress.reset(total=pairs_per_instance)
                    progress.update(checkpoint_offset - offset_start)

                if not offset < next_offset:
                    break

                batch.append((i,j), minhashes[i], minhashes[j])

                if len(batch) == batch_size:
                    process_batch(pool, batch, working_directory)
                    batch = []
                    progress.update(batch_size)

            if len(batch) != 0:
                process_batch(pool, batch, working_directory)
                progress.update(len(batch))

parser = argparse.ArgumentParser(description='Distributed dedupe using minhash.')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("--instance_count", type=int, default=1)
parser.add_argument("--instance", type=int, default=0)

if __name__ == '__main__':
    logfile_path = "dedupe_cc_dist.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count, args.instance_count, args.instance)