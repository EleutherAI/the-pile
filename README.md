# The Pile™

The Pile is (going to be) the world's largest diverse open source language modeling data set. We are currently developing Version 1, with an ultimate goal of 1 TiB of English text.

|    Component    |   Size   |Weight|Epochs|Mean Document Size|
|-----------------|----------|------|-----:|------------------|
|Bibliotik        |100.96 GiB|20.52%| 2.271|538.36 KiB        |
|PubMed Central   |90.27 GiB |18.35%| 2.271|30.55 KiB         |
|ArXiv            |56.21 GiB |11.42%| 2.271|46.61 KiB         |
|FreeLaw          |51.15 GiB |10.40%| 2.271|15.06 KiB         |
|OpenWebText      |37.03 GiB |7.53% | 2.271|4.84 KiB          |
|StackExchange    |32.20 GiB |6.54% | 2.271|2.16 KiB          |
|USPTO            |22.90 GiB |4.66% | 2.271|4.08 KiB          |
|PubMed Abstracts |19.26 GiB |3.92% | 2.271|1.30 KiB          |
|Wikipedia (en)   |17.27 GiB |3.51% | 2.271|3.00 KiB          |
|OpenSubtitles    |12.98 GiB |2.64% | 2.271|30.48 KiB         |
|Literotica       |11.60 GiB |2.36% | 2.271|25.69 KiB         |
|Gutenberg (PG-19)|10.88 GiB |2.21% | 2.271|398.73 KiB        |
|DM Mathematics   |7.75 GiB  |1.57% | 2.271|47.21 MiB         |
|BookCorpus       |6.30 GiB  |1.28% | 2.271|369.87 KiB        |
|Ubuntu IRC       |5.52 GiB  |1.12% | 2.271|15.96 MiB         |
|EuroParl         |4.59 GiB  |0.93% | 2.271|68.87 KiB         |
|PhilPapers       |2.38 GiB  |0.48% | 2.271|73.37 KiB         |
|NIH ExPorter     |1.89 GiB  |0.39% | 2.271|2.11 KiB          |
|Enron Emails     |901.43 MiB|0.18% | 2.271|1.78 KiB          |
|**Total**        |492.02 GiB|      |      |8.36 KiB          |




(Epochs refers to the number of epochs elapsed after 1.2TB)



## Manual Download Components

The following components need manual downloading. Either download them or comment out from `pile.py`. 

 - **Bibliotik**: `books3.tar.gz` needs to be in the current directory. Download temporarily unavailable.
 - **CORD-19**: `document_parses` needs to be in the current directory. Download from [here](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge).

## Workflow

To propose a new dataset be added to the Pile, [open an issue](https://github.com/EleutherAI/The-Pile/issues/new). Your issue should include a description of the dataset, its size, what language(s) it is in, a link to the data, and any other relevant information. If a project manger approves your proposal, they will change its label to [![Datasets](https://img.shields.io/github/labels/EleutherAI/The-Pile/Dataset)](https://github.com/EleutherAI/The-Pile/labels/Dataset) and add it to [![Project: Datasets](https://img.shields.io/badge/Project-Datasets-lightgrey)](https://github.com/EleutherAI/The-Pile/projects/2). Datasets that we elect to not include in the current version of the Pile will receive a [![Deferred](https://img.shields.io/github/labels/EleutherAI/The-Pile/Deferred%20to%20v2)](https://github.com/EleutherAI/The-Pile/labels/Deferred%20to%20v2) or [![Declined](https://img.shields.io/github/labels/EleutherAI/The-Pile/Declined)](https://github.com/EleutherAI/The-Pile/labels/Declined) label. While we welcome multilingual  datasets and plan on including non-English datasets in the future, the initial release of the Pile will be English-only and all submissions of non-English datasets will be deferred.

To claim responsibility for implementing an unclaimed dataset, leave a comment on one of our unassigned issues. Once an dataset has been assigned to you, make the necessary changes to `datsets.py` and `pile.py` in a fork and submit a pull request. If you require, you can also submit a script for processing the data as shown [here](https://github.com/EleutherAI/pile_enron_emails).

To raise an issue that is not proposing a new dataset, open an issue with the tag [![Feature Request](https://img.shields.io/github/labels/EleutherAI/The-Pile/Feature%20Request)](https://github.com/EleutherAI/The-Pile/labels/Feature%20Request) or [![Bug](https://img.shields.io/github/labels/EleutherAI/The-Pile/Bug)](https://github.com/EleutherAI/The-Pile/labels/Bug) as appropriate.
