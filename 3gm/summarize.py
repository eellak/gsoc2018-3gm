# Produce summaries of laws from law titles using
# TextRank algorithm provided by gensim

from gensim.summarization import summarize as summarize_textrank
import codifier
import multiprocessing
import database
import string
import logging
db = database.Database()

# Filtering Heuristic
MAX_TITLE_WORDS = 20

# Summarization job


def job(identifier):
    global db
    punct = str.maketrans('', '', string.punctuation)
    try:
        l = codifier.codifier.laws[identifier]
        titles = filter(lambda x: len(x.split()) <= MAX_TITLE_WORDS,
                        [x.lstrip().rstrip().translate(punct) for x in l.titles.values()])
        titles = filter(lambda x: x.rstrip() != '', titles)
        titles = '. '.join(titles)
        summary = summarize_textrank(titles, ratio=0.1)
    except BaseException as e:
        logging.warning(str(e))

    finally:
        summary_obj = {
            '_id': identifier,
            'summary': summary
        }
        db.summaries.save(summary_obj)

# Summarize


def summarize(identifiers=[]):
    workers = multiprocessing.cpu_count() - 1
    pool = multiprocessing.Pool(workers)
    if identifiers == []:
        identifiers = list(codifier.codifier.laws.keys())
    print(identifiers)
    pool.map(job, identifiers)


if __name__ == '__main__':
    summarize()
