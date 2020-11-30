import lm_dataformat as lmd
from glob import glob
import re
from tqdm import tqdm

ngrams_to_exclude = set()


def hash(s):
    return 


def ngrams(txt, n):
    pos = 0
    words = re.split(r'\s', txt.lower())

    arr = []
    for word in words:
        arr.append((word, pos))
        pos += len(word)

    arr = list(filter(lambda x: x[0].strip(), arr))

    for i in range(len(arr) - n):
        yield arr[i:i+n]


for f in glob('excludes/*'):
    with open(f) as fh:
        doc = fh.read()
        ngs = ngrams(doc, 13)
        for ngram in ngs:
            ngrams_to_exclude.add(' '.join([x[0] for x in ngram]))


def process_doc(txt, n=13):
    ngs = ngrams(txt, n)
    res = []
    delspans = []
    for ngram in ngs:
        joinedn = ' '.join([x[0] for x in ngram])
        if joinedn in ngrams_to_exclude:
            delspans.append((max(0, ngram[0][1] - 200), min(len(txt), ngram[-1][1] + 200)))
    
    if len(delspans) == 0: return [txt]
    
    ptr = 0
    result = []
    for l, r in delspans:
        if ptr < l:
            result.append(txt[ptr:l])
            ptr = r
        if l <= ptr < r:
            ptr = r
        if r < ptr:
            raise AssertionError()
    
    result.append(txt[ptr:])

    result = list(filter(lambda x: len(x) > 200, result))

    if len(result) > 10: return []

    return result


chunk_docs = 50000


dsets = [
    ('output_pile', '00.jsonl.zst'),
    ('output_owt', '/data/datasets/openwebtext'),
]

for outdir, source in dsets:
    ar = lmd.Archive(outdir)
    for i, doc in enumerate(tqdm(lmd.Reader(source).stream_data())):
        for piece in process_doc(doc):
            ar.add_data(piece)

        if (i + 1) % chunk_docs == 0:
            ar.commit()

    ar.commit()
        