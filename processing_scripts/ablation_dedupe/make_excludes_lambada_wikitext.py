import re

def wikitext_detokenizer(string):
    # contractions
    string = string.replace("s '", "s'")
    string = re.sub(r"/' [0-9]/", r"/'[0-9]/", string)
    # number separators
    string = string.replace(" @-@ ", "-")
    string = string.replace(" @,@ ", ",")
    string = string.replace(" @.@ ", ".")
    # punctuation
    string = string.replace(" : ", ": ")
    string = string.replace(" ; ", "; ")
    string = string.replace(" . ", ". ")
    string = string.replace(" ! ", "! ")
    string = string.replace(" ? ", "? ")
    string = string.replace(" , ", ", ")
    # double brackets
    string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
    string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
    string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
    string = re.sub(r"\"\s*([^\"]*?)\s*\"", r'"\1"', string)
    string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
    # miscellaneous
    string = string.replace("= = = =", "====")
    string = string.replace("= = =", "===")
    string = string.replace("= =", "==")
    string = string.replace(" " + chr(176) + " ", chr(176))
    string = string.replace(" \n", "\n")
    string = string.replace("\n ", "\n")
    string = string.replace(" N ", " 1 ")
    string = string.replace(" 's", "'s")

    return string


def lambada_detokenizer(text):
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    return '\n'+text.strip()


from glob import glob
for f in [*glob('wikitext-2-raw/*'), *glob('wikitext-103-raw/*')]:
    if 'train' in f: continue
    with open(f) as fh,open('excludes/' + '_'.join(f.split('/')[-2:]) + '.txt', 'w') as fout:
        fout.write(wikitext_detokenizer(fh.read()))

import json
with open('lambada_test.jsonl') as fh, open('excludes/lambada.txt', 'w') as fout:
    for line in fh:
        fout.write(json.loads(line)['text'] + '\n')