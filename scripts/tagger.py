from entities import *
import parser
import codifier
import tokenizer
import helpers
import syntax
import os
import sys
sys.path.insert(0, '../3gm')

if __name__ == '__main__':
    counter = 0
    cod = codifier.LawCodifier(sys.argv[1])
    f = open(sys.argv[2], 'w+')
    cod.codify_new_laws()
    for identifier, law in cod.laws.items():
        for article in law.sentences:
            print(article)
            for s in law.get_paragraphs(article):
                global actions
                global whats
                trees = []
                try:
                    extracts, non_extracts = helpers.get_extracts(s)
                except:
                    counter += 1
                    continue
                non_extracts = ' '.join(non_extracts)
                non_extracts = tokenizer.tokenizer.split(
                    non_extracts, delimiter='. ')

                for non_extract in non_extracts:
                    tmp = list(map(lambda s: s.strip(
                        string.punctuation),  non_extract.split(' ')))

                    for action in actions:
                        for i, w in enumerate(tmp):
                            if action == w:
                                f.write(non_extract + '\n')
                                print('woo')
    f.close()
    print('Unmatched Brackets: ', counter)
