from the_pile.utils import *
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import io
import parse

random.seed(42)

for f in ls('pile_pass1'):
    f = [x for x in ls(f) if 'current_chunk_incomplete' not in x]
    if len(f) == 1: break

f, = f
print(f)

fout = 'pile_output/' + parse.parse('{}chunk{}/{}', f)[1] + '.jsonl.zst'
fouth = 'pile_holdout/' + parse.parse('{}chunk{}/{}', f)[1] + '.jsonl.zst'

with open(f, 'rb') as fh, open(fout, 'wb') as fout, open(fouth, 'wb') as fouth:
    print('reading')
    cctx = zstandard.ZstdDecompressor()
    reader = io.BufferedReader(cctx.stream_reader(fh))
    lines = []
    for line in tqdm(reader):
        lines.append(line)
    
    random.shuffle(lines)

    pivot = int(len(lines) * 0.01)

    holdout = lines[:pivot]
    lines = lines[pivot:]

    cctx = zstandard.ZstdCompressor(level=3, threads=8)
    compressor = cctx.stream_writer(fout)
    print('writing')
    for line in tqdm(lines): compressor.write(line)
    compressor.flush(zstandard.FLUSH_FRAME)

    cctx = zstandard.ZstdCompressor(level=3, threads=8)
    compressor = cctx.stream_writer(fouth)
    print('writing holdout')
    for line in tqdm(holdout): compressor.write(line)
    compressor.flush(zstandard.FLUSH_FRAME)

    del lines

rm_if_exists(f)