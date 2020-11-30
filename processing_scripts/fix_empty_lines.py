from the_pile.utils import *
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import io
import parse

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


def cont(x):
    return x.strip()


writef(fout, filter(cont, readf(f)))
sh('mv tmp ' + f)
