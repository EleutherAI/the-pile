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

from .models import get_db_session, NGram

# Multiprocessing
def extract_ngrams(data, num, tqdm_func, global_tqdm):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]

def process_batch(pool, batch, n_value, db_session):
    tasks = []
    for document in batch:
        task = (extract_ngrams, (document, n_value))
        tasks.append(task)

    on_done = lambda _ : None
    on_error = lambda _ : None
    document_ngrams = pool.map(None, tasks, on_error, on_done)

    query = db_session.query(NGram) \
                      .filter(NGram.n_gram.in_(document_ngrams))


    existing_ngrams = set()
    for n_gram_row in query.all():        
        existing_ngrams.add(n_gram_row.n_gram)
        n_gram_row.count += 1

    for document_ngram in document_ngrams:
        if document_ngram not in existing_ngrams:
            new_ngram = NGram()
            new_ngram.n_gram = document_ngram
            new_ngram.count = 1
            db_session.add(new_ngram)

    db_session.commit()

def main(working_directory, process_count, n_value):
    nltk.download('punkt')

    cc_dataset = CommonCrawlDataset()
    db_session = get_db_session()

    batch_size = 1000
    batch = []
    pool = TqdmMultiProcessPool(process_count)

    with tqdm.tqdm(total=cc_dataset.num_docs(), dynamic_ncols=True, unit="docs") as progress:
        for document, meta in cc_dataset.documents():

            batch.append(document)

            if len(batch) == batch_size:
                process_batch(pool, batch, n_value, db_session)
                batch = []
                progress.update(batch_size)

        if len(batch) != 0:
            process_batch(pool, batch, n_value, db_session)
            progress.update(len(batch))

parser = argparse.ArgumentParser(description='n-gram statistics')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)
parser.add_argument("-n", "--n_value", type=int, default=13)

if __name__ == '__main__':
    logfile_path = "generate_minhashes.log"
    setup_logger_tqdm(logfile_path)

    args = parser.parse_args()
    main(args.working_directory, args.process_count, args.n_value)