from tqdm import tqdm
import lm_dataformat as lmd
import random


random.seed(42)

def utf8len(s):
    return len(s.encode('utf-8'))

out = lmd.Archive('github_min')

n = 0
size = 0
for data, meta in tqdm(filter(lambda x: len(x[0]) < 100000, lmd.Reader('components/github/github.jsonl.zst.tar').stream_data(get_meta=True)), total=56626342):
    if random.random() < 0.16:
        out.add_data(data, meta)
        n += 1
        size += utf8len(data)

out.commit()

print('size', size)
print('ndocs', n)