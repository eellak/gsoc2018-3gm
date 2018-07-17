import copy
import re


class Tokenizer:

    def __init__(self, exceptions):
        self.exceptions = exceptions
        self.hashmap = {}
        self.inv_hashmap = {}
        for e in self.exceptions:
            h = str(hash(e))
            self.hashmap[h] = e
            self.inv_hashmap[e] = h

        self.subordinate_conjuctions = [
            'ότι',
            'όπως',
            'πως',
            'που',
            'μήπως',
            'να',
            'όταν',
            'ενώ',
            'καθώς',
            'αφού',
            'αφότου',
            'ωσότου',
            'για να',
            'άμα',
            'εάν',
            'αν',
            'ώστε',
            'αν και',
            'μολονότι',
            'παρά'
        ]

        self.subordinate_conjuctions_regex = r', ({})[^,]*, '.format(
            '|'.join(self.subordinate_conjuctions))

    def add_exception(self, e):
        self.exceptions.append(e)
        hashmap[str(hash(e))] = e

    def split(self, q, remove_subordinate=False, delimiter='.'):
        if remove_subordinate:
            q = self.remove_subordinate(q)

        for e in self.exceptions:
            q = q.replace(e, self.inv_hashmap[e])

        q = q.split(delimiter)

        for i, x in enumerate(q):
            for h, e in self.hashmap.items():
                q[i] = q[i].replace(h, e)

        return q

    def remove_subordinate(self, q):
        return re.sub(self.subordinate_conjuctions_regex, ' ', q)


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
