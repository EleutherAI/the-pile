import os
import argparse
import pickle

import tqdm
import nltk
from nltk.util import ngrams
from nltk.probability import FreqDist
from tqdm_multiprocess import TqdmMultiProcessPool

from the_pile.datasets import CommonCrawlDataset

import logging
from the_pile.logger import setup_logger_tqdm
logger = logging.getLogger(__name__)

# Multiprocessing
def extract_ngrams(data, num, tqdm_func, global_tqdm):
    return ngrams(nltk.word_tokenize(data), num)

def process_batch(pool, batch, frequencies, n_value):
    tasks = []
    for document in batch:
        task = (extract_ngrams, (document, n_value))
        tasks.append(task)

    on_done = lambda _ : None
    on_error = lambda _ : None
    document_ngrams = pool.map(None, tasks, on_error, on_done)

    for document_ngram in document_ngrams:
        for n_gram in document_ngram:
            frequencies[n_gram] += 1       

def main(working_directory, process_count, n_value):
    nltk.download('punkt')

    stats_pickle_file = os.path.join(working_directory, f"stats_n{n_value}.pkl")

    cc_dataset = CommonCrawlDataset()
    frequencies = FreqDist()

    batch_size = 1000
    batch = []
    pool = TqdmMultiProcessPool(process_count)

    with tqdm.tqdm(total=cc_dataset.num_docs(), dynamic_ncols=True, unit="docs") as progress:
        for document, meta in cc_dataset.documents():

            batch.append(document)

            if len(batch) == batch_size:
                process_batch(pool, batch, frequencies, n_value)
                batch = []
                progress.update(batch_size)

        if len(batch) != 0:
            process_batch(pool, batch, frequencies, n_value)
            progress.update(len(batch))

    logger.info("Pickling frequency dist")
    pickle.dump(frequencies, open(stats_pickle_file, "wb"))

parser = argparse.ArgumentParser(description='n-gram statistics')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("-n", "--n_value", type=int, default=13)

if __name__ == '__main__':
    logfile_path = "generate_minhashes.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count, args.n_value)