import re
import os
import hashlib
from concurrent_iterator.thread import Producer
from functools import reduce
import operator
import collections
import urllib.request
from pathlib import Path
import gdown
import tarfile
import requests
import shutil
from tqdm import tqdm

def download_file(url, to):
    # modified from https://stackoverflow.com/a/37573701
    print('Downloading {}'.format(url))

    response = requests.get(url, stream=True)
    size = int(response.headers.get('content-length', 0))
    block_size = 1024*1024
    pbar = tqdm(total=size, unit='iB', unit_scale=True)
    with open(to, 'wb') as fout:
        for data in response.iter_content(block_size):
            pbar.update(len(data))
            fout.write(data)
    pbar.close()
    assert not (size != 0 and pbar.n != size)

Source = collections.namedtuple('Source', ['type', 'url'])

def download(fname, checksum, sources, extract=False):
    if os.path.exists(fname):
        try:
            sha256sum(fname, expected=checksum)
            return
        except AssertionError:
            print('{} exists but doesn\'t match checksum!'.format(fname))
            rm_if_exists(fname)
            

    parentdir = Path(fname).parent
    os.makedirs(parentdir, exist_ok=True)

    for source in sources:
        try:
            if source.type == 'direct':
                download_file(source.url, fname)
            elif source.type == 'gdrive':
                gdown.download(source.url, fname, quiet=False)
            elif source.type == 'gcloud':
                raise NotImplementedError('gcloud download not implemented!')
            
            sha256sum(fname, expected=checksum)

            if extract:
                tar_xf(fname)
            return
        except KeyboardInterrupt:
            raise
        except:
            import traceback
            traceback.print_exc()
            print('Download method [{}] {} failed, trying next option'.format(source.type, source.url))
            rm_if_exists(fname)
            continue

        break

    raise Exception('Failed to download {} from any source'.format(fname))


def tar_xf(x):
    parentdir = Path(x).parent
    tf = tarfile.open(x)
    tf.extractall(parentdir)

class ExitCodeError(Exception): pass


def id(x):
    return x

def utf8len(s):
    return len(s.encode('utf-8'))

def sh(x):
    if os.system(x): raise ExitCodeError()

def fwrite(fname, content):
    with open(fname, 'w') as fh:
        fh.write(content)

def fread(fname):
    with open(fname) as fh:
        return fh.read()

def ls(x):
    return [x + '/' + fn for fn in os.listdir(x)]


def cycle_documents(dataset):
    while True:
        yield from Producer(filter(id, dataset.documents()), 1000)

def concat(xs):
    for x in xs:
        yield from x


def flatMap(f, x):
    return reduce(operator.add, map(f, x), [])


def sha256sum(filename, expected=None):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    
    if expected:
        assert h.hexdigest() == expected
        print('CHECKSUM OK', filename)
    else:
        print(filename, h.hexdigest())


def rm_if_exists(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except NotADirectoryError:
        os.remove(path)


# https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KiB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MiB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GiB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TiB'.format(B/TB)


def strip_markdown_colons(x):
    return re.sub(r'^:::.*?\n', '', x, flags=re.MULTILINE)

def remove_advertisement(x):
    return re.sub(r'^Advertisement\n', '', x, flags=re.MULTILINE)


def compose(*fs):
    def _f(x):
        for f in reversed(fs):
            x = f(x)
        return x

    return _f