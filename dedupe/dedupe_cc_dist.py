import argparse
import os
import pickle
import signal
from signal import SIGINT, SIG_IGN
import sys

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

def process_batch(pool, batch, progress, working_directory):
    pass
    # checkpoint_file = os.path.join(working_directory, "checkpoint.pkl")
    # checkpoint_temp_file = os.path.join(working_directory, "checkpoint_temp.pkl")
    # checkpoint_old_file = os.path.join(working_directory, "checkpoint_old.pkl")    
    # transaction_lock = os.path.join(working_directory, ".transaction_lock")

    # # Generate minhashes with pool
    # tasks = []
    # for ((priority, offset, sha256sum), document) in batch:
    #     task = (generate_minhash, (document,))
    #     tasks.append(task)

    # on_done = lambda _ : None
    # on_error = on_done
    # minhashes = pool.map(progress, tasks, on_error, on_done)

    # # Commence Transaction
    # previous_signal_int = signal.signal(SIGINT, SIG_IGN)
    # Path(transaction_lock).touch()
    # start_offset = batch[0][0][1]
    # last_offset = batch[-1][0][1]

    # # Dump Minhashes
    # minhashes_and_meta = []               

    # for i, minhash in enumerate(minhashes):
    #     ((priority, offset, sha256sum), document) = batch[i]
    #     minhashes_and_meta.append((priority, offset, sha256sum, minhash))
    #     progress.update(len(document))

    # minhashes_file = os.path.join(working_directory, f"minhashes_{start_offset}.pkl")
    # pickle.dump(minhashes_and_meta, open(minhashes_file, "wb"))

    # # Dump Checkpoint                
    # pickle.dump(last_offset, open(checkpoint_temp_file, "wb"))

    # # Move stuff around safely in case of failure
    # if os.path.exists(checkpoint_file):
    #     os.rename(checkpoint_file, checkpoint_old_file)
    # os.rename(checkpoint_temp_file, checkpoint_file)

    # # Transaction Finished
    # os.remove(transaction_lock)
    # signal.signal(SIGINT, previous_signal_int)    

def load_minhashes(working_directory):
    minhashes_files = []
    document_count = CommonCrawlDataset().num_docs()
    batch_size = 1000 # Used elsewhere - careful!
    offset = 0
    total_file_size = 0
    while offset < document_count:
        minhashes_file = os.path.join(working_directory, f"minhashes_{offset}.pkl")
        offset += batch_size
        total_file_size += (os.path.getsize(minhashes_file))

    minhashes = []
    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
        for minhashes_file in minhashes_files:
            minhashes_temp = pickle.load(open(minhashes_file, "rb"))
            for minhash in minhashes_temp:
                minhashes.append(minhash)
            progress.update(os.path.getsize(minhashes_file))

    return minhashes

def main(working_directory, process_count, instance_count, instance):

    # Load All Pairs
    pairs_file = os.path.join(working_directory, "all_pairs.pkl")    
    if not os.path.exists(pairs_file):
        logger.info("Please generate pairs first with generate_all_pairs.py")
        sys.exit(0)

    logger.info(f"Loading pairs file {pairs_file}")
    pairs = pickle.load(open(pairs_file, "rb"))

    # Load All Minhashes
    logger.info(f"Loading minhashes {pairs_file}")
    minhashes = load_minhashes(working_directory)

    pair_count = len(minhashes)
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

    with tqdm.tqdm(total=pairs_per_instance, dynamic_ncols=True, unit="pairs") as progress:
        if os.path.exists(checkpoint_file):
            checkpoint_offset = pickle.load(open(checkpoint_file, "rb"))
            logger.info(f"Checkpoint found, starting from offset {checkpoint_offset:,}")            
        else:
            logger.info(f"No checkpoint found, starting from offset {offset_start:,}")
            checkpoint_offset = offset_start

        batch_size = 100000
        batch = []
        pool = TqdmMultiProcessPool(process_count)

        for offset, pair in enumerate(pairs):
            if offset < checkpoint_offset:
                progress.update()
                continue

            if not offset < next_offset:
                break

            batch.append(pair)

            if len(batch) == batch_size:
                process_batch(pool, batch, working_directory)
                batch = []

        if len(batch) != 0:
            process_batch(pool, batch, working_directory)

parser = argparse.ArgumentParser(description='Generating minhashes for cc')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("--instance_count", type=int, default=1)
parser.add_argument("--instance", type=int, default=0)

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count, args.instance_count, args.instance)