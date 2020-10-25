import argparse

import nltk
from nltk.util import ngrams
from datasketch import MinHash, LeanMinHash
import tqdm
from tqdm_multiprocess import TqdmMultiProcessPool

from the_pile.datasets import CommonCrawlDataset
from the_pile.pile import docs_for_dedupe

import logging
from utils.logger import setup_logger_tqdm
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

# Multiprocessed
def process_document(priority, offset, document, sha256sum, tqdm_func, global_tqdm):
    minhash = generate_minhash(document)

    global_tqdm.update(len(document))

def main(working_directory, process_count):

    batch_size = 100

    total_file_size = CommonCrawlDataset().size()

    with tqdm.tqdm(total=total_file_size, dynamic_ncols=True, unit_scale=1) as progress:
        batch = []

        for doc in docs_for_dedupe:
            batch.append(doc)

            if len(batch) == batch_size:
                pool = TqdmMultiProcessPool()
                tasks = []
                for ((priority, offset, sha256sum), document) in batch:
                    task = (process_document, (priority, offset, document, sha256sum))
                    tasks.append(task)

                on_done = lambda _ : None
                on_error = on_done
                result = pool.map(process_count, progress, tasks, on_error, on_done)
                print(result)

                batch = []

parser = argparse.ArgumentParser(description='Dedupe from provided indexes.')
parser.add_argument("-dir", "--working_directory", default="")
parser.add_argument("-procs", "--process_count", type=int, default=4)

if __name__ == '__main__':
    logfile_path = "dedupe_cc.log"
    setup_logger_tqdm(logfile_path)

    nltk.download('punkt')

    args = parser.parse_args()
    main(args.working_directory, args.process_count)