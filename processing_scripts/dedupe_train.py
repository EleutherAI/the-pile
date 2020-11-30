from the_pile.utils import *
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import io
import parse

import sys


from glob import glob



def readf(f):
    with open(f, 'rb') as fh:
        cctx = zstandard.ZstdDecompressor()
        reader = io.BufferedReader(cctx.stream_reader(fh))
        yield from tqdm(reader)


def writef(f, lines):
    with open(f, 'wb') as fh:
        cctx = zstandard.ZstdCompressor(level=3, threads=8)
        compressor = cctx.stream_writer(fh)
        for line in tqdm(lines):
            compressor.write(line)
        compressor.flush(zstandard.FLUSH_FRAME)

seen = set()

if os.path.exists('hashes.txt'):
    with open('hashes.txt') as fh:
        for line in tqdm(fh):
            seen.add(line.strip())
else:
    hashf = open('hashes.txt', 'w')
    for f in tqdm(glob('/mnt/data/pile_holdout/*.zst')):
        for doc in readf(f):
            hash = sha256str(doc)
            hashf.write(hash + '\n')
            seen.add(hash)
    hashf.close()

os.makedirs('train', exist_ok=True)

for f in tqdm(glob('train/*')):
    def filtered_docs():
        removed = 0
        for doc in readf(f):
            hash = sha256str(doc)
            if hash in seen:
                removed += 1
                if removed % 1000 == 0:
                    print(removed)
            else:
                yield doc
    writef('train2/' + f.split('/')[-1], filtered_docs())
    
