import lm_dataformat as lmd
import json
from pytablewriter import MarkdownTableWriter
from tqdm import tqdm, trange
from utils import humanbytes
import random

from datasets import *


datasets = [
    (
    [
        # Academic
        (PubMedCentralDataset(), 1.5 ),
        (ArXivDataset()        , 2.  ),
        (FreeLawDataset()      , 1.5 ),
        (USPTODataset()        , 2.  ),
        (PubMedDataset()       , 2.  ),
        (PhilPapersDataset()   , 3.  ),
        (ExPorterDataset()     , 3.  ),
    ], 0.45
    ),

    (
    [
        # General internet
        (OpenWebText2Dataset() , 2.  ),
        (StackExchangeDataset(), 2.  ),
        (WikipediaDataset()    , 3.  ),
    ], 0.20
    ),

    (
    [
        # Prose
        (BibliotikDataset()    , 1.  ),
        (GutenbergDataset()    , 2.  ),
        (LiteroticaDataset()   , 1.  ),
        (BookCorpusDataset()   , 1.5 ),
    ], 0.18
    ),

    (
    [
        (GithubDataset()       , 0.15),
    ], 0.10
    ),

    (
    [
        # Dialogue
        (UbuntuIRCDataset()    , 3.  ),
        (HackerNewsDataset()   , 3.  ),
        (EuroParlDataset()     , 3.  ),
        (YTSubtitlesDataset()  , 3.  ),
        (OpensubtitlesDataset(), 2.  ),
    ], 0.05
    ),

    (
    [
        # Misc
        (DMMathDataset()       , 2.  ),
        (EnronEmailsDataset()  , 3.  ),
    ], 0.02
    ),
]

datasets_new = []
target_size = 800 * 1024 * 1024 * 1024
for dsets, tgt_frac in datasets:
    dsets_size_wt = sum([x.size()*w for x, w in dsets])
    dsets_twt     = sum([w          for _, w in dsets])
    tgt_size = tgt_frac * target_size

    for dset, wt in dsets:
        frac_of_section = dset.size() * wt / dsets_size_wt
        datasets_new.append((dset, frac_of_section * tgt_size / dset.size()))

datasets = datasets_new


def take(n, iter):
    ret = []
    for i in range(n):
        try:
            ret.append(next(iter))
        except StopIteration:
            break
    return ret

def get_samples():
    for dset, _ in datasets:
        print('\\subsection{' + dset.name() + '}')
        print()
        docs = take(1000, dset.documents())
        random.shuffle(docs)

        limit = 8192
        res = ''
        for doc in docs:
            if len(res) > limit:
                break
            res += doc + '<|endoftext|>'
        
        if len(res) > limit:
            i = random.randrange(0, len(res) - limit)
            res = res[i:i+limit]
        print('\\begin{verbatim}\n' + res + '\n\\end{verbatim}')

def mk_table(datasets):
    values = []

    total_weight = sum([x[1] * x[0].size() for x in datasets])

    train_chars = 1.2e12

    for dataset, weight in datasets:
        size = dataset.size()
        relative_weight = size * weight / total_weight
        values.append([dataset.name(), size, '{:.2%}'.format(relative_weight), train_chars / size * relative_weight, humanbytes(size / dataset.num_docs())])
    
    values.sort(key=lambda x: -x[1])
    values.append(['**Total**', sum([x[1] for x in values]), "", "", humanbytes(sum([x[1] for x in values]) / sum(x[0].num_docs() for x in datasets))])
    values = [[x[0], humanbytes(x[1]), x[2], x[3], x[4]] for x in values]

    writer = MarkdownTableWriter()
    writer.table_name = "The Pile™"
    writer.headers = ["Component", "Size", "Weight", "Epochs", "Mean Document Size"]
    writer.value_matrix = values
    return writer.dumps()


class ThePile:
    def __init__(self, datasets, dataset_bytes):
        self.datasets = datasets
        self.dataset_bytes = dataset_bytes
    
    @abc.abstractmethod
    def name(self):
        return "The Pile"

    @abc.abstractmethod
    def documents(self):
        datasets = []
        weights = []

        # calculate relative_weight for each
        total_weight = sum([x[1] * x[0].num_docs() for x in self.datasets])
        for dataset, weight in self.datasets:
            size = dataset.size()
            relative_weight = weight * dataset.num_docs() / total_weight
            datasets.append(cycle_documents(dataset))
            weights.append(relative_weight)

        random.seed(42)
        
        # yield from dataset until right number of bytes
        total_bytes = 0
        pbar = tqdm(total=self.dataset_bytes, unit='B', unit_scale=True, unit_divisor=1024)
        while True:
            chunk = random.choices(population=datasets, weights=weights, k=1000)
            for dset in chunk:
                doc = next(dset)

                size = utf8len(doc)
                total_bytes += size
                pbar.update(size)
                yield doc

                if total_bytes > self.dataset_bytes:
                    return


    @abc.abstractmethod
    def clean(self):
        for dataset, _ in self.datasets: dataset.clean()
    
    def size(self):
        return sum(map(lambda x: x[0].size(), tqdm(self.datasets())))

if __name__ == '__main__':
    random.seed(42)
    print(mk_table(datasets))

    pile = ThePile(datasets, int(1.2e12))
    get_samples()
    for x in pile.documents():
        pass