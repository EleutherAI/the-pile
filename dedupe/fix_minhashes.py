import argparse
import os
import pickle
import signal
from signal import SIGINT, SIG_IGN
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

def load_minhashes(working_directory):
    document_count = CommonCrawlDataset().num_docs()

    # batch_size = 1000 # Used elsewhere - careful!
    # offset = 0
    # total_file_size = 0
    # while offset < document_count:
    #     minhashes_file = os.path.join(working_directory, f"minhashes_{offset}.pkl")
    #     offset += batch_size
    #     total_file_size += (os.path.getsize(minhashes_file))

    files = glob.glob(os.path.join(working_directory, "minhashes*"))

    total_file_size = 0
    for file in files:
        total_file_size += (os.path.getsize(file))

    count = 0
    minhashes = [None] * 10
    logger.info(f"minhash array length {len(minhashes):,}")
    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit="byte", unit_scale=1) as progress:
        for file in files:
            minhashes_temp = pickle.load(open(file, "rb"))
            for minhash in minhashes_temp:
                (priority, offset, sha256sum, minhash) = minhash
                try:
                    if not minhashes[offset]:
                        count += 1
                except:
                    logger.info(f"fucked offset: {offset:,}")

            progress.update(os.path.getsize(file))

    difference = document_count - count
    logger.info(f"Expected document count: {document_count:,}")
    logger.info(f"Actual document count: {count:,}")
    logger.info(f"Difference {difference:,}")

    return minhashes    

def main(working_directory):
    minhashes = load_minhashes(working_directory)

parser = argparse.ArgumentParser(description='Fix minhashes')
parser.add_argument("-dir", "--working_directory", default="")

if __name__ == '__main__':
    logfile_path = "fix_minhashes.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory)