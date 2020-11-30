import lm_dataformat as lmd 
import os
import hashlib
import re
from tqdm import tqdm

def sha256str(s):
    h = hashlib.sha256()
    h.update(s)
    return h.hexdigest()

def stableorder(x):
    arr = [(elem, sha256str(elem.encode('utf-8'))) for elem in x]
    arr.sort(key=lambda x: x[1])
    return [elem for elem,_ in arr]

def ls(x):
    return [x + '/' + fn for fn in stableorder(os.listdir(x))]

def fread(fname):
    with open(fname) as fh:
        return fh.read()

def strip_markdown_colons(x):
    return re.sub(r'^:::.*?\n', '', x, flags=re.MULTILINE)

def compose(*fs):
    def _f(x):
        for f in reversed(fs):
            x = f(x)
        return x

    return _f


ar = lmd.Archive('arxiv_lmd')

for doc in map(compose(strip_markdown_colons, fread), tqdm(ls('documents'))):
    ar.add_data(doc)

ar.commit()