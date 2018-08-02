# Produce summaries of laws from law titles using
# TextRank algorithm provided by gensim

from gensim.summarization import summarize
import codifier
import multiprocessing
import database
db = database.Database()

# Filtering Heuristic
MAX_TITLE_WORDS = 20

# Summarization job
def job(identifier):
    global db
    try:
        l = codifier.codifier.laws[identifier]
        titles = filter(lambda x: len(x.split()) <= MAX_TITLE_WORDS, [x.lstrip().rstrip().strip('.') for x in l.titles.values()])
        titles = '. '.join(titles)
        summary = summarize(titles, ratio=0.1)
        summary_obj = {
            '_id' : identifier,
            'summary' : summary
        }
        db.summaries.save(summary_obj)
    except:
        pass

if __name__ == '__main__':
    workers = multiprocessing.cpu_count() - 1
    pool = multiprocessing.Pool(workers)
    identifiers = list(codifier.codifier.laws.keys())
    pool.map(job, identifiers)
