# The Pile™

The Pile is a large, diverse, open source language modelling data set that consists of many smaller datasets combined together. The objective is to obtain text from as many modalities as possible to ensure that models trained using The Pile will have much broader generalization abilities. We are currently developing Version 1, with an ultimate goal of 1 TiB of English text. After the completion of Version 1, our next goal is a fully-multilingual, 10TiB text dataset.

The Pile is currently still under development.


|    Component    | Raw Size |Weight|Epochs|Effective Size|Mean Document Size|
|-----------------|----------|------|-----:|--------------|------------------|
|PubMed Central   |90.27 GiB |14.45%|1.7888|115.59 GiB    |30.55 KiB         |
|Bibliotik        |100.96 GiB|12.64%|1.3992|101.12 GiB    |538.36 KiB        |
|ArXiv            |56.21 GiB |12.00%|2.3851|95.97 GiB     |46.61 KiB         |
|OpenWebText2     |62.77 GiB |10.39%|1.8492|83.09 GiB     |3.85 KiB          |
|Github           |630.64 GiB|10.00%|0.1772|80.00 GiB     |11.68 KiB         |
|FreeLaw          |51.15 GiB |8.19% |1.7888|65.50 GiB     |15.06 KiB         |
|StackExchange    |32.20 GiB |5.33% |1.8492|42.62 GiB     |2.16 KiB          |
|USPTO            |22.90 GiB |4.89% |2.3851|39.11 GiB     |4.08 KiB          |
|Wikipedia (en)   |17.27 GiB |4.29% |2.7738|34.29 GiB     |3.00 KiB          |
|PubMed Abstracts |19.26 GiB |4.11% |2.3851|32.89 GiB     |1.30 KiB          |
|Gutenberg (PG-19)|10.88 GiB |2.72% |2.7985|21.79 GiB     |398.73 KiB        |
|OpenSubtitles    |12.98 GiB |1.80% |1.5471|14.38 GiB     |30.48 KiB         |
|DM Mathematics   |7.75 GiB  |1.71% |2.4656|13.67 GiB     |47.21 MiB         |
|Literotica       |11.60 GiB |1.45% |1.3992|11.62 GiB     |25.69 KiB         |
|BookCorpus       |6.30 GiB  |1.18% |2.0989|9.47 GiB      |369.87 KiB        |
|Ubuntu IRC       |5.52 GiB  |1.15% |2.3206|9.16 GiB      |2.01 MiB          |
|EuroParl         |4.59 GiB  |0.95% |2.3206|7.62 GiB      |68.87 KiB         |
|YoutubeSubtitles |3.73 GiB  |0.78% |2.3206|6.20 GiB      |22.55 KiB         |
|PhilPapers       |2.38 GiB  |0.76% |3.5777|6.09 GiB      |73.37 KiB         |
|NIH ExPorter     |1.89 GiB  |0.61% |3.5777|4.85 GiB      |2.11 KiB          |
|HackerNews       |1.59 GiB  |0.33% |2.3206|2.64 GiB      |4.46 KiB          |
|Enron Emails     |901.43 MiB|0.29% |3.6984|2.33 GiB      |1.78 KiB          |
|**Total**        |1.13 TiB  |      |      |800.00 GiB    |9.45 KiB          |




(Epochs refers to the number of epochs elapsed after 1.2TB)


## Usage


Install:

```
pip install -e .
```

To download all data:
```
python the_pile/pile.py --download
```

To generate fasttext training data for CC filtering (OWT2 only):
```
python the_pile/pile.py --make_fasttext_wt_only
```

## Manual Download Components

The following components need manual downloading. Either download them or comment out from `pile.py`. 

 - **Bibliotik**: `books3.tar.gz` needs to be in the current directory. Download temporarily unavailable.

## Workflow

To propose a new dataset be added to the Pile, [open an issue](https://github.com/EleutherAI/The-Pile/issues/new). Your issue should include a description of the dataset, its size, what language(s) it is in, a link to the data, and any other relevant information. If a project manger approves your proposal, they will change its label to [![Datasets](https://img.shields.io/github/labels/EleutherAI/The-Pile/Dataset)](https://github.com/EleutherAI/The-Pile/labels/Dataset) and add it to [![Project: Datasets](https://img.shields.io/badge/Project-Datasets-lightgrey)](https://github.com/EleutherAI/The-Pile/projects/2). Datasets that we elect to not include in the current version of the Pile will receive a [![Deferred](https://img.shields.io/github/labels/EleutherAI/The-Pile/Deferred%20to%20v2)](https://github.com/EleutherAI/The-Pile/labels/Deferred%20to%20v2) or [![Declined](https://img.shields.io/github/labels/EleutherAI/The-Pile/Declined)](https://github.com/EleutherAI/The-Pile/labels/Declined) label. While we welcome multilingual  datasets and plan on including non-English datasets in the future, the initial release of the Pile will be English-only and all submissions of non-English datasets will be deferred.

To claim responsibility for implementing an unclaimed dataset, leave a comment on one of our unassigned issues. Once an dataset has been assigned to you, make the necessary changes to `datsets.py` and `pile.py` in a fork and submit a pull request. If you require, you can also submit a script for processing the data as shown [here](https://github.com/EleutherAI/pile_enron_emails).

To raise an issue that is not proposing a new dataset, open an issue with the tag [![Feature Request](https://img.shields.io/github/labels/EleutherAI/The-Pile/Feature%20Request)](https://github.com/EleutherAI/The-Pile/labels/Feature%20Request) or [![Bug](https://img.shields.io/github/labels/EleutherAI/The-Pile/Bug)](https://github.com/EleutherAI/The-Pile/labels/Bug) as appropriate.

