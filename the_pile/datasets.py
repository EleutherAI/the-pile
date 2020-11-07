import abc
import os
import json

import gdown
import lm_dataformat as lmd
from tqdm import tqdm

from .utils import *

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

        size = sum(map(utf8len, tqdm(self.documents())))
        print('size', self.name(), size)
        return size
    
    def num_docs(self):
        """ Return an estimate of the number of documents in the dataset. Implementations may use a faster, less accurate estimate. """

        size = len(list(map(lambda x: None, tqdm(self.documents()))))
        print('docs', self.name(), size)
        return size


class WikipediaDataset(Dataset):
    def name(self):
        return "Wikipedia (en)"

    def _download(self):
        download('components/wikipedia_en/output/wikipedia-en.tar.gz', '87b78787f71297250bca644ab9d8e3992346eeb2e2ad91101487109e3d01e644', [
            Source('direct', 'http://eaidata.bmk.sh/data/wikipedia-en.tar.gz'),
        ], extract=True)

    def documents(self):
        self._download()

        for file in ls('components/wikipedia_en/output'):
            if not file.endswith('.json'):
                continue

            with open(file) as fh:
                ob = json.load(fh)
                yield from dummy_meta(ob)

    def clean(self):
        rm_if_exists('components/wikipedia_en')
    
    def size(self):
        return 6847462907
    
    def num_docs(self):
        return 6033151


class OpensubtitlesDataset(Dataset):
    def name(self):
        return "OpenSubtitles"

    def _download(self):
        download('components/opensubtitles/opensubtitles_out.tar', 'f3039709677292f899bb0a8fa2dbc6ae785f9e33ffd7613f94f4f722f2dfd95c', [
            Source('direct', 'http://eaidata.bmk.sh/data/opensubtitles_out.tar'),
        ], extract=True)

    def documents(self):
        self._download()

        return dummy_meta(lmd.Reader('components/opensubtitles/out').stream_data())

    def clean(self):
        rm_if_exists('components/opensubtitles')


    def size(self):
        return 13940478112

    def num_docs(self):
        return 446612


class BookCorpusDataset(Dataset):
    def name(self):
        return "BookCorpus"

    def _download(self):
        download('components/bookcorpus/books1.tar.gz', 'e3c993cc825df2bdf0f78ef592f5c09236f0b9cd6bb1877142281acc50f446f9', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/books1.tar.gz'),
            Source('direct', 'http://battle.shawwn.com/sdb/books1/books1.tar.gz'),
        ], extract=True)

    def documents(self):
        self._download()

        return dummy_meta(map(fread, ls('components/bookcorpus/books1/epubtxt')))

    def clean(self):
        rm_if_exists('components/bookcorpus')

    def size(self):
        return 6767414779
    
    def num_docs(self):
        return 17868


class OpenWebTextDataset(Dataset):
    def name(self):
        return "OpenWebText"

    def _download(self):
        # todo: convert
        download_directory = "components/openwebtext"
        done_file = os.path.join(download_directory, "download.done")
        if not os.path.exists(done_file):
            os.makedirs(download_directory, exist_ok=True)
            url = "https://drive.google.com/uc?id=1EA5V0oetDCOke7afsktL_JDQ-ETtNOvx"
            output_file = os.path.join(download_directory, "openwebtext.tar.xz")        
            gdown.download(url, output_file, quiet=False)
            sha256sum(output_file,'9fe39d154c5bc67da8c359415372b79510eb1e2edb0d035fe4f7fc3a732b9336')

            with open(done_file, "w") as fh:
                fh.write("done!")

    def documents(self):
        self._download()

        return dummy_meta(lmd.Reader('components/openwebtext/openwebtext').stream_data())

    def clean(self):
        rm_if_exists('components/openwebtext')

    
    def size(self):
        return 39757465434
    
    def num_docs(self):
        return 8013769


class GutenbergDataset(Dataset):
    def name(self):
        return "Gutenberg (PG-19)"

    def _download(self):
        if not os.path.exists('components/gutenberg'):
            # todo: convert after gcloud download is implemented
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

        return dummy_meta(map(fread, ls('components/gutenberg/pg19_train')))

    def clean(self):
        rm_if_exists('components/gutenberg')
    
    def size(self):
        return 11678184672
    
    def num_docs(self):
        return 28602


class DMMathDataset(Dataset):
    def name(self):
        return "DM Mathematics"

    def _download(self):
        if not os.path.exists('components/dm_math'):
            # todo: convert after gcloud download is implemented
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

        return dummy_meta(concat(
            map(
                lambda x: map(fread, ls('components/dm_math/mathematics_dataset-v1.0/train-' + x)), 
                ['easy', 'medium', 'hard'])
        ))

    def clean(self):
        rm_if_exists('components/dm_math')

    def size(self):
        return 8316165951

    def num_docs(self):
        return 168


class EnronEmailsDataset(Dataset):
    def name(self):
        return "Enron Emails"

    def _download(self):
        download('components/enron_emails/enron_mail_20150507.tar.gz', 'b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7', [
            Source('direct', 'http://eaidata.bmk.sh/data/enron_mail_20150507.tar.gz'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/enron_emails/out').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/enron_emails')

    def size(self):
        return 945212874
    
    def num_docs(self):
        return 517401


class LiteroticaDataset(Dataset):
    """ Source: https://www.reddit.com/r/literotica/comments/6xvxvh/i_downloaded_all_380000_stories_on_literotica/?utm_source=share&utm_medium=ios_app&utm_name=iossmf """
    def name(self):
        return "Literotica"

    def _download(self):
        download('components/literotica/Literotica.jsonl.zst', '3c6b968f851831c6345f175b394416f7521da3bacd90fdc827093f0d310bd4ef', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/Literotica.jsonl.zst'),
            Source('gdrive', 'https://drive.google.com/uc?id=1Nx63w9BFZZSI_s2pmJnhcBU9c-y803T7'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/literotica/Literotica.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/literotica')

    def size(self):
        return 12458318640
    
    def num_docs(self):
        return 473653


class BibliotikDataset(Dataset):
    def name(self):
        return "Bibliotik"

    def _download(self):
        download('components/bibliotik/books3.tar.gz', '016b90fa6b8507328b6a90d13b0f68c2b87dfd281b35e449a1d466fd9eebc14a', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/books3.tar.gz'),
        ], extract=True)

    def documents(self):
        self._download()

        #yield from map(fread, flatMap(ls, ls('components/bibliotik/books3/the-eye.eu/public/Books/Bibliotik')))
        yield from lmd.Reader('components/bibliotik/Bibliotik.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/bibliotik')

    def size(self):
        return 108404259563
    
    def num_docs(self):
        return 196640


class CORD19Dataset(Dataset):
    def name(self):
        return "CORD-19"

    def _download(self):

        if not os.path.exists('components/cord19'):
            if not os.path.exists('document_parses'):
                raise AssertionError('Must download document_parses manually!')

            sh("""
            mkdir -p components/cord19
            cd components/cord19

            git clone https://github.com/EleutherAI/pile_cord19 .
            virtualenv env
            . env/bin/activate

            mv ../../document_parses .

            pip install -r requirements.txt
            python main.py
            """)

    def documents(self):
        self._download()

        return lmd.Reader('components/cord19/out').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/cord19')
    
    def size(self):
        return 4573360967
    
    def num_docs(self):
        return 174560


class UbuntuIRCDataset(Dataset):
    def name(self):
        return "Ubuntu IRC"

    def _download(self):
        download('components/ubuntu_irc/ubuntu_irc_until_2020_9_1.jsonl.zst', 'b2bd119beb2741f428c7f1de954794718ce6e8090e3125be5e64845bb320767e', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/ubuntu_irc_until_2020_9_1.jsonl.zst'),
            Source('direct', 'http://eaidata.bmk.sh/data/ubuntu_irc_until_2020_9_1.jsonl.zst'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/ubuntu_irc/ubuntu_irc_until_2020_9_1.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/ubuntu_irc')
    
    def size(self):
        return 5923631555
    
    def num_docs(self):
        return 2807


class ArXivDataset(Dataset):
    def name(self):
        return "ArXiv"

    def _download(self):
        download('components/arxiv/arxiv.jsonl.zst', '084b894f513986076a7d97e5c323c7fa8ebef1733f151a7fbdb139c19c07b571', [
            Source('direct', 'http://eaidata.bmk.sh/data/arxiv.jsonl.zst'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/arxiv/arxiv.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/arxiv')

    def size(self):
        return 60353358395
    
    def num_docs(self):
        return 1264405


class PubMedDataset(Dataset):
    def name(self):
        return "PubMed Abstracts"

    def _download(self):
        download('components/pubmed/PUBMED_title_abstracts_2019_baseline.jsonl.zst', '15c26a83ac2b11378b8e6ba5a16bab92428de29bacb85709834948cfcf1f029b', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/PUBMED_title_abstracts_2019_baseline.jsonl.zst'),
            Source('direct', 'http://eaidata.bmk.sh/data/PUBMED_title_abstracts_2019_baseline.jsonl.zst'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/pubmed/PUBMED_title_abstracts_2019_baseline.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/pubmed')

    def size(self):
        return 20684050384
    
    def num_docs(self):
        return 15518009


class ExPorterDataset(Dataset):
    def name(self):
        return "NIH ExPorter"

    def _download(self):
        download('components/exporter/NIH_ExPORTER_awarded_grant_text.jsonl.zst', 'be7fc69b9a3652391b6567891b99277ac99e7dfd5892ba19cb312f909357c458', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/NIH_ExPORTER_awarded_grant_text.jsonl.zst'),
            Source('gdrive', 'https://drive.google.com/uc?id=11mO-0LuL2YeKoqqWXyHPHf3d2ODnjVPP'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/exporter/NIH_ExPORTER_awarded_grant_text.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/exporter')
    
    def size(self):
        return 2034579138
    
    def num_docs(self):
        return 939661


class StackExchangeDataset(Dataset):
    def name(self):
        return "StackExchange"

    def _download(self):
        download('components/stackexchange/stackexchange_dataset.tar', 'f64f31d20db8d8692c1a019314a14974b4911a34ffef126feaf42da88860c666', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/stackexchange_dataset.tar'),
            Source('direct', 'http://eaidata.bmk.sh/data/stackexchange_dataset.tar'),
        ], extract=True)

    def documents(self):
        self._download()

        return dummy_meta(lmd.Reader('components/stackexchange/out').stream_data())

    def clean(self):
        rm_if_exists('components/stackexchange/out')

    def size(self):
        return 34571286358
    
    def num_docs(self):
        return 15622475


class FreeLawDataset(Dataset):
    def name(self):
        return "FreeLaw"

    def _download(self):
        download('components/freelaw/FreeLaw_Opinions.jsonl.zst', '7d7ba907cf397e8585bb3ef148b3e9678edbf142b2247460f907c16aecbaed2d', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/FreeLaw_Opinions.jsonl.zst'),
            Source('gdrive', 'https://drive.google.com/uc?id=1L-x3g3V888gHNUVHQWDkJBJHs5N02Kjz'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/freelaw/FreeLaw_Opinions.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/freelaw')
    
    def size(self):
        return 54923939791
    
    def num_docs(self):
        return 3562015


class PubMedCentralDataset(Dataset):
    def name(self):
        return "PubMed Central"

    def _download(self):
        download('components/pubmedcentral/PMC_extracts.tar.gz', 'dd2ecc79480bd5b78c29ea78af96941c69f6bda3d36a7d510019ccc4848fb867', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/PMC_extracts.tar.gz'),
            Source('direct', 'http://eaidata.bmk.sh/data/PMC_extracts.tar.gz'),
        ])

    def documents(self):
        self._download()

        return dummy_meta(map(strip_markdown_colons, lmd.Reader('components/pubmedcentral/PMC_extracts.tar.gz').stream_data()))

    def clean(self):
        rm_if_exists('components/pubmedcentral')

    def size(self):
        return 96929951580

    def num_docs(self):
        return 3098931


class CZICDataset(Dataset):
    def name(self):
        return "CZIC"

    def _download(self):
        # todo: convert CZIC
        if not os.path.exists('components/czic'):
            sh("""
            mkdir -p components/czic
            cd components/czic
            virtualenv env
            . env/bin/activate
            pip install gdown
            gdown https://drive.google.com/uc?id=1qjZZTqS-m63TMKBYB1eNRc5Bh4W--SYQ
            """)
            sha256sum('components/czic/GOVINFO_CZIC_KL.jsonl.zst', 'c7a46f5af12789fc8b2105b208e22fa400c63ac720c72073e90ee91af6744f00')

    def documents(self):
        self._download()

        return lmd.Reader('components/czic/GOVINFO_CZIC_KL.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/czic')

    def size(self):
        return 837798818

    def num_docs(self):
        return 4774


class PhilPapersDataset(Dataset):
    def name(self):
        return "PhilPapers"

    def _download(self):
        download('components/philpapers/PhilArchive.jsonl.zst', 'e90529b9b3961328d1e34b60534a8e0f73d5ad1f104e22a217de53cd53c41fea', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/PhilArchive.jsonl.zst'),
            Source('gdrive', 'https://drive.google.com/uc?id=1u01vkBNAS8jtu0AZeQW56bzf-6QbeSRB'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/philpapers/PhilArchive.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/philpapers')

    def size(self):
        return 2553543227

    def num_docs(self):
        return 33990


class USPTODataset(Dataset):
    def name(self):
        return "USPTO"

    def _download(self):
        download('components/uspto/pile_uspto.jsonl.zst.tar', '7a7d2c8e21df2ad0324810a8e675f4d8bdc5ee40b17914a6c0542ddfda1560fd', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/pile_uspto.tar'),
            Source('direct', 'http://eaidata.bmk.sh/data/pile_uspto.tar'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/uspto/pile_uspto.jsonl.zst.tar').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/uspto')

    def size(self):
        return 24593538339

    def num_docs(self):
        return 5883037


class EuroParlDataset(Dataset):
    def name(self):
        return "EuroParl"

    def _download(self):
        download('components/europarl/EuroParliamentProceedings_1996_2011.jsonl.zst', '6111400e7b7f75ce91fed1b5fc0a3630b8263217bd01ce75f7d8701f26ac0e98', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/EuroParliamentProceedings_1996_2011.jsonl.zst'),
            Source('gdrive', 'https://drive.google.com/uc?id=12Q23Y7IKQyjF28xH0Aw6yZaYEx2YIOiB'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/europarl/EuroParliamentProceedings_1996_2011.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/europarl')

    def size(self):
        return 4923130035

    def num_docs(self):
        return 69814


class YTSubtitlesDataset(Dataset):
    def name(self):
        return "YoutubeSubtitles"

    def _download(self):
        download('components/youtubesubtitles/yt_subs.jsonl.zst', '0b9130b8c92290eba360337fea90c2617721f65d955f785f8755cb5f4a8e319c', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/yt_subs.jsonl.zst'),
            Source('direct', 'http://eaidata.bmk.sh/data/yt_subs.jsonl.zst'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/youtubesubtitles/yt_subs.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/youtubesubtitles')

    def size(self):
        return 4010420381

    def num_docs(self):
        return 173651


class HackerNewsDataset(Dataset):
    def name(self):
        return "HackerNews"

    def _download(self):
        download('components/hackernews/hn.tar.gz', '6220e1dcd5d9d71821fee552e4e154ee1ee5f62744e3eab9a4c5001f52e27067', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/hn.tar.gz'),
            Source('direct', 'http://eaidata.bmk.sh/data/hn.tar.gz'),
        ])

    def documents(self):
        self._download()

        return dummy_meta(lmd.Reader('components/hackernews/hn.tar.gz').stream_data())

    def clean(self):
        rm_if_exists('components/hackernews')
    
    def size(self):
        return 1704809038
    
    def num_docs(self):
        return 373028


class GithubDataset(Dataset):
    def name(self):
        return "Github"

    def _download(self):
        download('components/github/github.jsonl.zst.tar', 'f7a66e8226baf075a42628d10d8eba234460da73b0ffd300736036db9be3b3c3', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/github.tar'),
            Source('direct', 'http://eaidata.bmk.sh/data/github.tar'),
        ])

    def documents(self):
        self._download()

        return filter(lambda x: len(x[0]) < 100000, lmd.Reader('components/github/github.jsonl.zst.tar').stream_data(get_meta=True))

    def clean(self):
        rm_if_exists('components/github')
    
    def size(self):
        return 677143668214
    
    def num_docs(self):
        return 56626342


class OpenWebText2Dataset(Dataset):
    def name(self):
        return "OpenWebText2"

    def _download(self):
        download('components/openwebtext2/openwebtext2.jsonl.zst.tar', '9043d1b93c35ff1a38a17e16c73c009d4617dcaab6da15adc0faf4779739a027', [
            Source('direct', 'https://the-eye.eu/public/AI/pile_preliminary_components/openwebtext2.jsonl.zst.tar'),
            Source('direct', 'http://eaidata.bmk.sh/data/openwebtext2.jsonl.zst.tar'),
        ])

    def documents(self):
        self._download()

        return map(lambda x: (remove_advertisement(x[0]), x[1]), lmd.Reader('components/openwebtext2/openwebtext2.jsonl.zst.tar').stream_data(get_meta=True))

    def clean(self):
        rm_if_exists('components/openwebtext2')
    
    def size(self):
        return 67396380547
    
    def num_docs(self):
        return 17103059


class CommonCrawlDataset(Dataset):
    def name(self):
        return "CommonCrawl"

    def _download(self):
        download('components/commoncrawl/pile_cc_filtered_deduped.jsonl.zst', '4906a6731a7d2d9182c40a13d681078ed537508cf75b1d32ad7f7c491b2f272a', [
            Source('direct', 'http://eaidata.bmk.sh/data/pile_cc_filtered_deduped.jsonl.zst'),
        ])

    def documents(self):
        self._download()

        return lmd.Reader('components/commoncrawl/pile_cc_filtered_deduped.jsonl.zst').stream_data(get_meta=True)

    def clean(self):
        rm_if_exists('components/commoncrawl')
    
    def size(self):
        return 243872121726
    
    def num_docs(self):
        return 54953117