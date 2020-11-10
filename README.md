# The Pile™

The Pile is a large, diverse, open source language modelling data set that consists of many smaller datasets combined together. The objective is to obtain text from as many modalities as possible to ensure that models trained using The Pile will have much broader generalization abilities. We are currently developing Version 1, with an ultimate goal of 1 TiB of English text. After the completion of Version 1, our next goal is a fully-multilingual, 10TiB text dataset.

The Pile is currently **under heavy development**. Breaking changes may be introduced rapidly and without warning. 


|    Component    | Raw Size |Weight|Epochs|Effective Size|Mean Document Size|
|-----------------|----------|------|-----:|--------------|------------------|
|CommonCrawl      |227.12 GiB|19.29%|1.0194|227.12 GiB    |4.33 KiB          |
|PubMed Central   |90.27 GiB |11.66%|1.5501|137.27 GiB    |30.55 KiB         |
|Bibliotik        |100.96 GiB|10.20%|1.2125|120.08 GiB    |538.36 KiB        |
|OpenWebText2     |62.77 GiB |9.69% |1.8530|114.09 GiB    |3.85 KiB          |
|ArXiv            |56.21 GiB |9.68% |2.0669|113.96 GiB    |46.61 KiB         |
|Github           |630.64 GiB|8.07% |0.1536|95.00 GiB     |11.68 KiB         |
|FreeLaw          |51.15 GiB |6.61% |1.5501|77.78 GiB     |15.06 KiB         |
|StackExchange    |32.20 GiB |4.97% |1.8530|58.52 GiB     |2.16 KiB          |
|USPTO            |22.90 GiB |3.95% |2.0669|46.44 GiB     |4.08 KiB          |
|PubMed Abstracts |19.26 GiB |3.32% |2.0669|39.06 GiB     |1.30 KiB          |
|Gutenberg (PG-19)|10.88 GiB |2.20% |2.4251|25.87 GiB     |398.73 KiB        |
|Wikipedia (en)   |6.38 GiB  |1.48% |2.7795|17.39 GiB     |1.11 KiB          |
|DM Mathematics   |7.75 GiB  |1.38% |2.1366|16.23 GiB     |48340.81 KiB      |
|OpenSubtitles    |12.98 GiB |1.32% |1.2233|15.58 GiB     |30.48 KiB         |
|Literotica       |11.60 GiB |1.17% |1.2125|13.80 GiB     |25.69 KiB         |
|BookCorpus       |6.30 GiB  |0.96% |1.8188|11.24 GiB     |369.87 KiB        |
|Ubuntu IRC       |5.52 GiB  |0.84% |1.8349|9.93 GiB      |2060.85 KiB       |
|EuroParl         |4.59 GiB  |0.70% |1.8349|8.25 GiB      |68.87 KiB         |
|PhilPapers       |2.38 GiB  |0.61% |3.1003|7.23 GiB      |73.37 KiB         |
|HackerNews       |3.90 GiB  |0.60% |1.8349|7.02 GiB      |4.92 KiB          |
|YoutubeSubtitles |3.73 GiB  |0.57% |1.8349|6.72 GiB      |22.55 KiB         |
|NIH ExPorter     |1.89 GiB  |0.49% |3.1003|5.76 GiB      |2.11 KiB          |
|Enron Emails     |0.88 GiB  |0.24% |3.2049|2.77 GiB      |1.78 KiB          |
|**Total**        |          |      |      |1177.12 GiB   |7.85 KiB          |








(Epochs refers to the number of epochs elapsed after 1.2TB)


## Usage


Install:

```
pip install -e .
```

To download all data:
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
