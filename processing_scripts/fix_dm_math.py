from the_pile.utils import *
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import io
import json

import sys


f = sys.argv[1]

fout = 'tmp'

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


def despace(x):
    res = []
    for i, char in enumerate(x):
        if i % 2 == 1:
            if char != '\n':
                print(x)
                raise AssertionError()
        else:
            res.append(char)
    
    return ''.join(res)


def fix(x):
    # optimization
    if b'DM Mathematics' not in x: return x

    ob = json.loads(x)

    if ob['meta']['pile_set_name'] != 'DM Mathematics': return x

    ob['text'] = despace(ob['text'])

    return (json.dumps(ob).strip() + '\n').encode('utf-8')


writef(fout, map(fix, readf(f)))
sh('mv tmp ' + f)

