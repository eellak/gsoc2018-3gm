[![Build Status](https://travis-ci.org/papachristoumarios/gsoc2018-3gm.svg?branch=master)](https://travis-ci.org/papachristoumarios/gsoc2018-3gm)
![license](https://img.shields.io/badge/license-GPL--3.0--or--later-orange.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)


# :rocket: Google Summer Of Code 2018 - 3gm

Welcome to _Government Gazette text mining, cross linking, and codification Project_ (or 3gm for short) using [Natural Language Processing Methods](https://en.wikipedia.org/wiki/Natural_language_processing) and Practices on **Greek Legislation**.

This project aims to provide with the most recent versions of each law, i.e. an automated [**codex**](https://en.wikipedia.org/wiki/Codification_(law)) via NLP methods and practices.

## Demo

The project is hosted at [3gm.ellak.gr](https://3gm.ellak.gr) or [openlaws.ellak.gr](https://openlaws.ellak.gr).

## Timeline

You can view the detailed timeline [here](https://docs.google.com/document/d/1AnbAzqE2HCsJy2q2zWHcRBvtmBbimoYIqm8AQ4bQrZA/edit?usp=sharing). What has been done during the program can be found in the [Final Progress Report](https://gist.github.com/papachristoumarios/5ccd30c191e1c7051bd364447e4e9b54).

---

## Google Summer of Code 2018

The project met and exceeded its goals for Google Summer of Code 2018. [Link](https://summerofcode.withgoogle.com/projects/#4875998630248448)

Google Summer of Code participant: Marios Papachristou ([papachristoumarios](https://github.com/papachristoumarios))

Organization: [GFOSS - Open Technologies Alliance](https://gfoss.eu/)

### Mentors

* Mentor: Diomidis Spinellis ([dsplinellis](https://github.com/dspinellis))
* Mentor: Sarantos Kapidakis
* Mentor: Alexios Zavras (zvr)

---

## Overview

- **Getting started**
  - [Home](https://github.com/eellak/gsoc2018-3gm/wiki)
  - [Installation](https://github.com/eellak/gsoc2018-3gm/wiki/Installation)
  - [Operation](https://github.com/eellak/gsoc2018-3gm/wiki/Operation)
  - [Codifier](https://github.com/eellak/gsoc2018-3gm/wiki/Codifier)
  - [Architecture](https://github.com/eellak/gsoc2018-3gm/wiki/Architecture)
  - [Final Progress Report](https://github.com/eellak/gsoc2018-3gm/wiki/Final-Report-for-Google-Summer-of-Code-2018)
- **Algorithms**
  - [Amendment Detection](https://github.com/eellak/gsoc2018-3gm/wiki/Algorithms-for-analyzing-Government-Gazette-Documents)
  - [Topic Modeling](https://github.com/eellak/gsoc2018-3gm/wiki/Topic-Modelling)
  - [Ranking](https://github.com/eellak/gsoc2018-3gm/wiki/Ranking-Laws-using-PageRank)
  - [Evaluation and Metrics](https://github.com/eellak/gsoc2018-3gm/wiki/Evaluation-and-Metrics)
- **Datasets and Continuous Integration**
  - [Fetching Documents](https://github.com/eellak/gsoc2018-3gm/wiki/Fetching-Documents)
  - [Processing Documents](https://github.com/eellak/gsoc2018-3gm/wiki/Document-Processing)
- **Documentation**
  - [API Documentation](https://github.com/eellak/gsoc2018-3gm/wiki/API-Documentation)
  - [RESTful API](https://github.com/eellak/gsoc2018-3gm/wiki/RESTful-API)
  - Help (for web application)
    - [English](https://github.com/eellak/gsoc2018-3gm/wiki/Help-(in-English))
    - [Greek](https://github.com/eellak/gsoc2018-3gm/wiki/Help-(in-Greek))
- **Development**
  - [Testing](https://github.com/eellak/gsoc2018-3gm/wiki/Testing)
  - [Licensing](https://github.com/eellak/gsoc2018-3gm/wiki/Licensing)
  - [Future Work & Contributing](https://github.com/eellak/gsoc2018-3gm/wiki/Contributing-To-The-Project)
  - [Document Embeddings](https://github.com/eellak/gsoc2018-3gm/wiki/Document-Embeddings-with-Doc2Vec)

---

## Initial Problem Statement

In the recent years plenty of attention has been gathering around analyzing public sector texts via text mining methods enabled by modern libraries, algorithms and practices and bought to to the forefront by open source projects such as textblob, spaCy, SciPy, Tensorflow and NLTK. These collaborative productive efforts seem to be a shift towards more efficient understanding of natural language by machines which can be used in conjunction with public documents in order to provide a more robust organization and codification in the legal sector.  

This proposal  aims to extend the existing Government Gazette (GG) text mining code by implementing features in order to organize and (cross)-link GG texts with legal texts and detect the signatories via heuristic and machine learning methods. This will enable elimination of bureaucratic processes and huge time savings for jurists who for example seek legal documents in legal databases.

## Initial Project Proposal

For this purpose, the GG documents have to be downloaded as PDFs and parse them to raw text files. Heuristic rules and Named Entity Recognition methodologies have to be applied in order to detect competent ministers and references to other legal texts which will be converted into hypertext format.

This process is either targeted in detecting amendments proposed and signed in the GG documents so that they can be incorporated within other laws or detecting similar categories of amendments and merging them under a common law, also referred as law codification. The newly “merged” / edited / codified laws could be then legislated. The project will be coded preferably in the Python programming language.   

The project is divided into main stages / milestones described below as well as their deliverables. A first metric of the evaluation of the project could be the successful categorization of laws referring to a certain category of laws (e.g. regarding mediation or new laws) and are contained in different GG articles. A second key metric would be the extension of this to a large number of law categories. Last but not least, the project can be tested with the NLP library spaCy which is also a proposed project through this year’s Google Summer of Code proposals by GFOSS, which can also be tested beyond the scope of this GSoC.

Through the case of analyzing, categorizing and codifying Government Gazette articles this proposal sets out to illustrate key points such as elimination of bureaucracy and efficient management of public documents for the implementation of tangible solutions enabling huge savings of time for jurists. The synergy of machine learning algorithms combined with in vitro processing of legal texts signifies the potential for broader usage of machine learning in the public sector; an area with ample amounts of unorganized data.

**Keywords:** _text mining, government gazette, machine learning, law codification_

---

## Technologies used

1. The project is written in **Python 3.x** using the following libraries: _spaCy, gensim, selenium, pdfminer.six, networkx, Flask_RESTful, Flask, pytest, numpy, pymongo, sklearn, pyocr, bs4, pillow_ and _wand_.
2. The information is stored in **MongoDB** (document-oriented database schema) and is accessible through a **RESTful API**.

---

## Project Features & Production Ready Tools

1. Document [**parser**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/pparser.py) can parse PDFs from Government Gazette Issues (see the  `data` for examples). The documents are split into articles in order to detect amendments.
2. [**Parser**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/pparser.py) for existing laws.
3. [**Named Entities**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/entities.py) for Legal Acts (e.g. Laws, Legislative Decrees etc.) encoded in regular expressions.
4. [**Similarity analyzer**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/topic_models.py) using topic models for finding Government Gazette Issues that have the same topics.
    1. We use an _unsupervised model_ to extract the topics and then group Issues by topics for **cross-linking** between Government Gazette Documents. Topic modelling is done with the [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) algorithm as illustrated in the [Wiki Page](https://github.com/eellak/gsoc2018-3gm/wiki/Topic-Modelling). The source code is located at [`3gm/topic_models.py`](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/topic_models.py).
    2. There is also a [Doc2Vec approach](https://github.com/eellak/gsoc2018-3gm/wiki/Document-Embeddings-with-Doc2Vec).
5. Documented end-2-end procedure at **[Project Wiki](https://github.com/eellak/gsoc2018-3gm/wiki)**
6. [**MongoDB**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/database.py) Integration
7. [**Fetching Tool**](https://github.com/eellak/gsoc2018-3gm/blob/master/scripts/fetcher.py) for automated fetching of documents from ET
8. Parallelized tool for [**batch conversion of documents with pdf2txt**](https://github.com/eellak/gsoc2018-3gm/blob/master/scripts/converter.py) (for newer documents) or Google Tesseract 4.0 (for performing OCR on older documents) with `pdfminer.six`, `tesseract` and `pyocr`
9. **Digitalized archive** of Government Gazette Issues from 1976 - today in [PDF](https://archive.org/details/greekgovernmentgazette) and [plaintext](https://pithos.okeanos.grnet.gr/public/7Z2GQvF0boDbCjYWFnmyc) format. Conversion of documents is done either via `pdfminer.six` or `tesseract` (for OCR on older documents).
10. [**Web application**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/app.py) written in Flask located at `3gm/app.py` hosted at [3gm.ellak.gr](http://snf-829516.vm.okeanos.grnet.gr/)
11. [**RESTful API**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/app.py) written in `flask-restful` for providing versions of the laws and
12. [**Unit tests**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/tests.py) integrated to Travis CI.
13. [**Versioning**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/database.py) system for laws with support for _checkouts_, _rollbacks_ etc. 
14. [**Ranking**](https://github.com/eellak/gsoc2018-3gm/wiki/Ranking-Laws-using-PageRank) of laws using PageRank provided by the `networkx` package. 
15. [**Summarization Module using TextRank**](https://github.com/eellak/gsoc2018-3gm/blob/master/3gm/summarize.py) for providing summaries at the search results.
16. **[Amendment Detection Algorithm](https://github.com/eellak/gsoc2018-3gm/wiki/Algorithms-for-analyzing-Government-Gazette-Documents)**. For example (taken from Greek Government Gazette):

> Μετά το άρθρο 9Α του ν. 4170/2013, που προστέθηκε με το άρθρο 3 του ν. 4474/2017, **προστίθεται** _άρθρο 9ΑΑ_, ως εξής:

Main Body / Extract

> Άρθρο 9ΑΑ

> Πεδίο εφαρμογής και προϋποθέσεις της υποχρεωτικής αυτόματης ανταλλαγής πληροφοριών όσον αφορά στην Έκθεση ανά Χώρα
1. Η Τελική Μητρική Οντότητα ενός Ομίλου Πολυεθνικής Επιχείρησης (Ομίλου ΠΕ) που έχει τη φορολογική της κατοικία στην Ελλάδα ή οποιαδήποτε άλλη Αναφέρουσα Οντότητα, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ, υποβάλλει την Έκθεση ανά Χώρα όσον αφορά το οικείο Φορολογικό Έτος Υποβολής Εκθέσεων εντός δώδεκα (12) μηνών από την τελευταία ημέρα του Φορολογικού
Έτους Υποβολής Εκθέσεων του Ομίλου ΠΕ, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ.

The above text signifies the addition of an article to an existing law. We use a combination of heuristics and NLP from the spaCy package to detect the keywords (e.g. verbs, subjects etc.):

* Detect keywords for additions, removals, replacements etc.
* Detect the subject which is in nominative in Greek. The subject is also part of some keywords such as article (άρθρο), paragraph(παράγραφος), period (εδάφιο), phrase (φράση) etc. These words have a subset relationship which means that once the algorithm finds the subject it should look up for its predecessors. So it results in a structure like this:

<p align="center">
  <img src="/docs/syntax.png"/>
</p>      

* A Python dictionary is generated:

```json
{'action': 'αντικαθίσταται', 'law': {'article': { '_id': '9AA', 'content': 'Πεδίο εφαρμογής και προϋποθέσεις της υποχρεωτικής αυτόματης ανταλλαγής πληροφοριών όσον αφορά στην Έκθεση ανά Χώρα 1. Η Τελική Μητρική Οντότητα ενός Ομίλου Πολυεθνικής Επιχείρησης (Ομίλου ΠΕ) που έχει τη φορολογική της κατοικία στην Ελλάδα ή οποιαδήποτε άλλη Αναφέρουσα Οντότητα, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ, υποβάλλει την Έκθεση ανά Χώρα όσον αφορά το οικείο Φορολογικό Έτος Υποβολής Εκθέσεων εντός δώδεκα (12) μηνών από την τελευταία ημέρα του Φορολογικού Έτους Υποβολής Εκθέσεων του Ομίλου ΠΕ, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ.'}, '_id': 'ν. 4170/2013'}, '_id': 14}
```
* And is translated to a **MongoDB operation** (in this case insertion into the database). Then the information is stored to the database.

For more information visit the [corresponding Wiki Page](https://github.com/eellak/gsoc2018-3gm/wiki/Algorithms-for-analyzing-Government-Gazette-Documents)

---

## Challenges

1. Government Gazette Issues may not always follow guidelines. 
2. Improving heuristics.
3. Gathering Information.
4. Digitizing very old articles.

---

## License

 The project is [**opensourced**](https://en.wikipedia.org/wiki/Open-source_software) as a part of the Google Summer of Code Program and Vision. Here, the GNU GPLv3 license is adopted. For more information see LICENSE.
