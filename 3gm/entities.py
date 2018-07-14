import re
import numpy as np
from helpers import *
import string


class Minister:

    def __init__(self, name, middle, surname, ministry):
        self.name = name
        self.surname = surname
        self.ministry = ministry
        self.middle = middle

    def is_mentioned(self, s):
        search_full = re.search(self.name + ' ' + self.surname, s)
        if search_full is not None:
            return search_full.span()
        search_sur = re.search(self.surname, s)
        if search_sur is not None:
            return search_sur.span()
        search_min = re.search(self.ministry, s)
        if search_min is not None:
            return search_min.span()

    def __repr__(self):
        return '{} {}'.format(self.name, self.surname)


class Action:

    def __init__(self, name, lemma, derivatives=[], weight_vector=None):
        self.name = name
        self.lemma = lemma
        self.derivatives = derivatives
        self.derivatives.append(name)
        if weight_vector is None:
            self.weight_vector = (1 / (len(self.derivatives))) * \
                np.ones(len(self.derivatives))
        else:
            self.weight_vector = weight_vector

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def score(self, word, _normalize_word=True):
        scores = np.zeros(len(self.derivatives))
        for i, derivative in enumerate(self.derivatives):
            scores[i] = edit_distance(
                word if not _normalize_word else normalize_word(word), derivative)
        return np.dot(scores, self.weight_vector)

    def __eq__(self, q):
        w = q.lower()
        return w == self.name or w in self.derivatives or w == self.name.capitalize(
        ) or w in list(map(lambda s: s.capitalize(), self.derivatives))

# Actions
actions = [
    Action('προστίθεται', 'add', ['προσθέτουμε', 'προσθήκη', 'προστίθενται']),
    Action('διαγράφεται', 'delete', ['διαγράφουμε', 'διαγραφή', 'διαγράφονται', 'καταργείται', 'καταργούνται']),
    Action('παύεται', 'terminate', ['παύση', 'παύουμε', 'παύονται']),
    Action('τροποποιείται', 'amend', ['τροποποίηση', 'τροποποιούμε', 'τροποποιούνται']),
    Action('αντικαθίσταται', 'replace', ['αντικαθίσταται', 'αντικατάσταση', 'αντικαθίστανται']),
    Action('αναριθμείται', 'renumber', ['αναριθμείται', 'αναριθμούνται'])
]

# Entities - Statutes
whats = [
    'φράση',
    'παράγραφος',
    'άρθρο',
    'εδάφιο',
    'φράσεις',
    'άρθρα',
    'εδάφια',
    'παράγραφοι',
    'τίτλος',
    'περίπτωση',
    'περιπτώσεις',
    'υποπερίπτωση',
    'υποπεριπτώσεις'
    ]

wheres = ['Στο', 'στο', 'Στην', 'στην', 'στον', 'Στον']


law_regex = r'(ν.|Ν.) [0-9][0-9][0-9][0-9]/[1-2][0-9][0-9][0-9]'
legislative_decree_regex = r'(ν.δ.|Ν.Δ.) ([0-9]|[0-9][0-9]|[0-9][0-9][0-9])/[1-2][0-9][0-9][0-9]'
presidential_decree_regex = r'(π.δ.|Π.Δ.) ([0-9]|[0-9][0-9]|[0-9][0-9][0-9])/[1-2][0-9][0-9][0-9]'
legislative_act_regex = r'Πράξη(|ς) Νομοθετικού Περιεχομένου ([0-9]|[0-3][0-9]).[0-9][0-9].[1-2][0-9][0-9][0-9]'
date = r'(([1-9]|0[1-9]|[12][0-9]|3[01])[-/.\s+](1[1-2]|0[1-9]|[1-9]|Ιανουαρίου|Φεβρουαρίου|Μαρτίου|Απριλίου|Μαΐου|Ιουνίου|Ιουλίου|Αυγούστου|Νοεμβρίου|Δεκεμβρίου|Σεπτεμβρίου|Οκτωβρίου|Ιαν|Φεβ|Μαρ|Απρ|Μαϊ|Ιουν|Ιουλ|Αυγ|Σεπτ|Οκτ|Νοε|Δεκ)(?:[-/.\s+](1[0-9]\d\d|20[0-9][0-8]))?)'
article_regex = ['άρθρο \d+', 'άρθρου \d+']
paragraph_regex = [
    'παράγραφος \d+',
    'παραγράφου \d+',
    'παρ. \d+',
    'παράγραφος']

plural_suffixes = [
    'οι',
    'α',
    'εις',
    'οι',
    'ες'
]

class LegalEntities:
    entities = [
        law_regex,
        legislative_act_regex,
        presidential_decree_regex
    ]

    ratification =  r'(NOMOΣ|ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ|ΚΟΙΝΗ ΥΠΟΥΡΓΙΚΗ ΑΠΟΦΑΣΗ|ΝΟΜΟΘΕΤΙΚΟ ΔΙΑΤΑΓΜΑ) ΥΠ’ ΑΡΙΘ(|Μ). (\d+)'



class Numerals:

    units = {
        'πρώτ': 1,
        'δεύτερ': 2,
        'τρίτ': 3,
        'τέταρτ': 4,
        'πέμπτ': 5,
        'έκτ': 6,
        'έβδομ': 7,
        'όγδο': 8,
        'ένατ': 9
    }

    inv_units = {
        1: 'πρώτ',
        2: 'δεύτερ',
        3: 'τρίτ',
        4: 'τέταρτ',
        5: 'πέμπτ',
        6: 'έκτ',
        7: 'έβδομ',
        8: 'όγδο',
        9: 'ένατ'
    }

    tens = {
        'δέκατ': 10,
        'εικοστ': 20,
        'τριακοστ': 30,
        'τεσσαρακοστ': 40,
        'πεντηκοστ': 50,
        'εξηκοστ': 60,
        'εβδομηκοστ': 70,
        'ογδοηκοστ': 80,
        'ενενηκοστ': 90
    }

    inv_tens = {
        80: 'ογδοηκοστ',
        50: 'πεντηκοστ',
        20: 'εικοστ',
        70: 'εβδομηκοστ',
        40: 'τεσσαρακοστ',
        10: 'δέκατ',
        60: 'εξηκοστ',
        90: 'ενενηκοστ',
        30: 'τριακοστ'
    }

    hundreds = {
        'εκατοστ': 100,
        'διακοσιοστ': 200,
        'τριακοσιοστ': 300,
        'τετρακοσιοστ': 400,
        'πεντακοσιοστ': 500,
        'εξακοσιοστ': 600,
        'εφτακοσιοστ': 700,
        'επτακοστιοστ': 700,
        'οκτακοσιοστ': 800,
        'οχτακοσιοστ': 800,
        'εννιακοστιοστ': 900
    }

    inv_hundreds = {
        100: 'εκατοστ',
        200: 'διακοσιοστ',
        300: 'τριακοσιοστ',
        400: 'τετρακοσιοστ',
        500: 'πεντακοσιοστ',
        600: 'εξακοσιοστ',
        700: 'επτακοστιοστ',
        800: 'οχτακοσιοστ',
        900: 'εννιακοστιοστ'
    }

    greek_nums = {
        'α': 1,
        'β' : 2,
        'γ' : 3,
        'δ' : 4,
        'ε' : 5,
        'στ' : 6,
        'ζ' : 7,
        'η' : 8,
        'θ' : 9,
        'ι' : 10,
        'κ' : 20,
        'λ' : 30,
        'μ' : 40,
        'ν' : 50,
        'ξ' : 60,
        'ο' : 70,
        'π' : 80,
        'Ϟ' : 90,
        'ρ' : 100
    }

    @staticmethod
    def full_number_to_integer(s):
        result = 0

        for unit, val in Numerals.units.items():
            if re.search(unit, s) is not None:
                result += val
                break
        for ten, val in Numerals.tens.items():
            if re.search(ten, s) is not None:
                result += val
                break

        for hundred, val in Numerals.hundreds.items():
            if re.search(hundred, s) is not None:
                result += val
                break

        return result

    @staticmethod
    def full_numeral_to_integer_from_list(tmp, index):
        k = index - 1
        result = 0
        while k >= 0:
            print(tmp[k])
            number = Numerals.full_number_to_integer(tmp[k])
            if number == 0:
                break
            else:
                result += number
                k -= 1
        return result

    @staticmethod
    def greek_nums_to_int(s):
        r = 0
        for key, val in Numerals.greek_nums.items():
            if key in s:
                r += val

        return r

    class GreekNum:

        def __init__(self, s):
            self._s = s
            self.value = Numerals.greek_nums_to_int(s)

        @property
        def s(self):
            return self._s

        @s.getter
        def s(self):
            return self._s

        @s.setter
        def s(self, v):
            self._s = v
            self.value = Numerals.greek_nums_to_int(v)

        def __eq__(self, other):
            return self.value == other.value

        def __ne__(self, other):
            return self.value != other.value

        def __gt__(self, other):
            return self.value > other.value

        def __lt__(self, other):
            return self.value < other.value

        def __ge__(self, other):
            return self.value >= other.value

        def __le__(self, other):
            return self.value <= other.value

        def __str__(self):
            return self.s

        def __repr__(self):
            return self.s


class EditDistanceClassifier:
    """
        Classify a word to an action by a scoring a number
        of keywords. The proceedure is the following:
        Let w be our word of interest and a be an action.
        The action is also defined by some "derivatives" such as
        the same word as a verb or in other forms like genitive,
        accusative etc. each of which associated by a given weight
        (refer to Action class for more). Each action has a score
        which is the dot product of the edit_distances to its of the
        derivatives with its weight. If a the total score is smaller
        than a given threshold then we return the closest action (with
        the minimum score)
    """

    @staticmethod
    def classify_word(word, actions=actions, threshold=5):

        result = np.zeros(len(actions))
        for i, action in enumerate(actions):
            result[i] = action.score(word)
        amin = np.argmin(result)
        if result[amin] < threshold:
            return actions[amin], result[amin]
        else:
            return None, -1

    @staticmethod
    def classify_extract(extract, actions=actions):
        tmp = extract.split(' ')
        d = list(
            filter(
                lambda x: x[0] is not None, [
                    EditDistanceClassifier.classify_word(
                        w, actions) for w in tmp]))
        print(d)
        amin = 0
        for i in range(len(d)):
            if d[i][1] < d[amin][1]:
                amin = i

        print('Smallest hamming = {}, dist = {}'.format(d[amin], tmp[amin]))
