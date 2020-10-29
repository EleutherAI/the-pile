import argparse
import os
import pickle
import json
import sys
import asyncio

import nltk
from nltk.util import ngrams
from datasketch import MinHash, LeanMinHash
from datasketch.experimental.aio.lsh import AsyncMinHashLSH
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

def generate_minhash(document):

    n_grams = extract_ngrams(document, 5)
    five_gram_set = set(n_grams)
    minhash = MinHash(num_perm=10)
    for five_gram in five_gram_set:
        minhash.update(five_gram.encode('utf8'))

    return LeanMinHash(minhash)

_storage = {'type': 'aiomongo', 'mongo': {'host': 'localhost', 'port': 27017, 'db': 'lsh_test'}}

async def minhash_lsh_dedupe_mongo(minhash, priority, offset, sha256sum):
    lsh = await AsyncMinHashLSH(storage_config=_storage, threshold=0.5, num_perm=10)
    results = await lsh.query(minhash)

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
            await lsh.remove(json_results)
            await lsh.insert(json.dumps((priority, offset, sha256sum)), minhash)
            return json_results

    # Duplicate not found, insert self
    await lsh.insert(json.dumps((priority, offset, sha256sum)), minhash)    
    await lsh.close()

def process_document(priority, offset, document, sha256sum, tqdm_func, global_tqdm):
    minhash = generate_minhash(document)
    duplicate = asyncio.run(minhash_lsh_dedupe_mongo(minhash, priority, offset, sha256sum))
    global_tqdm.update(len(document))
    return duplicate

def docs_for_dedupe():
    # format: ((priority, offset, sha256sum), document)
    dset = CommonCrawlDataset()
    i = -1
    for doc in dset.documents():
        i += 1
        yield (100, i, sha256str(doc.encode('utf-8'))), doc

def main(working_directory, process_count):

    # # workaround for datasketch MinHashLSH bug
    # first_run_file = os.path.join(args.working_directory, ".first_run")
    # if not os.path.exists(first_run_file):
    #     get_minhash_lsh_cassandra()
    #     with open(first_run_file, "w") as fh:
    #         fh.write("hello")
    #     logger.info("Cassandra connection created on first run to bypass a bug. Please run the script again.")
    #     sys.exit(0) 

    nltk.download('punkt')

    total_file_size = CommonCrawlDataset().size()
    checkpoint_file = os.path.join(working_directory, "checkpoint.pkl")
    duplicates_file = os.path.join(working_directory, "duplicates.txt")

    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit_scale=1) as progress, \
         open(duplicates_file, "a") as fh:

        if os.path.exists(checkpoint_file):
            checkpoint_offset = pickle.load(open(checkpoint_file, "rb")) + 1
            logger.info(f"Checkpoint found, starting from offset {checkpoint_offset}")
        else:
            checkpoint_offset = 0
            logger.info("No checkpoint found, starting from offset 0")            

        for doc in docs_for_dedupe():
            ((priority, offset, sha256sum), document) = doc

            if offset < checkpoint_offset:
                progress.update(len(document))
                continue

            result = process_document(priority, offset, document, sha256sum)
            if result:
                priority, offset, sha256sum = result
                fh.write(f"{priority} {offset} {sha256sum}\n")

parser = argparse.ArgumentParser(description='Dedupe from provided indexes.')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count)