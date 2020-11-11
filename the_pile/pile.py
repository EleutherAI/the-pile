import time
import random
import fasttext

from pytablewriter import MarkdownTableWriter
from tqdm import tqdm

from the_pile.utils import humanbytes, parse_size
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

datasets_new = []
target_size = 950 * 1024 * 1024 * 1024
train_chars = 1200 * 1024 * 1024 * 1024
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

def mk_table(datasets, train_chars, print_latex=False):
    values = []

    total_weight = sum([x[1] * x[0].size() for x in datasets])

    for dataset, weight in datasets:
        size = dataset.size()
        relative_weight = size * weight / total_weight
        values.append([dataset.name(), size, '{:.2%}'.format(relative_weight), '{:.4f}'.format(train_chars / size * relative_weight), size * weight, humanbytes(size / dataset.num_docs(), 'KiB')])
    
    values.sort(key=lambda x: -x[4])
    values.append(['**Total**', "", "", "", sum([x[4] for x in values]), humanbytes(sum([x[1] for x in values]) / sum(x[0].num_docs() for x in datasets), 'KiB')])
    values = [[x[0], humanbytes(x[1], 'GiB') if x[1] else "", x[2], x[3], humanbytes(x[4], 'GiB'), x[5]] for x in values]

    writer = MarkdownTableWriter()
    writer.table_name = "The Pile™"
    writer.headers = ["Component", "Raw Size", "Weight", "Epochs", "Effective Size", "Mean Document Size"]
    writer.value_matrix = values

    if print_latex:
        rows = []
        for row in values[:-1]:
            rows.append("        " + " & ".join(map(lambda x: str(x).replace('%', r'\%'), row)) + r" \\")
        totalrow = " & ".join(map(lambda x: r'\textbf{%s}' % str(x).replace('%', r'\%') if x else "", values[-1][1:])) + r" \\"
        latex = r"""
\begin{table*}[t!]
    \centering
    \begin{tabular}{l r r r r r}
    \toprule
        \textbf{Component} & \textbf{Raw Size} & \textbf{Weight} & \textbf{Copies} & \textbf{Effective Size} & \textbf{Mean Document Size} \\
        \midrule
""" + "\n".join(rows) + r"""
        \midrule
        \textbf{The Pile} & """ + totalrow + r"""
        \bottomrule
    \end{tabular}
\caption{Overview of datasets in \textit{The Pile} before deduplication. The Pile is distributed with a predefined up/down-sampling of the different constituent datasets.}
\label{table:pile_overview}
\end{table*}
        """
        print(latex)
    return writer.dumps()


def dataset_tqdm(dset):
    if isinstance(dset, PileReplication):
        return dset.documents()
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


class PileReplication(Dataset):
    def __init__(self, datasets, dataset_bytes, profile=False):
        self.datasets = datasets
        self.dataset_bytes = dataset_bytes
        self.profile = profile
        self.rnd = random.Random(42)
    
    def name(self):
        return "Custom Pile"

    def documents(self):
        datasets = []
        weights = []

        # calculate relative_weight for each
        total_weight = sum([x[1] * x[0].num_docs() for x in self.datasets])
        for dataset, weight in self.datasets:
            size = dataset.size()
            relative_weight = weight * dataset.num_docs() / total_weight
            datasets.append((dataset.name(), cycle_documents(dataset)))
            weights.append(relative_weight)
        
        # yield from dataset until right number of bytes
        total_bytes = 0
        pbar = tqdm(total=self.dataset_bytes, unit='B', unit_scale=True, unit_divisor=1024)


        profiler = Profiler(profile=self.profile)
        while True:
            chunk = self.rnd.choices(population=datasets, weights=weights, k=1000)
            for name, dset in chunk:
                doc, meta = profiler.measured_next(name, dset)

                size = utf8len(doc)
                total_bytes += size
                pbar.update(size)

                meta['pile_set_name'] = name

                yield doc, meta

                if total_bytes > self.dataset_bytes:
                    return

    def clean(self):
        for dataset, _ in self.datasets: dataset.clean()
    
    def size(self):
        return self.dataset_bytes


class ThePile(Dataset):
    def name(self):
        return "The Pile"

    def _download(self):
        # TODO: host final pile
        pass

    def documents(self):
        self._download()

        return lmd.Reader('pile_output').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('pile_output')
    
    def size(self):
        return 1200 * 1024 * 1024 * 1024

class LimitedDataset(Dataset):
    def __init__(self, dataset, limit_size):
        self.dataset = dataset
        self.limit_size = limit_size
        self.rnd = random.Random(42)
    
    def name(self):
        return self.dataset.name() + " (truncated)"

    def documents(self):
        numer = self.limit_size
        denom = self.dataset.size()
        for doc, meta in dataset_tqdm(self.dataset):
            docsize = utf8len(doc)
            if self.rnd.random() < numer / denom:
                yield doc, meta
                numer -= docsize
            denom -= docsize

            if numer <= 0 or denom <= 0:
                break
    
    def clean(self):
        self.dataset.clean()
    
    def size(self):
        return self.limit_size


def preprocess_for_fasttext(x):
    return x.replace('\n', ' ').replace('\r', ' ')[:4000][-1500:]


import collections
import argparse
import json

def make_fasttext(pile, keep_frac):
    with open('fasttext_pile.txt', 'w') as fh, open('pile_sample.txt', 'w') as fh2:
        for x, _ in pile:
            if random.random() < keep_frac:
                p = preprocess_for_fasttext(x)
                if len(p) > 100:
                    fh.write('__label__pile ' + p + '\n')
            if random.random() < 0.001:
                fh2.write(x + '<|endoftext|>\n')

def lang_stats(pile):
    download_file('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'lid.176.bin', '7e69ec5451bc261cc7844e49e4792a85d7f09c06789ec800fc4a44aec362764e')
    
    langdet = fasttext.load_model("lid.176.bin") 
    langs = collections.defaultdict(lambda: collections.defaultdict(int))
    for i, (data, meta) in enumerate(pile.documents()):
        details = langdet.predict(data.replace('\n', ' ')[:3000], k=1)

        langs[meta['pile_set_name']][details[0][0].replace('__label__', '')] += 1

        if (i+1) % 100000 == 0:
            for name, x in langs.items():
                print('========= {} =========='.format(name))
                print('\n'.join([k + ',' + str(v / sum(x.values())).ljust(9) for k,v in sorted(list(x.items()), key=lambda x: -x[1])]))

            ob = {
                'langs': langs
            }
            with open('language_stats.json', 'w') as fout:
                fout.write(json.dumps(ob))


def sample_from_sets(datasets, n_docs):
    random.seed(42)
    for dset, _ in datasets:
        print(dset.name())
        fname = 'dataset_samples/{}.json'.format(dset.name().replace(' ', '_'))
        if os.path.exists(fname): continue

        n = dset.num_docs()

        # hotfix: github is the only dataset in v1 that's run for less than one epoch, so we only look at the part of it that actually ended up in v1.
        if dset.name() == 'Github': n = int(n * 0.19)

        indices = set(random.sample(range(n), n_docs))
        pbar = tqdm(total=n_docs)

        docs = []
        for i, (doc, meta) in enumerate(dset.documents()):
            if i > max(indices): break
            if i in indices:
                docs.append((doc, meta))
                pbar.update(1)
        
        try:
            os.mkdir('dataset_samples')
        except:
            pass

        with open(fname, 'w') as fh:
            json.dump(docs, fh)

        pbar.close()


def docs_for_dedupe():
    # format: ((priority, offset, sha256sum), document)
    dset = CommonCrawlDataset()
    for i, (doc, _) in dset.documents():
        yield (100, i, sha256str(doc)), doc


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--force_download', action='store_true', help='force download all')
    parser.add_argument('--limit', type=str, help='limit output size - this option causes read_amount tokens to be generated and then limit tokens to be sampled')
    parser.add_argument('--using', type=str, default='pile', help='the dataset to use')
    parser.add_argument('--chunk', type=str, help='output chunk size (for make_lmd)')
    parser.add_argument('--interleave_output', type=int, help='output interleaved chunks (for make_lmd)')
    parser.add_argument('--make_dummy', action='store_true', help='dummy consumer')
    parser.add_argument('--make_lmd', action='store_true', help='generate lm_dataformat')
    parser.add_argument('--make_fasttext', action='store_true', help='make data for fasttext')
    parser.add_argument('--make_lang_analysis', action='store_true', help='make language analysis data')
    parser.add_argument('--make_dataset_samples', type=int, help='make dataset sample data')
    parser.add_argument('--profile', action='store_true', help='turn on profiler')
    parser.add_argument('--read_amount', type=str, default='1200G', help='the size of the data read from the set')

    args = parser.parse_args()
    random.seed(42)

    if args.using != 'pile_reprod_no_cc':
        # add CC
        datasets.append((CommonCrawlDataset(), 1.))

    print(mk_table(datasets, parse_size(args.read_amount)))

    if args.using == 'pile_reprod' or args.using == 'pile_reprod_no_cc':
        pile = PileReplication(datasets, parse_size(args.read_amount), profile=args.profile)
    elif args.using == 'cc':
        pile = CommonCrawlDataset()
    elif args.using == 'pile':
        pile = ThePile()
    elif args.using == 'owt2':
        pile = OpenWebText2Dataset()
    elif args.using == 'bibliotik':
        pile = BibliotikDataset()
    else:
        print('We don\'t have a shortcut for that yet!')

    if args.force_download:
        for dset, _ in datasets:
            dset._download()
    
    if args.limit:
        size_limit = parse_size(args.limit)
        pile = LimitedDataset(pile, size_limit)

    if args.make_lmd:
        assert not (args.interleave_output and args.chunk) # can't chunk and interleave

        if args.interleave_output:
            ars = [lmd.Archive('pile_pass1/chunk{}'.format(i)) for i in range(args.interleave_output)]
        else:
            ar = lmd.Archive('pile_output')

        if args.chunk:
            chunk_size = parse_size(args.chunk)

        cursize = 0
        for doc, meta in pile.documents():
            if args.interleave_output:
                ar = random.choice(ars)
            
            ar.add_data(doc, meta)
                
            cursize += len(doc)
            if args.chunk and cursize > chunk_size:
                # interleave will not be on
                cursize = 0
                ar.commit(archive_name=args.using)
        
        if args.interleave_output:
            for ar in ars: ar.commit(archive_name=args.using)
        else:
            ar.commit(archive_name=args.using)

    if args.make_fasttext:
        make_fasttext(pile.documents(), 0.1)
    
    if args.make_dataset_samples:
        sample_from_sets(datasets, args.make_dataset_samples)
    
    if args.make_lang_analysis:
        lang_stats(pile)

    if args.make_dummy:
        pbar = tqdm(total=pile.size(), unit="B", unit_scale=1)
        for doc, meta in pile.documents():
            pbar.update(utf8len(doc))
        pbar.close()