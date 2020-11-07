import the_pile
import hashlib


def limit_iter(x, ct):
    for i in range(ct):
        yield next(x)


def test_deterministic():
    total_docs = 100000

    # remember to update this hash every time the pile is modified
    expected = 'e197f27c3061a73123277cd79d641681b6abc92b2ea9e69710c045bb73bd8b28'

    # run twice just to make sure it doesn't change
    for i in range(2):
        h1 = hashlib.sha256()
        pile = the_pile.pile()
        for doc in limit_iter(pile.documents(), total_docs):
            h1.update(doc.encode('utf-8'))
        assert h1.hexdigest() == expected