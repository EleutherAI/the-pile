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

            wget -nc http://battle.shawwn.com/sdb/books1/books1.tar.gz
            tar xf books1.tar.gz
            """)
            sha256sum('components/bookcorpus/books1.tar.gz')

    def documents(self):
        self._download()

        yield from map(fread, ls('components/bookcorpus/books1/epubtxt'))

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
            sha256sum('components/openwebtext/openwebtext.tar.xz','9fe39d154c5bc67da8c359415372b79510eb1e2edb0d035fe4f7fc3a732b9336')

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


class DMMathDataset(Dataset):
    def name(self):
        return "DM Mathematics"

    def _download(self):
        if not os.path.exists('components/dm_math'):
            sh("""
            mkdir -p components/dm_math
            cd components/dm_math
            virtualenv env
            . env/bin/activate
            pip install gsutil
            gsutil -m rsync gs://mathematics-dataset/ $PWD
            tar xf mathematics_dataset-v1.0.tar.gz
            """)
            sha256sum('components/dm_math/mathematics_dataset-v1.0.tar.gz', 'def638343403cb9ed60437d6b684c859dd23b72779f5cc5661b0a31e67c58576')

    def documents(self):
        self._download()

        yield from concat(
            map(
                lambda x: map(fread, ls('components/dm_math/mathematics_dataset-v1.0/train-' + x)), 
                ['easy', 'medium', 'hard'])
        )

    def clean(self):
        if os.path.exists('components/dm_math'):
            sh("""
            rm -rf components/dm_math
            """)

    def size(self):
        return 8316165951

class EnronEmailsDataset(Dataset):
    def name(self):
        return "Enron Emails"

    def _download(self):
        if not os.path.exists('components/enron_emails'):
            sh("""
            mkdir -p components/enron_emails
            cd components/enron_emails
            git clone https://github.com/EleutherAI/pile_enron_emails .
            virtualenv env
            . env/bin/activate
            pip install -r requirements.txt
            python main.py
            """)
            sha256sum('components/enron_emails/enron_mail_20150507.tar.gz', 'b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7')

    def documents(self):
        self._download()

        yield from lmd.Reader('components/enron_emails/out').stream_data()

    def clean(self):
        if os.path.exists('components/enron_emails'):
            sh("""
            rm -rf components/enron_emails
            """)

    def size(self):
        return 945212874


class LiteroticaDataset(Dataset):
    """ Source: https://www.reddit.com/r/literotica/comments/6xvxvh/i_downloaded_all_380000_stories_on_literotica/?utm_source=share&utm_medium=ios_app&utm_name=iossmf """
    def name(self):
        return "Literotica"

    def _download(self):
        if not os.path.exists('components/literotica'):
            sh("""
            mkdir -p components/literotica
            cd components/literotica
            virtualenv env
            . env/bin/activate
            pip install gdown
            gdown https://drive.google.com/uc?id=0B5J6A3VOJQjGTUt5cm9XMV80cmc
            tar xf liter.tar.gz
            """)
            sha256sum('components/literotica/liter.tar.gz', '9b54711a9df7b0a9512fd4e4d15f7295908791cab514610f5d0c65acd079ec59')

    def documents(self):
        self._download()

        yield from map(fread, ls('components/literotica/liter/story_text'))

    def clean(self):
        if os.path.exists('components/literotica'):
            sh("""
            rm -rf components/literotica
            """)

    def size(self):
        return 9456345155