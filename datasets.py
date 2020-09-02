import abc
import os
import lm_dataformat as lmd
import json
from tqdm import tqdm

from utils import *

class Dataset(abc.ABC):
    @abc.abstractmethod
    def name(self):
        """ Human-readable name of the dataset """
        pass

    @abc.abstractmethod
    def documents(self):
        """ A generator producing all documents in the dataset. """
        pass

    @abc.abstractmethod
    def clean(self):
        """ Remove any dataset files. """
        pass
    
    def size(self):
        """ Return an estimate of the dataset size. Implementations may use a faster, less accurate estimate. """

        return sum(map(utf8len, tqdm(self.documents())))

class WikipediaDataset(Dataset):
    def name(self):
        return "Wikipedia (en)"

    def _download(self):
        if not os.path.exists('components/wikipedia_en'):
            sh("""
            git clone https://github.com/noanabeshima/wikipedia-downloader/ components/wikipedia_en
            cd components/wikipedia_en
            virtualenv env
            . env/bin/activate
            bash install_requirements.sh
            python main.py
            """)

    def documents(self):
        self._download()

        for file in ls('components/wikipedia_en/output'):
            ob = json.loads(fread(file))
            yield from ob

    def clean(self):
        if os.path.exists('components/wikipedia_en'):
            sh("""
            rm -rf components/wikipedia_en
            """)
    
    def size(self):
        self._download()
        return sum(os.path.getsize(f) for f in ls('components/wikipedia_en/output'))


class OpensubtitlesDataset(Dataset):
    def name(self):
        return "OpenSubtitles"

    def _download(self):
        if not os.path.exists('components/opensubtitles'):
            sh("""
            git clone https://github.com/sdtblck/Opensubtitles_dataset components/opensubtitles
            cd components/opensubtitles
            virtualenv env
            . env/bin/activate
            pip install -r requirements.txt
            python3 parse_opensubtitle_xml.py
            """)

    def documents(self):
        self._download()

        yield from lmd.Reader('components/opensubtitles/out').stream_data()

    def clean(self):
        if os.path.exists('components/opensubtitles'):
            sh("""
            rm -rf components/opensubtitles
            """)

    def size(self):
        return 13940478112


class BookCorpusDataset(Dataset):
    def name(self):
        return "BookCorpus"

    def _download(self):
        if not os.path.exists('components/bookcorpus/nometa'):
            sh("""
            mkdir -p components/bookcorpus
            cd components/bookcorpus

            wget -nc https://battle.shawwn.com/sdb/bookcorpus/2020-09-01-bookcorpus-nometa.tar.zst
            tar -I zstd -xf 2020-09-01-bookcorpus-nometa.tar.zst
            """)

    def documents(self):
        self._download()

        yield from map(fread, ls('components/bookcorpus/nometa/epub'))

    def clean(self):
        if os.path.exists('components/bookcorpus'):
            sh("""
            rm -rf components/bookcorpus
            """)

    def size(self):
        return 6767414779

class OpenWebTextDataset(Dataset):
    def name(self):
        return "OpenWebText"

    def _download(self):
        if not os.path.exists('components/openwebtext'):
            sh("""
            mkdir -p components/openwebtext
            cd components/openwebtext
            virtualenv env
            . env/bin/activate
            pip install gdown
            gdown https://drive.google.com/uc?id=1EA5V0oetDCOke7afsktL_JDQ-ETtNOvx
            tar xf openwebtext.tar.xz
            """)

    def documents(self):
        self._download()

        yield from lmd.Reader('components/openwebtext/openwebtext').stream_data()

    def clean(self):
        if os.path.exists('components/openwebtext'):
            sh("""
            rm -rf components/openwebtext
            """)
    
    def size(self):
        return 39757465434


class GutenbergDataset(Dataset):
    def name(self):
        return "Gutenberg (PG-19)"

    def _download(self):
        if not os.path.exists('components/gutenberg'):
            sh("""
            mkdir -p components/gutenberg
            cd components/gutenberg
            virtualenv env
            . env/bin/activate
            pip install gsutil
            mkdir -p pg19_train
            gsutil -m rsync gs://deepmind-gutenberg/train ./pg19_train

            """)

    def documents(self):
        self._download()

        yield from map(fread, ls('components/gutenberg/pg19_train'))

    def clean(self):
        if os.path.exists('components/gutenberg'):
            sh("""
            rm -rf components/gutenberg
            """)
    
    def size(self):
        self._download()
        return sum(os.path.getsize(f) for f in ls('components/gutenberg/pg19_train'))