import pytest
import tokenizer
import re
import entities

def replace_phrase(
        s,
        old_phrase,
        new_phrase):
    """Replacement of phrase inside document
    :old_phrase phrase to be replaced
    :new_phrase new phrase
    :article optional detect phrase in certain article
    :paragraph optional detect phrase in certain paragraph
    """

    joined = '. '.join(s)
    joined = re.sub(old_phrase, new_phrase, joined)
    splitted = tokenizer.tokenizer.split(joined, delimiter='. ')

    return splitted

def remove_phrase(s, old_phrase):
    return replace_phrase(s, old_phrase, '')

def insert_phrase(
        s,
        new_phrase,
        position='append',
        old_phrase=''):

    """Phrase insertion with respect to another phrase"""

    joined = '. '.join(s)

    if position == 'prepend':
        joined = new_phrase + ' ' + joined
    elif position == 'append':
        joined = joined + ' ' + new_phrase
    elif position in ['before', 'after']:
        assert(old_phrase != '')
        if position == 'before':
            rep = new_phrase + ' ' + old_phrase
        elif position == 'after':
            rep = old_phrase + ' ' + new_phrase
        else:
            raise Exception('Not a valid position')
        q = replace_phrase(s, old_phrase, rep)
        joined = '. '.join(q)

    splitted = tokenizer.tokenizer.split(joined, delimiter='. ')

    return splitted

def get_cases(s):
    cases = []
    for i, x in enumerate(s):
        if 1 <= len(x) <= 4:
            try:
                n = entities.Numerals.GreekNum(x)
                cases.append((i, n, n.value))
            except:
                pass
    if cases != []:
        if cases[0][2] != 1:
            n = entities.Numerals.GreekNum('α')
            cases.insert(0, (0, n, n.value))

    return cases


def test_phrase():
    import codifier

    law = codifier.codifier.laws['ν. 4511/2018']
    test =  law.sentences['1']['1']

    test1 = replace_phrase(test, 'επίδοσής της στο αντίδικο μέρος', 'foo')
    tmp = '. '.join(test1)
    assert('επίδοσής της στο αντίδικο μέρος' not in tmp and 'foo' in tmp)

    test2 = remove_phrase(test1, 'foo')
    assert('foo' not in '. '.join(test2))

    test3 = insert_phrase(test1, 'appended')
    assert(test3[-1].endswith('appended'))

    test4 = insert_phrase(test1, 'prepended', position='prepend')
    assert(test4[0].startswith('prepended'))

    test5 = insert_phrase(test1, 'boo', position='before', old_phrase='foo')
    tmp = '. '.join(test5)
    assert('boo foo' in tmp)

    test6 = insert_phrase(test1, 'boo', position='after', old_phrase='foo')
    tmp = '. '.join(test6)
    assert('foo boo' in tmp)

    test7 = law.insert_phrase('boo', position='before', old_phrase='επίδοσής της στο αντίδικο μέρος', article='1', paragraph='1')
    import pprint
    pprint.pprint(test7)

if __name__ == '__main__':
    test_phrase()
