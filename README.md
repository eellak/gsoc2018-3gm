# gsoc2018-3gm

## Abstract

### Problem Statement

In the recent years plenty of attention has been gathering around analyzing public sector texts via text mining methods enabled by modern libraries, algorithms and practices and bought to to the forefront by open source projects such as textblob, spaCy, SciPy, Tensorflow and NLTK. These collaborative productive efforts seem to be a shift towards more efficient understanding of natural language by machines which can be used in conjunction with public documents in order to provide a more robust organization and codification in the legal sector.  

This proposal  aims to extend the existing Government Gazette (GG) text mining code by implementing features in order to organize and (cross)-link GG texts with legal texts and detect the signatories via heuristic and machine learning methods. This will enable elimination of bureaucratic processes and huge time savings for jurists who for example seek legal documents in the ISOKRATIS database of legal texts (which is an applicable case study).   

### Project Proposal

For this purpose, the GG documents have to be downloaded as PDFs and parse them to raw text files. Heuristic rules and Named Entity Recognition methodologies have to be applied in order to detect competent ministers and references to other legal texts which will be converted into hypertext format.

This process is either targeted in detecting amendments proposed and signed in the GG documents so that they can be incorporated within other laws or detecting similar categories of amendments and merging them under a common law, also referred as law codification. The newly “merged” / edited / codified laws could be then legislated. The project will be coded preferably in the Python programming language.   

The project is divided into main stages / milestones described below as well as their deliverables. A first metric of the evaluation of the project could be the successful categorization of laws referring to a certain category of laws (e.g. regarding mediation or new laws) and are contained in different GG articles. A second key metric would be the extension of this to a large number of law categories. Last but not least, the project can be tested with the NLP library spaCy.io which is also a proposed project through this year’s Google Summer of Code proposals by GFOSS, which can also be tested beyond the scope of this GSoC.

Through the case of analyzing, categorizing and codifying Government Gazette articles this proposal sets out to illustrate key points such as elimination of bureaucracy and efficient management of public documents for the implementation of tangible solutions enabling huge savings of time for jurists. The synergy of machine learning algorithms combined with in vitro processing of legal texts signifies the potential for broader usage of machine learning in the public sector; an area with ample amounts of unorganized data.

**Keywords:** _text mining, government gazette, machine learning, law codification_

---

## Licensing

The project is opensourced as a part of the Google Summer of Code Programme and Vision. Here, the GNU GPLv3 license is adopted. For more information see `LICENSE`. 

## Methods & Practices

### Word2Vec Models

For research purposes and further usage in the codification process a word2vec model with gensim is trained on various GG issues. That is to detect similarities between words in order to be used with syntactic analysis heuristic methods. For example the most similar words to the word "Υπουργός" (Minister) are

```python
[('Υπουργό', 0.6968967914581299), ('Υπουργού', 0.6823141574859619), ('Εσωτερικών', 0.6715962886810303), ('Αλληλεγγύης', 0.6563194990158081), ('Γραμματέας', 0.6339884996414185), ('Οικονομίας', 0.6258766651153564), ('Γενικό', 0.6158846616744995), ('Μεταφορών', 0.6002545952796936), ('Φορέας', 0.5990256071090698)]
```

which is pretty satisfying. The word vectors are also reduced in dimension using t-Stochastic Neigbor Embedding into 2D resulting in this plot (for 100 words):

![GitHub Logo](/docs/word2vec.png)


### Storing data

This project has to do with a lot of documents so selecting a NoSQL database like MongoDB would be a perfect fit for the project. The articles are organized in collections by paragraphs. It uses the `pymongo` module to communicate with the MongoDB database server. The scripts used for communication with the database as well as query building from syntactic analysis is found in the `src/database.py` module.
