import lm_dataformat as lmd
from glob import glob
import os
import json
import collections
from tqdm import tqdm

import re
from best_download import download_file
import fasttext

import zstandard
import multiprocessing as mp
from profanity_check import predict

in_path = 'pile'
out_path = 'prof_analysis'

# From https://stackoverflow.com/a/31505798
import re
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")

    # return quotes to normal
    text = text.replace("\".", ".\"")
    text = text.replace("”.", ".”")
    text = text.replace("\"!", "!\"")
    text = text.replace("”!", "!”")
    text = text.replace("\"?", "?\"")
    text = text.replace("”?", "?”")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

from best_download import download_file
import fasttext
download_file('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'lid.176.bin', '7e69ec5451bc261cc7844e49e4792a85d7f09c06789ec800fc4a44aec362764e')

langdet = fasttext.load_model("lid.176.bin")

def language(doc):
    details = langdet.predict(doc.replace('\n', ' '), k=1)

    return {
        'lang': details[0][0].replace('__label__', '')
    }

def is_english(doc): return doc != '' and language(doc) == 'en'

def words(sent): return re.split(r'\s+', sent)

def join(arr):
    ret = []
    for val in arr:
        ret.extend(val)
       
    return ret

def unjoin(arr, lens):
    ret = []
    
    last = 0
    for l in lens:
        ret.append(arr[last:last+l])
        last += l
    assert last == len(arr)
    
    return ret


def is_profane(docs):
    if len(docs) == 0: return []
    return list(map(int, predict(docs)))


def profanity(doc):
    sents = list(filter(is_english, split_into_sentences(doc)))
    p_sents = is_profane(sents)
    
    sentwords = list(map(words, sents))
    sentlens = list(map(len, sentwords))
    
    lwords = join(sentwords)
    p_words = list(map(is_profane, lwords))
    p_words = unjoin(p_words, sentlens)
    n_prof = list(map(sum, p_words))
    
    res = list(zip(p_sents, sentlens, n_prof))
    return {
        'sentences': res,
        'num_bytes': len(doc.encode('utf-8'))
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
    profanity
]

pool = mp.Pool(24)


for f in tqdm(sorted(glob(in_path + '/*'))):
    if os.path.exists(out_path + '/analysis_' + f.split('/')[-1]): continue
    def meta_items():
        rdr = lmd.Reader(f)
        return pool.imap(analyze, rdr.stream_data(get_meta=True))
    
    writef(out_path + '/tmp_analysis_' + f.split('/')[-1], meta_items())
    os.rename(out_path + '/tmp_analysis_' + f.split('/')[-1], out_path + '/analysis_' + f.split('/')[-1])
