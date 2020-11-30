from the_pile.utils import *
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import io
import parse

def readf(f):
    with open(f, 'rb') as fh:
        cctx = zstandard.ZstdDecompressor()
        reader = io.BufferedReader(cctx.stream_reader(fh))
        lines = []
        for line in tqdm(reader):
            lines.append(line)

    return lines


def writef(f, lines):
    with open(f, 'wb') as fh:
        cctx = zstandard.ZstdCompressor(level=3, threads=8)
        compressor = cctx.stream_writer(fh)
        for line in tqdm(lines): compressor.write(line)
        compressor.flush(zstandard.FLUSH_FRAME)

import sys
lines = []
for f in sys.argv[2:]:
    print(f)
    lines.extend(readf(f))

writef(sys.argv[1], lines)
