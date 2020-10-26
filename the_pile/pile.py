import random
import fasttext

from pytablewriter import MarkdownTableWriter
from tqdm import tqdm

from the_pile.utils import humanbytes
from the_pile.datasets import *


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
        (GithubDataset()       , 1.  ),
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

train_chars = 1200 * 1024 * 1024 * 1024

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

def mk_table(datasets):
    values = []

    total_weight = sum([x[1] * x[0].size() for x in datasets])

    for dataset, weight in datasets:
        size = dataset.size()
        relative_weight = size * weight / total_weight
        values.append([dataset.name(), size, '{:.2%}'.format(relative_weight), train_chars / size * relative_weight, size * weight, humanbytes(size / dataset.num_docs())])
    
    values.sort(key=lambda x: -x[4])
    values.append(['**Total**', sum([x[1] for x in values]), "", "", sum([x[4] for x in values]), humanbytes(sum([x[1] for x in values]) / sum(x[0].num_docs() for x in datasets))])
    values = [[x[0], humanbytes(x[1]), x[2], x[3], humanbytes(x[4]), x[5]] for x in values]

    writer = MarkdownTableWriter()
    writer.table_name = "The Pile™"
    writer.headers = ["Component", "Raw Size", "Weight", "Epochs", "Effective Size", "Mean Document Size"]
    writer.value_matrix = values
    return writer.dumps()


def dataset_tqdm(dset):
    pbar = tqdm(total=dset.size(), unit='B', unit_scale=True, unit_divisor=1024)
    for doc in dset.documents():
        pbar.update(utf8len(doc))
        yield doc 


class Profiler:
    def __init__(self, profile):
        self.i = 0
        self.profile = profile
        self.time_per_dataset = collections.defaultdict(lambda: [0, 0])

    def measured_next(self, name, iter):
        if not self.profile:
            # no-op
            return next(iter)
        else:
            self.i += 1
            start = time.time()
            doc = next(iter)
            elapsed = time.time() - start

            self.time_per_dataset[name][0] += elapsed
            self.time_per_dataset[name][1] += 1

            if self.i % 100000 == 0:
                times = [(dsname, total, ct) for dsname, (total, ct) in self.time_per_dataset.items()]
                times.sort(key=lambda x: x[1])
                for name, total, ct in times:
                    print(name.ljust(22), '{:.8f}'.format(total / ct), str(ct).rjust(8), '{:.4f}'.format(total))
            
            return doc


class ThePile(Dataset):
    def __init__(self, datasets, dataset_bytes, profile=False):
        self.datasets = datasets
        self.dataset_bytes = dataset_bytes
        self.profile = profile
    
    def name(self):
        return "The Pile"

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


        profiler = Profiler(profile=self.profile)
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


    def clean(self):
        for dataset, _ in self.datasets: dataset.clean()
    
    def size(self):
        return self.dataset_bytes


def preprocess_for_fasttext(x):
    return x.replace('\n', ' ').replace('\r', ' ')[:4000][-1500:]


import collections
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--download', action='store_true', help='force download all')
parser.add_argument('--make_fasttext', action='store_true', help='make data for fasttext')
parser.add_argument('--make_fasttext_wt_only', action='store_true', help='make data for fasttext using only OpenWebText2Dataset')
parser.add_argument('--make_analysis', action='store_true', help='make analysis data')
parser.add_argument('--profile', action='store_true', help='turn on profiler')

args = parser.parse_args()

def make_fasttext(pile, keep_frac):
    with open('fasttext_pile.txt', 'w') as fh, open('pile_sample.txt', 'w') as fh2:
        for x in pile:
            if random.random() < keep_frac:
                p = preprocess_for_fasttext(x)
                if len(p) > 100:
                    fh.write('__label__pile ' + p + '\n')
            if random.random() < 0.001:
                fh2.write(x + '<|endoftext|>\n')

def lang_stats(pile):
    langdet = fasttext.load_model("lid.176.bin") 
    n = 0
    langs = collections.defaultdict(int)
    for x in pile:
        details = langdet.predict(x.replace('\n', ' '), k=5)
        langs[details[0][0].replace('__label__', '')] += 1
        n += 1
        print('\n'.join([k + ',' + str(v / n).ljust(9) for k,v in sorted(list(langs.items()), key=lambda x: -x[1])]))

if __name__ == '__main__':
    random.seed(42)
    print(mk_table(datasets))

    if args.using == 'pile' or args.using == 'pile_no_cc':
        pile = ThePile(datasets, train_chars, profile=args.profile)
    elif args.using == 'cc':
        pile = dataset_tqdm(CommonCrawlDataset())
    elif args.using == 'owt2':
        pile = dataset_tqdm(OpenWebText2Dataset())
    else:
        print('Unknown dataset!')

    if args.download:
        for dset, _ in datasets:
            dset._download()
    if args.make_fasttext:
        make_fasttext(pile.documents(), 0.1)
    elif args.make_fasttext_wt_only:
        make_fasttext(dataset_tqdm(OpenWebText2Dataset()), 1)

