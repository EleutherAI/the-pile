# The Pile™
|    Component    |   Size   |Weight|Epochs (@1.2TB)|
|-----------------|----------|------|--------------:|
|Bibliotik        |100.96 GiB|47.48%|          5.256|
|OpenWebText      |37.03 GiB |17.41%|          5.256|
|Wikipedia (en)   |17.27 GiB |8.12% |          5.256|
|OpenSubtitles    |12.98 GiB |6.11% |          5.256|
|Gutenberg (PG-19)|10.88 GiB |5.12% |          5.256|
|Literotica       |8.81 GiB  |4.14% |          5.256|
|DM Mathematics   |7.75 GiB  |3.64% |          5.256|
|BookCorpus       |6.30 GiB  |2.96% |          5.256|
|Ubuntu IRC       |5.52 GiB  |2.59% |          5.256|
|CORD-19          |4.26 GiB  |2.00% |          5.256|
|Enron Emails     |901.43 MiB|0.41% |          5.256|
|**Total**        |212.63 GiB|      |               |

## Manual Download Components

The following components need manual downloading. Either download them or comment out from `pile.py`. 

 - **Bibliotik**: `books3.tar.gz` needs to be in the current directory. Download temporarily unavailable.
 - **CORD-19**: `document_parses` needs to be in the current directory. Download from [here](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge).

## Workflow

To propose a new dataset be added to the Pile, open an issue with the tag ![](https://img.shields.io/github/labels/EleutherAI/The-Pile/Proposed%20Dataset). Your issue should include a description of the dataset, its size, what language(s) it is in, a link to the data, and any other relevant information. If a project manger approves your proposal, they will change its label to ![](https://img.shields.io/github/labels/EleutherAI/The-Pile/Dataset?link=https://github.com/EleutherAI/The-Pile/issues?q=is%3Aissue+is%3Aopen+label%3ADataset) and add it to ![](https://img.shields.io/badge/Project-Datasets-lightgrey?link=https://github.com/EleutherAI/The-Pile/projects/2&link=https://github.com/EleutherAI/The-Pile/projects/2).

To claim an unclaimed dataset, leave a comment on one of our unassigned issues. Once an dataset has been assigned to you, make the necessary changes to `datsets.py` and `pile.py` in a fork and submit a pull request. If you require, you can also submit a script for processing the data as shown [here](https://github.com/EleutherAI/pile_enron_emails).

To raise an issue that is not proposing a new dataset, open an issue with the tag ![](https://img.shields.io/github/labels/EleutherAI/The-Pile/Feature%20Request) or ![](https://img.shields.io/github/labels/EleutherAI/The-Pile/Bug) as appropriate.
