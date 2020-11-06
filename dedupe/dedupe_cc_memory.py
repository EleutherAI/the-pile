import argparse
import os
import pickle
import signal
from signal import SIGINT, SIG_IGN
import sys
import glob
import math
import json

import nltk
from nltk.util import ngrams
from datasketch import MinHash, LeanMinHash, MinHashLSH
import tqdm
from tqdm_multiprocess import TqdmMultiProcessPool

from the_pile.datasets import CommonCrawlDataset
from the_pile.utils import sha256str

from dedupe.archiver import Archive, Reader

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

# # Multiprocessing
# def compare_pair(m1, m2, tqdm_func, global_tqdm):
#     return m1.jaccard(m2) > 0.5

# def process_batch(pool, batch, offset_start, working_directory): 
#     checkpoint_file = os.path.join(working_directory, "dedupe_checkpoint.pkl")
#     checkpoint_temp_file = os.path.join(working_directory, "dedupe_checkpoint_temp.pkl")
#     checkpoint_old_file = os.path.join(working_directory, "dedupe_checkpoint_old.pkl")
#     transaction_lock = os.path.join(working_directory, ".transaction_lock_dedupe")

#     # Generate minhashes with pool
#     tasks = []
#     for (pair, m1, m2) in batch:
#         task = (compare_pair, (m1, m2))
#         tasks.append(task)

#     on_done = lambda _ : None
#     on_error = lambda _ : None
#     results = pool.map(None, tasks, on_error, on_done)

#     # Commence Transaction
#     previous_signal_int = signal.signal(SIGINT, SIG_IGN)
#     Path(transaction_lock).touch()

#     # Dump Duplicates
#     duplicates = []

#     for i, is_duplicate in enumerate(results):
#         if not is_duplicate:
#             continue

#         pair, _, _ = batch[i]
#         duplicates.append(pair)

#     duplicates_file = os.path.join(working_directory, f"duplicates_{offset_start}.pkl")
#     pickle.dump(duplicates, open(duplicates_file, "wb"))

#     # Dump Checkpoint
#     last_offset = offset_start + len(batch) - 1
#     pickle.dump(last_offset, open(checkpoint_temp_file, "wb"))

#     # Move stuff around safely in case of failure
#     if os.path.exists(checkpoint_file):
#         os.rename(checkpoint_file, checkpoint_old_file)
#     os.rename(checkpoint_temp_file, checkpoint_file)

#     # Transaction Finished
#     os.remove(transaction_lock)
#     signal.signal(SIGINT, previous_signal_int)    

def verify_fixed_minhashes(working_directory):
    document_count = CommonCrawlDataset().num_docs()

    fixed_directory = os.path.join(working_directory, "fixed_minhashes")

    batch_size = 1000
    files = []
    start_offset = 0
    while True:
        file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
        if not os.path.exists(file):
            break
        files.append(file)
        start_offset += batch_size

    total_file_size = 0
    for file in files:
        total_file_size += os.path.getsize(file)

    count = 0
    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
        for file in files:
            document_data = pickle.load(open(file, "rb"))
            count += len(document_data)

            progress.update(os.path.getsize(file))

    difference = document_count - count
    logger.info(f"Expected document count: {document_count:,}")
    logger.info(f"Loaded documents with minhashes count: {count:,}")
    logger.info(f"Difference {difference:,}")

def yield_minhashes(working_directory):
    fixed_directory = os.path.join(working_directory, "fixed_minhashes")

    batch_size = 1000
    files = []
    start_offset = 0
    while True:
        file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
        if not os.path.exists(file):
            break
        files.append(file)
        start_offset += batch_size

    total_file_size = 0
    for file in files:
        total_file_size += os.path.getsize(file)

    for file in files:
        document_data = pickle.load(open(file, "rb"))
        for document in document_data:
            yield document

def load_minhashes_old(working_directory):
    pass
    # total_file_size = 0
    # for file in files:
    #     total_file_size += (os.path.getsize(file))

    # count = 0
    # minhashes = [None] * document_count
    # logger.info(f"minhash array length {len(minhashes):,}")
    # with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
    #     for file in files:
    #         document_data = pickle.load(open(file, "rb"))
    #         for document in document_data:
    #             (priority, offset, sha256sum, minhash) = document
    #             if not minhashes[offset]:
    #                 count += 1

    #             minhashes[offset] = document

    #         progress.update(os.path.getsize(file))

    # difference = document_count - count
    # logger.info(f"Expected document count: {document_count:,}")
    # logger.info(f"Loaded documents with minhashes count: {count:,}")
    # logger.info(f"Difference {difference:,}")

    # return minhashes

# def get_pair_count(document_count, working_directory):
#     pair_count_file = os.path.join(working_directory, "pair_count.pkl")
#     if os.path.exists(pair_count_file):
#         return pickle.load(open(pair_count_file, "rb"))

#     logger.info(f"Counting all pairs...")    
#     pair_count = 0
#     for i in tqdm.tqdm(range(document_count)):
#         pair_count += document_count - (i + 1)

#     pickle.dump(pair_count, open(pair_count_file, "wb"))
#     return pair_count

# def get_pair_from_offset(document_count, offset):
#     count = 0
#     for i in range(document_count):
#         j_start = i + 1
#         j_size = document_count - (j_start)
#         if offset >= count + j_size:
#             count += j_size
#             continue

#         j = (offset - count) + j_start
#         return (i, j)

# def test_pair_math():
#     document_count = 5

#     offset = 0
#     for i in range(document_count):
#         for j in range(i+1, document_count):
#             logger.info(f"expected: {(i, j)}")
#             returned = get_pair_from_offset(document_count, offset)
#             logger.info(f"returned: {returned}")
#             assert(returned == (i, j))
#             offset += 1     

#     assert(get_pair_count(document_count, "") == offset)

# Remove dupes from dumbing
def fix_minhashes(working_directory):
    # Load All Minhashes
    logger.info(f"Loading minhashes...")
    minhashes = load_minhashes_old(working_directory)

    fixed_directory = os.path.join(working_directory, "fixed_minhashes")
    os.makedirs(fixed_directory, exist_ok=True)

    batch_size = 1000
    batch = []
    start_offset = 0
    for document in tqdm.tqdm(minhashes, dynamic_ncols=True, unit="docs"):
        # (priority, offset, sha256sum, minhash) = document
        batch.append(document)

        if len(batch) == batch_size:
            minhashes_file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
            pickle.dump(batch, open(minhashes_file, "wb"))
            start_offset += 1000
            batch = []

    if len(batch) != 0:
        minhashes_file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
        pickle.dump(batch, open(minhashes_file, "wb"))

def get_lsh(working_directory):    
    lsh_file_path = os.path.join(working_directory, "lsh.pkl")
    if os.path.exists(lsh_file_path):
        logger.info("Loading lsh from pickle...")
        lsh = pickle.load(open(lsh_file_path, "rb"))
        return lsh

    logger.info(f"Building LSH")
    lsh = MinHashLSH(threshold=0.5, num_perm=10)
    document_count = CommonCrawlDataset().num_docs()
    progress = tqdm.tqdm(total=document_count, dynamic_ncols=True, unit="docs")
    for (priority, offset, sha256sum, minhash) in yield_minhashes(working_directory):
        lsh.insert((priority, offset), minhash)
        progress.update()
    progress.close()

    logger.info("Dumping LSH")
    pickle.dump(lsh, open(lsh_file_path, "wb"))
    return lsh

def package_for_lm(working_directory):
    logger.info("Building file list")
    document_count = CommonCrawlDataset().num_docs()
    start_offset = 0
    files = []
    fixed_directory = os.path.join(working_directory, "fixed_minhashes")    
    while True:
        file = os.path.join(fixed_directory, f"duplicates_{start_offset}.pkl")
        if not os.path.exists(file):
            break

        files.append(file)
        start_offset += 1000

    logger.info(f"File count: {len(files):,}")

    duplicates_lm_file = os.path.join(working_directory, "duplicates.jsonl.zst")
    archiver = Archive(duplicates_lm_file)

    duplicate_count = 0
    for file in tqdm.tqdm(files, dynamic_ncols=True, unit="batches"):
        duplicates = pickle.load(open(file, "rb"))
        for duplicate in duplicates:
            duplicate_count += 1
            archiver.add_data("", meta=list(duplicate))

    archiver.commit()

    logger.info(f"Original Doucment Count: {document_count:,}")
    logger.info(f"Duplicate Count: {duplicate_count:,}")

    logger.info(f"example data:")
    reader = Reader()

    limit = 10
    count = 0
    for _, meta in reader.read_jsonl(duplicates_lm_file, get_meta=True):
        print(meta)

        if count == limit:
            break

        count += 1


def main(working_directory, process_count, instance_count, instance):  

    # fix_minhashes(working_directory)

    lsh = get_lsh(working_directory)

    logger.info("Building file list")
    document_count = CommonCrawlDataset().num_docs()
    start_offset = 0
    files = []
    fixed_directory = os.path.join(working_directory, "fixed_minhashes")    
    while True:
        minhashes_file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
        if not os.path.exists(minhashes_file):
            break

        files.append(minhashes_file)
        start_offset += 1000

    logger.info(f"Document count: {document_count:,}")
    logger.info(f"File count: {len(files):,}")

    start_offset = 0
    for file in tqdm.tqdm(files, dynamic_ncols=True, unit="batches"):
        minhashes = pickle.load(open(file, "rb"))

        duplicates = []
        for (priority, offset, sha256sum, minhash) in minhashes:
            results = lsh.query(minhash)
            for found_priority, found_offset in results:
                if found_offset != offset:
                    duplicates.append((priority, offset, sha256sum))
                    lsh.remove((priority, offset))
                    break

        duplicates_file = os.path.join(fixed_directory, f"duplicates_{start_offset}.pkl")
        pickle.dump(duplicates, open(duplicates_file, "wb"))
        start_offset += len(minhashes)

def verify_dedupe(working_directory):

    lsh = get_lsh(working_directory)

    logger.info("Building file list")
    document_count = CommonCrawlDataset().num_docs()
    start_offset = 0
    files = []
    fixed_directory = os.path.join(working_directory, "fixed_minhashes")    
    while True:
        minhashes_file = os.path.join(fixed_directory, f"minhashes_{start_offset}.pkl")
        if not os.path.exists(minhashes_file):
            break

        files.append(minhashes_file)
        start_offset += 1000

    logger.info(f"Document count: {document_count:,}")
    logger.info(f"File count: {len(files):,}")
    
    duplicates = []
    done = False
    for file in tqdm.tqdm(files, dynamic_ncols=True, unit="batches"):
        minhashes = pickle.load(open(file, "rb"))
        
        if done:
            break

        for (priority, offset, sha256sum, minhash) in minhashes:
            results = lsh.query(minhash)
            for found_priority, found_offset in results:
                if found_offset != offset:
                    duplicates.append((offset, found_offset))
                    lsh.remove((priority, offset))
                    break

            if len(duplicates) == 1000:
                done = True
                break

    duplicates_file = os.path.join(working_directory, f"verify_dedupe.pkl")
    pickle.dump(duplicates, open(duplicates_file, "wb"))

def docs_for_dedupe():
    # format: ((priority, offset, sha256sum), document)
    dset = CommonCrawlDataset()
    i = -1
    for doc in dset.documents():
        i += 1
        yield (100, i, sha256str(doc.encode('utf-8'))), doc

def output_verification(working_directory):

    duplicates_file = os.path.join(working_directory, f"verify_dedupe.pkl")
    duplicates = pickle.load(open(duplicates_file, "rb"))

    verify_cc_documents_file = os.path.join(working_directory, "verify_cc_documents.pkl")
    if os.path.exists(verify_cc_documents_file):
        cc_documents = pickle.load(open(verify_cc_documents_file, "rb"))
    else:
        remaining = 2 * len(duplicates)
        cc_documents = {}    
        for offset, found_offset in duplicates:
            cc_documents[offset] = None
            cc_documents[found_offset] = None

        document_count = CommonCrawlDataset().num_docs()
        with tqdm.tqdm(total=document_count, dynamic_ncols=True, unit="docs") as progress:
            for doc in docs_for_dedupe():
                ((priority, offset, sha256sum), document) = doc
                if offset in cc_documents:
                    cc_documents[offset] = document
                    remaining -= 1

                progress.update()

                if remaining == 0:
                    break

    for offset, found_offset in duplicates:        
        logger.info("DOCUMENT")
        logger.info("===========================")
        logger.info(cc_documents[offset])
        logger.info("===========================")
        logger.info("MATCHING DOCUMENT")
        logger.info(cc_documents[found_offset])
        logger.info("")
        logger.info("")        
        input("Press enter for next document")

import lm_dataformat as lmd

def read_cc():
    yield from lmd.Reader('components/commoncrawl/pile_cc_filtered.jsonl.zst.tar').stream_data(get_meta=True)

def cc_remove_duplicates(working_directory):

    duplicate_offsets = set()

    logger.info("Loading all duplicates")
    duplicates_lm_file = os.path.join(working_directory, "duplicates.jsonl.zst")    
    progress = tqdm.tqdm(total=os.path.getsize(duplicates_lm_file), dynamic_ncols=True, unit_scale=True, unit="byte")
    previous_file_position = 0
    reader = Reader()    
    for _, meta in reader.read_jsonl(duplicates_lm_file, get_meta=True):
        priority, offset, sha256sum = tuple(meta)
        duplicate_offsets.add(offset)

        current_file_position = reader.fh.tell()
        progress.update(current_file_position - previous_file_position)
        previous_file_position = current_file_position

    deduped_cc_path = os.path.join(working_directory, "pile_cc_filtered_deduped.jsonl.zst.tar")
    archiver = Archive(deduped_cc_path)

    logger.info("Deduping CC")
    offset = 0
    count = 0
    document_count = CommonCrawlDataset().num_docs()
    progress = tqdm.tqdm(total=document_count, dynamic_ncols=True, unit="docs")
    for doc, meta in read_cc():
        if offset not in duplicate_offsets:
            archiver.add_data(doc, meta=meta)
            count += 1

        offset += 1
        progress.update()

    archiver.commit()

    duplicate_count = offset - count
    
    logger.info(f"Expected Document Count: {offset:,}")
    logger.info(f"Original Document Count: {offset:,}")
    logger.info(f"Expected Duplicate Count: {len(duplicate_offsets):,}")    
    logger.info(f"Duplicate Count: {duplicate_count:,}")
    logger.info(f"Remaining documents: {count:,}")


    # # Batching
    # document_count = CommonCrawlDataset().num_docs()
    # pair_count = get_pair_count(document_count, working_directory)
    # pairs_per_instance = int(pair_count / instance_count)
    # offset_start = pairs_per_instance * instance
    # next_offset = offset_start + pairs_per_instance
    # logger.info(f"Total pairs: {pair_count:,}")
    # logger.info(f"Number of instances: {instance_count}")
    # logger.info(f"Pairs per instance: {pairs_per_instance:,}")
    # logger.info(f"Currently running instance: {instance}")
    # logger.info(f"Offset Start: {offset_start:,}")
    # logger.info(f"Next Offset Start: {next_offset:,}")

    # checkpoint_file = os.path.join(working_directory, "dedupe_checkpoint.pkl")
    # checkpoint_temp_file = os.path.join(working_directory, "dedupe_checkpoint_temp.pkl")
    # checkpoint_old_file = os.path.join(working_directory, "dedupe_checkpoint_old.pkl")
    # transaction_lock = os.path.join(working_directory, ".transaction_lock_dedupe")

    # if os.path.exists(transaction_lock):
    #     logger.info("Program crashed during transaction, fixing files...")
    #     # Just re-do from last safe checkpoint (overwrite minhashes)
    #     if os.path.exists(checkpoint_temp_file):
    #         if os.path.exists(checkpoint_old_file):
    #             os.rename(checkpoint_old_file, checkpoint_file)
    #         os.remove(checkpoint_temp_file)
    #     else:
    #         pass

    #     os.remove(transaction_lock)        

    # if os.path.exists(checkpoint_file):
    #     checkpoint_offset = pickle.load(open(checkpoint_file, "rb")) + 1
    #     logger.info(f"Checkpoint found, starting from offset {checkpoint_offset}")    
    #     (i_start, j_start) = get_pair_from_offset(document_count, checkpoint_offset)
                
    # else:
    #     logger.info(f"No checkpoint found, starting from offset {offset_start}")   
    #     checkpoint_offset = offset_start
    #     (i_start, j_start) = get_pair_from_offset(document_count, offset_start)


    # batch_size = 100000 # Pair batch size, not minhash batch size
    # batch = []
    # pool = TqdmMultiProcessPool(process_count)

    # # Can't use total pair count as tqdm blows up    
    # batch_count = int(math.ceil(pairs_per_instance / batch_size))
    # logger.info(f"Total 100k batches in set: {batch_count}")

    # # Should be whole always as batch_size doesn't change?
    # batches_completed = int((checkpoint_offset - offset_start) / batch_size)
    # logger.info(f"Batches already completed: {batches_completed}")

    # with tqdm.tqdm(total=batch_count, dynamic_ncols=True, unit="100k/batch") as progress:
    #     progress.update(batches_completed)
    #     offset = checkpoint_offset
    #     for i in range(i_start, document_count):
    #         if i != i_start:
    #             j_start = i + 1

    #         for j in range(j_start, document_count):                
    #             if not offset < next_offset:
    #                 break


    #             # (priority, offset, sha256sum, minhash) = document
    #             batch.append(((i,j), minhashes[i][3], minhashes[j][3]))

    #             if len(batch) == batch_size:
    #                 process_batch(pool, batch, offset, working_directory)
    #                 batch = []
    #                 progress.update()

    #             offset += 1

    #     if len(batch) != 0:
    #         process_batch(pool, batch, offset, working_directory)
    #         progress.update()

parser = argparse.ArgumentParser(description='Memory dedupe using minhash lsh.')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("--instance_count", type=int, default=1)
parser.add_argument("--instance", type=int, default=0)

if __name__ == '__main__':
    logfile_path = "dedupe_cc_memory.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    # main(args.working_directory, args.process_count, args.instance_count, args.instance)
    # verify_dedupe(args.working_directory)
    cc_remove_duplicates(args.working_directory)

# if __name__ == '__main__':
#     setup_logger_tqdm()
#     test_pair_math()