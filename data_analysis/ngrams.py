import os
import argparse
import pickle

import tqdm
import nltk
from nltk.util import ngrams
from nltk.probability import FreqDist

from the_pile.datasets import CommonCrawlDataset

import logging
from the_pile.logger import setup_logger_tqdm
logger = logging.getLogger(__name__)

def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]

def main(working_directory, process_count, n_value):
    nltk.download('punkt')

    stats_pickle_file = os.path.join(working_directory, f"stats_n{n_value}.pkl")

    cc_dataset = CommonCrawlDataset()
    document_count = cc_dataset.num_docs()

    frequencies = FreqDist()

    with tqdm.tqdm(total=document_count, dynamic_ncols=True, unit="docs") as progress:
        for document, meta in cc_dataset.documents():
            n_grams = ngrams(nltk.word_tokenize(document), n_value)
            for n_gram in n_grams:
                frequencies[n_gram] += 1
            progress.update()

    logger.info("Pickling frequency dist")
    pickle.dump(frequencies, open(stats_pickle_file, "wb"))

parser = argparse.ArgumentParser(description='n-gram statistics')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("-n", "--n_value", type=int, default=4)

if __name__ == '__main__':
    logfile_path = "generate_minhashes.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count, args.n_value)