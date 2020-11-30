from the_pile.utils import *
import lm_dataformat as lmd
import random
import os
from tqdm import tqdm
import shutil


fnames = ls('pile_output')[:10]

import collections

total_bytes = 0
bytes_per_subset = collections.defaultdict(int)
i = 0

for f in fnames:
    rdr = lmd.Reader(f)
    for doc, meta in rdr.stream_data(get_meta=True):
        size = utf8len(doc)
        bytes_per_subset[meta['pile_set_name']] += size
        total_bytes += size

        i += 1
        if i % 10000 == 0:
            l = list(bytes_per_subset.items())
            l.sort(key=lambda x: -x[1])
            for s, n in l:
                print(s, n / total_bytes)
            print('==============')
