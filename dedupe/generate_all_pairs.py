import argparse
import os
import pickle

from the_pile.datasets import CommonCrawlDataset

import logging
from the_pile.logger import setup_logger_tqdm
logger = logging.getLogger(__name__)

def main(working_directory):
    document_count = CommonCrawlDataset().num_docs()
    logger.info(f"Document count: {document_count:,}")

    pairs = []
    for i in range(document_count):
        for j in range(i+1, document_count):
            pairs.append((i,j))

    logger.info(f"Generated pairs: {len(pairs):,}")

    pairs_file = os.path.join(working_directory, "all_pairs.pkl")
    logger.info(f"Dumping pairs to file {pairs_file}")
    pickle.dump(pairs, open(pairs_file, "wb"))

parser = argparse.ArgumentParser(description='Generating all pairs for cc')
parser.add_argument("-dir", "--working_directory", default="")

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory)