import lm_dataformat as lmd
import json
from pytablewriter import MarkdownTableWriter
from tqdm import tqdm 
from utils import humanbytes

from datasets import *


datasets = [
    (OpenWebTextDataset()  , 1. ),
    (WikipediaDataset()    , 1. ),
    (OpensubtitlesDataset(), 1. ),
    (GutenbergDataset()    , 1. ),
    (BookCorpusDataset()   , 1. ),
]


if __name__ == '__main__':
    values = []

    total_weight = sum([x[1] * x[0].size() for x in datasets])

    train_chars = 1.2e12

    for dataset, weight in datasets:
        size = dataset.size()
        relative_weight = size * weight / total_weight
        print(dataset.name(), weight * size / total_weight)
        values.append([dataset.name(), size, '{:.1%}'.format(relative_weight), train_chars / size * relative_weight])
    
    print(values)
    
    values.sort(key=lambda x: -x[1])
    values.append(['**Total**', sum([x[1] for x in values]), "", ""])
    values = [[x[0], humanbytes(x[1]), x[2], x[3]] for x in values]

    writer = MarkdownTableWriter()
    writer.table_name = "The Pile™ Components"
    writer.headers = ["Component", "Size", "Weight", "Epochs (@1T2B)"]
    writer.value_matrix = values
    print(writer.dumps())