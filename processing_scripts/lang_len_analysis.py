import lm_dataformat as lmd
from glob import glob
import os
import json
import collections
from tqdm import tqdm

import transformers
import re
from best_download import download_file
import fasttext

import zstandard
import multiprocessing as mp


in_path = 'pile'
out_path = 'langlen_stage1'


def lengths(doc):
    global tok
    return {
        'len_char': len(doc),
        'len_utf8bytes': len(doc.encode('utf-8')),
        'len_words': len(re.split(r'\s+', doc)),
        'len_tokens': len(tok.encode(doc)),
    }


download_file('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'lid.176.bin', '7e69ec5451bc261cc7844e49e4792a85d7f09c06789ec800fc4a44aec362764e')


def language(doc):
    global langdet
    details = langdet.predict(doc.replace('\n', ' '), k=1)

    return {
        'lang': details[0][0].replace('__label__', '')
    }


def writef(f, lines):
    with open(f, 'wb') as fh:
        cctx = zstandard.ZstdCompressor(level=3, threads=8)
        compressor = cctx.stream_writer(fh)
        for line in tqdm(lines):
            compressor.write(line)
        compressor.flush(zstandard.FLUSH_FRAME)


def analyze(ob):
    doc, meta = ob
    res = {
        'pile_set_name': meta['pile_set_name']
    }
    for metric in metrics:
        res = {**res, **metric(doc)}
    return json.dumps(res).encode('utf-8')


metrics = [
    lengths,
    language,
]

def init_process():
    global langdet
    global tok

    langdet = fasttext.load_model("lid.176.bin")
    tok = transformers.GPT2TokenizerFast.from_pretrained('gpt2')


pool = mp.Pool(30, initializer=init_process)


for f in tqdm(sorted(glob(in_path + '/*'))):
    if os.path.exists(out_path + '/analysis_' + f.split('/')[-1]): continue
    def meta_items():
        rdr = lmd.Reader(f)
        return pool.imap(analyze, rdr.stream_data(get_meta=True)) 
    
    writef(out_path + '/tmp_analysis_' + f.split('/')[-1], meta_items())
    os.rename(out_path + '/tmp_analysis_' + f.split('/')[-1], out_path + '/analysis_' + f.split('/')[-1])
