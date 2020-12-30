# The Pile Replication Code

## The official website for the the Pile is [here](http://pile.eleuther.ai/).

The Pile is a large, diverse, open source language modelling data set that consists of many smaller datasets combined together. The objective is to obtain text from as many modalities as possible to ensure that models trained using The Pile will have much broader generalization abilities. We are currently developing Version 1, with an ultimate goal of 1 TiB of English text. After the completion of Version 1, our next goal is a fully-multilingual, 10TiB text dataset.

**This repository is for replicating or making variants of the Pile.** If you would like to use the Pile, an official release is planned for the near future. If you would like to be an early user of the Pile before the official release, please contact us through our [discord server](https://discord.com/invite/vtRgjbM).

The Pile is currently **under heavy development**. Breaking changes may be introduced rapidly and without warning. 


|    Component    | Raw Size |Weight|Epochs|Effective Size|Mean Document Size|
|-----------------|----------|------|-----:|--------------|------------------|
|[Pile-CC](https://github.com/leogao2/commoncrawl_downloader)      |227.12 GiB|18.11%|   1.0|227.12 GiB    |4.33 KiB          |
|[PubMed Central](https://github.com/EleutherAI/pile-pubmedcentral)   |90.27 GiB |14.40%|   2.0|180.55 GiB    |30.55 KiB         |
|[Books3](https://twitter.com/theshawwn/status/1320282149329784833)        |100.96 GiB|12.07%|   1.5|151.44 GiB    |538.36 KiB        |
|[OpenWebText2](https://github.com/EleutherAI/openwebtext2)     |62.77 GiB |10.01%|   2.0|125.54 GiB    |3.85 KiB          |
|[ArXiv](https://gist.github.com/leogao2/e09b64eae3b987925ccf3b86401624c6)            |56.21 GiB |8.96% |   2.0|112.42 GiB    |46.61 KiB         |
|[Github](https://github.com/EleutherAI/github-downloader)           |95.16 GiB |7.59% |   1.0|95.16 GiB     |5.25 KiB          |
|[FreeLaw](https://github.com/thoppe/The-Pile-FreeLaw)          |51.15 GiB |6.12% |   1.5|76.73 GiB     |15.06 KiB         |
|[StackExchange](https://github.com/EleutherAI/stackexchange-dataset)    |32.20 GiB |5.13% |   2.0|64.39 GiB     |2.16 KiB          |
|[USPTO Backgrounds](https://github.com/EleutherAI/pile-uspto)            |22.90 GiB |3.65% |   2.0|45.81 GiB     |4.08 KiB          |
|[PubMed Abstracts](https://github.com/thoppe/The-Pile-PubMed) |19.26 GiB |3.07% |   2.0|38.53 GiB     |1.30 KiB          |
|[Gutenberg (PG-19)](https://github.com/deepmind/pg19)|10.88 GiB |2.17% |   2.5|27.19 GiB     |398.73 KiB        |
|[OpenSubtitles](https://github.com/sdtblck/Opensubtitles_dataset)    |12.98 GiB |1.55% |   1.5|19.47 GiB     |30.48 KiB         |
|[Wikipedia (en)](https://github.com/noanabeshima/wikipedia-downloader)   |6.38 GiB  |1.53% |   3.0|19.13 GiB     |1.11 KiB          |
|[DM Mathematics](https://github.com/deepmind/mathematics_dataset)   |7.75 GiB  |1.24% |   2.0|15.49 GiB     |8.00 KiB          |
|[Ubuntu IRC](https://github.com/EleutherAI/pile-ubuntu-irc)       |5.52 GiB  |0.88% |   2.0|11.03 GiB     |545.48 KiB        |
|[BookCorpus2](https://github.com/shawwn/scrap/blob/master/epub2txt-all)       |6.30 GiB  |0.75% |   1.5|9.45 GiB      |369.87 KiB        |
|[EuroParl](https://github.com/thoppe/The-Pile-EuroParl)         |4.59 GiB  |0.73% |   2.0|9.17 GiB      |68.87 KiB         |
|[HackerNews](https://github.com/EleutherAI/hn-scraper)       |3.90 GiB  |0.62% |   2.0|7.80 GiB      |4.92 KiB          |
|[YoutubeSubtitles](https://github.com/sdtblck/youtube_subtitle_dataset) |3.73 GiB  |0.60% |   2.0|7.47 GiB      |22.55 KiB         |
|[PhilPapers](https://github.com/thoppe/The-Pile-PhilPapers)       |2.38 GiB  |0.38% |   2.0|4.76 GiB      |73.37 KiB         |
|[NIH ExPorter](https://github.com/thoppe/The-Pile-NIH-ExPORTER)     |1.89 GiB  |0.30% |   2.0|3.79 GiB      |2.11 KiB          |
|[Enron Emails](https://github.com/EleutherAI/pile-enron-emails)     |0.88 GiB  |0.14% |   2.0|1.76 GiB      |1.78 KiB          |
|**Total**        |          |      |      |1254.20 GiB   |5.91 KiB          |


(Epochs refers to the number of epochs elapsed after 1.2TB)


## Usage


Install:

```
pip install -e .
```

### To replicate pile

```
python the_pile/pile.py --interleave_output 30 --using pile_reprod
```

Use the pass 2 script [here](https://github.com/EleutherAI/The-Pile/tree/master/processing_scripts) to complete shuffling.


### Other

To force download all data:
```
python the_pile/pile.py --force_download
```

To generate fasttext training data for CC filtering (OWT2 only):
```
sudo apt install build-essential
python the_pile/pile.py --using owt2 --make_fasttext 
```

## Manual Download Components

The following components need manual downloading. Either download them or comment out from `pile.py`. 

 - **Bibliotik**: `books3.tar.gz` needs to be in the current directory. Download temporarily unavailable.

## Workflow

To propose a new dataset be added to the Pile, [open an issue](https://github.com/EleutherAI/The-Pile/issues/new). Your issue should include a description of the dataset, its size, what language(s) it is in, a link to the data, and any other relevant information. If a project manger approves your proposal, they will change its label to [![Datasets](https://img.shields.io/github/labels/EleutherAI/The-Pile/Dataset)](https://github.com/EleutherAI/The-Pile/labels/Dataset) and add it to [![Project: Datasets](https://img.shields.io/badge/Project-Datasets-lightgrey)](https://github.com/EleutherAI/The-Pile/projects/2). Datasets that we elect to not include in the current version of the Pile will receive a [![Deferred](https://img.shields.io/github/labels/EleutherAI/The-Pile/Deferred%20to%20v2)](https://github.com/EleutherAI/The-Pile/labels/Deferred%20to%20v2) or [![Declined](https://img.shields.io/github/labels/EleutherAI/The-Pile/Declined)](https://github.com/EleutherAI/The-Pile/labels/Declined) label. While we welcome multilingual  datasets and plan on including non-English datasets in the future, the initial release of the Pile will be English-only and all submissions of non-English datasets will be deferred.

To claim responsibility for implementing an unclaimed dataset, leave a comment on one of our unassigned issues. Once an dataset has been assigned to you, make the necessary changes to `datsets.py` and `pile.py` in a fork and submit a pull request. If you require, you can also submit a script for processing the data as shown [here](https://github.com/EleutherAI/pile_enron_emails).

To raise an issue that is not proposing a new dataset, open an issue with the tag [![Feature Request](https://img.shields.io/github/labels/EleutherAI/The-Pile/Feature%20Request)](https://github.com/EleutherAI/The-Pile/labels/Feature%20Request) or [![Bug](https://img.shields.io/github/labels/EleutherAI/The-Pile/Bug)](https://github.com/EleutherAI/The-Pile/labels/Bug) as appropriate.

Data ready for final implementation should meet the following criteria:

- The data must be in [lm_dataformat](https://github.com/leogao2/lm_dataformat/) format.
- The data must be shuffled.

**In preparation for the initial release, we are no longer accepting additions to the *master* branch. If you would like to contribute a dataset, please submit the pull request to the *Version2* branch.**
