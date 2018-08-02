import copy
import re
import entities

class Tokenizer:

    def __init__(self, exceptions):
        """Costructor function
        :params exceptions : A list of tokenizer exceptions
        """
        self.exceptions = exceptions
        self.hashmap = {}
        self.inv_hashmap = {}

        # hash exceptions
        for e in self.exceptions:
            h = str(hash(e))
            self.hashmap[h] = e
            self.inv_hashmap[e] = h

        # subordinate conjuctions
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

        # construct subordinate conjuctions regex
        self.subordinate_conjuctions_regex = r', ({})[^,]*, '.format(
            '|'.join(self.subordinate_conjuctions))

    def add_exception(self, e):
        """Add exception to tokeinzer
        :params e : The exception to be added
        """
        self.exceptions.append(e)
        hashmap[str(hash(e))] = e

    def hash(q):
        """Hash tokenizer exceptions"""
        for e in self.exceptions:
            q = q.replace(e, self.inv_hashmap[e])
        return q

    def inverse_hash(q):
        """Invert hashed text"""
        for h, e in self.hashmap.items():
            q = q.replace(h, e)
        return q

    def split(self, q, remove_subordinate=False, *delimiter):
        """Split a string using the tokenizer
        :params q : The string to be split
        :params remove_subordinate : True if subordinate conjuctions
        are going to be removed
        :params *delimiter : A list of delimiters to split on
        """
        if remove_subordinate:
            q = self.remove_subordinate(q)

        for e in self.exceptions:
            q = q.replace(e, self.inv_hashmap[e])

        splitting_regex =  '|'.join(map(re.escape, delimiter))
        q = re.split(splitting_regex, q)

        for i, x in enumerate(q):
            for h, e in self.hashmap.items():
                q[i] = q[i].replace(h, e)

        return q

    def split_cases(self, q, ncases, suffix=')', prefix=''):
        """Split into cases provided by Greek Numerals
        e.g. α) Αλφα β) Βήτα yields ['Αλφα', 'Βήτα']
        params: q : String query
        params ncases : Number of cases
        params suffix : Suffix"""
        cases = list(entities.Numerals.greek_num_generator(ncases, suffix=suffix))
        for i in range(len(cases)):
            cases[i] = prefix + cases[i]

        return self.split(q, False, *cases)

    def join_cases(self, l, suffix = ')', prefix=''):
        ncases = len(l) + 1
        cases = [''] + list(entities.Numerals.greek_num_generator(ncases, suffix=suffix))
        result = []
        for c, w in zip(cases, l):
            result.append(prefix + c + w)
        return ' '.join(result).lstrip()

    def remove_subordinate(self, q):
        """Remove subordinate conjuctions from a string
        :params q : String to be cleaned
        """
        return re.sub(self.subordinate_conjuctions_regex, ' ', q)

# Common Tokenizer Exceptions in Legal Texts
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

# Tokenizer object
global tokenizer
tokenizer = Tokenizer(TOKENIZER_EXCEPTIONS)
