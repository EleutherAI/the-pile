import lm_dataformat as lmd
import json
from pytablewriter import MarkdownTableWriter
from tqdm import tqdm 
from utils import humanbytes
import random

from datasets import *


datasets = [
    (BibliotikDataset()    , 1. ),
    (PubMedCentralDataset(), 1. ),
    (ArXivDataset()        , 1. ),
    (FreeLawDataset()      , 1. ),
    (OpenWebTextDataset()  , 1. ),
    (PubMedDataset()       , 1. ),
    (WikipediaDataset()    , 1. ),
    (OpensubtitlesDataset(), 1. ),
    (GutenbergDataset()    , 1. ),
    (LiteroticaDataset()   , 1. ),
    (DMMathDataset()       , 1. ),
    (BookCorpusDataset()   , 1. ),
    (UbuntuIRCDataset()    , 1. ),
    (CORD19Dataset()       , 1. ),
    (ExPorterDataset()     , 1. ),
    (EnronEmailsDataset()  , 1. ),
    (StackExchangeDataset(), 1. ),
]

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
        total_weight = sum([x[1] * x[0].size() for x in self.datasets])
        for dataset, weight in self.datasets:
            size = dataset.size()
            relative_weight = size * weight / total_weight
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
    print(mk_table(datasets))

    pile = ThePile(datasets, int(1.2e12))
    for x in pile.documents():
        pass