import copy


class Tokenizer:

    def __init__(self, exceptions):
        self.exceptions = exceptions
        self.hashmap = {}
        self.inv_hashmap = {}
        for e in self.exceptions:
            h = str(hash(e))
            self.hashmap[h] = e
            self.inv_hashmap[e] = h

    def add_exception(self, e):
        self.exceptions.append(e)
        hashmap[str(hash(e))] = e

    def split(self, q, delimiter='.'):

        for e in self.exceptions:
            q = q.replace(e, self.inv_hashmap[e])

        q = q.split(delimiter)

        for i, x in enumerate(q):
            for h, e in self.hashmap.items():
                q[i] = q[i].replace(h, e)

        return q


global TOKENIZER_EXCEPTIONS
TOKENIZER_EXCEPTIONS = [
    'χλμ.',
    'σ.',
    'π.μ.',
    'μ.μ.',
    'π.Χ.',
    'μ.Χ.',
    'δηλ.',
    'τ.μ.',
    'κ.ο.κ',
    'κ.λπ.',
    'κ.α.',
    'κ.ά',
    'κ.κ',
    'παρ.',
    'σελ.',
    'υπ.',
    'κοκ.',
    'αγγλ.',
    'ν.',
    'π.δ.',
    'ν.δ.',
    'κ.υ.α',
    'λ.χ.',
    'κυβ.',
    'κλπ.',
    'κ.',
    'α.α',
    'βλ.',
    'δισ.']

global tokenizer
tokenizer = Tokenizer(TOKENIZER_EXCEPTIONS)
