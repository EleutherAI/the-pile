from the_pile.datasets import WikipediaDataset, GutenbergDataset, PubMedCentralDataset, EnronEmailsDataset

from cassandra.cluster import Cluster

def main():
    # wiki = WikipediaDataset()
    # print("Wiki Size: ", wiki.size())

    # gutenberg = GutenbergDataset()
    # print("Gutenberg Size: ", gutenberg.size())

    # pubmed = PubMedCentralDataset()
    # pubmed._download()

    enron = EnronEmailsDataset()
    enron._download()

def test_cassandra():
    cluster = Cluster(["127.0.0.1"], port=9042)
    session = cluster.connect(wait_for_all_pools=True)
    session.execute('USE cityinfo')
    rows = session.execute('SELECT * FROM users')
    for row in rows:
        print(row.age, row.name, row.username)

if __name__ == '__main__':
    test_cassandra()
