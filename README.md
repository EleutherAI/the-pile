# The Pile™

The Pile is (going to be) the world's largest open source language modeling data set. We are currently developing Version 1, with a goal of 1 TiB of English text.

|    Component    |   Size   |Weight|Epochs (@1.2TB)|
|-----------------|----------|------|--------------:|
|Bibliotik        |100.96 GiB|37.55%|          4.157|
|ArXiv            |56.21 GiB |20.91%|          4.157|
|OpenWebText      |37.03 GiB |13.77%|          4.157|
|Wikipedia (en)   |17.27 GiB |6.42% |          4.157|
|OpenSubtitles    |12.98 GiB |4.83% |          4.157|
|Gutenberg (PG-19)|10.88 GiB |4.05% |          4.157|
|Literotica       |8.81 GiB  |3.28% |          4.157|
|DM Mathematics   |7.75 GiB  |2.88% |          4.157|
|BookCorpus       |6.30 GiB  |2.34% |          4.157|
|Ubuntu IRC       |5.52 GiB  |2.05% |          4.157|
|CORD-19          |4.26 GiB  |1.58% |          4.157|
|Enron Emails     |901.43 MiB|0.33% |          4.157|
|**Total**        |268.84 GiB|      |               |


## Manual Download Components

The following components need manual downloading. Either download them or comment out from `pile.py`. 

 - **Bibliotik**: `books3.tar.gz` needs to be in the current directory. Download temporarily unavailable.
 - **CORD-19**: `document_parses` needs to be in the current directory. Download from [here](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge).

## Workflow

To propose a new dataset be added to the Pile, open an issue with the tag [![Proposed Dataset](https://img.shields.io/github/labels/EleutherAI/The-Pile/Proposed%20Dataset)](https://github.com/EleutherAI/The-Pile/labels/Proposed%20Dataset). Your issue should include a description of the dataset, its size, what language(s) it is in, a link to the data, and any other relevant information. If a project manger approves your proposal, they will change its label to [![Datasets](https://img.shields.io/github/labels/EleutherAI/The-Pile/Dataset)](https://github.com/EleutherAI/The-Pile/labels/Dataset) and add it to [![Project: Datasets](https://img.shields.io/badge/Project-Datasets-lightgrey)](https://github.com/EleutherAI/The-Pile/projects/2). Datasets that we elect to not include in the current version of the Pile will receive a [![Deferred](https://img.shields.io/github/labels/EleutherAI/The-Pile/Deferred%20to%20v2)](https://github.com/EleutherAI/The-Pile/labels/Deferred%20to%20v2) or [![Declined](https://img.shields.io/github/labels/EleutherAI/The-Pile/Declined)](https://github.com/EleutherAI/The-Pile/labels/Declined) label. While we welcome multilingual  datasets and plan on including non-English datasets in the future, the initial release of the Pile will be English-only and all submissions of non-English datasets will be deferred.

To claim responsibility for implementing an unclaimed dataset, leave a comment on one of our unassigned issues. Once an dataset has been assigned to you, make the necessary changes to `datsets.py` and `pile.py` in a fork and submit a pull request. If you require, you can also submit a script for processing the data as shown [here](https://github.com/EleutherAI/pile_enron_emails).

To raise an issue that is not proposing a new dataset, open an issue with the tag [![Feature Request](https://img.shields.io/github/labels/EleutherAI/The-Pile/Feature%20Request)](https://github.com/EleutherAI/The-Pile/labels/Feature%20Request) or [![Bug](https://img.shields.io/github/labels/EleutherAI/The-Pile/Bug)](https://github.com/EleutherAI/The-Pile/labels/Bug) as appropriate.
