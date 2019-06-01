[![Build Status](https://travis-ci.org/papachristoumarios/gsoc2018-3gm.svg?branch=master)](https://travis-ci.org/papachristoumarios/gsoc2018-3gm)
![license](https://img.shields.io/badge/license-GPL--3.0--or--later-orange.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)


# :rocket: Greek Government Gazette Text Mining, Cross Linking and Codification  - 3gm

  

Welcome to _Government Gazette text mining, cross linking, and codification Project_ (or 3gm for short) using [Natural Language Processing Methods](https://en.wikipedia.org/wiki/Natural_language_processing) and Practices on **Greek Legislation**.

This project aims to provide with the most recent versions of each law, i.e. an automated [**codex**](https://en.wikipedia.org/wiki/Codification_(law)) via NLP methods and practices.

## About the project

We live in a complex regulatory environment. As citizens, we obey government regulations from many authorities. As members of organized societies and groups, we must obey organizational policies and rules. As social beings, we are bound by conventions we make with others. As individuals, they are bound by personal rules of conduct. The full number and size of regulations can be really scary. We can agree on some general principles but, at the same time, we can disagree on how these principles apply to specific situations. In order to minimize such disagreements, regulators are often obliged to create numerous regulations or very large regulations to deal with special cases.

In the recent years plenty of attention has been gathering around analyzing public sector texts via text mining methods enabled by modern libraries, algorithms and practices and bought to to the forefront by open source projects such as textblob, spaCy, SciPy, Tensorflow and NLTK. These collaborative productive efforts seem to be a shift towards more efficient understanding of natural language by machines which can be used in conjunction with public documents in order to provide useful tools for legislators. This emerging sector is usually referred as "Computational Law".

This project, developed under the auspices the Google Summer of Code 2018 Program, carries out the extraction of [**Government Gazette (ΦΕΚ)**](https://archive.org/details/greekgovernmentgazette) texts from the [**National Printing House (ET)**](http://www.et.gr/), cross-links them with each other and, finally, identifies and applies the amendments to the legal text by providing automatic codification of the Greek legislation using methods and techniques of Natural Language Processing. This will allow the elimination of bureaucratic procedures and great time savings for lawyers looking for the most recent versions of statutes in legal databases. The detection of amendments is automated in order to amend the amendments to the laws merged into a common law, a procedure known as codification of the law. The new "merged" / modified / codified laws can show the current text of a law at every moment. This is something that is being traditionally done by hand and our aim was to automate it.

Finally, the laws are clustered into topics according to their content using a non-supervised machine learning model (Latent Dirichlet Allocation) to provide a more holistic representation of Greek legislation. Also, for easier indexing, PageRank was used and therefore the interconnections of the laws were positively taken into account, because the more references there is a legislative text than the other the more important it is characterized.

Through the analysis, categorization and codification of the GG documents, this project facilitates key elements of everyday life such as the elimination of bureaucracy and the efficient management of public documents to implement tangible solutions, which allows huge savings for lawyers and citizens.

A presentation of the project is [available here as part of FOSSCOMM 2018 at the University of Crete](https://docs.google.com/presentation/d/1S5nSSr1uFo4FXLPnCw-qQckVaxN-8Vd5rIbUcv9-FNE/edit?usp=sharing)

## Demo

The project is hosted at [3gm.ellak.gr](https://3gm.ellak.gr) or [openlaws.ellak.gr](https://openlaws.ellak.gr).  A video presentation of the project is available [here](https://www.youtube.com/watch?v=_UIGsy85Ehw).

## Timeline

You can view the detailed timeline [here](https://docs.google.com/document/d/1AnbAzqE2HCsJy2q2zWHcRBvtmBbimoYIqm8AQ4bQrZA/edit?usp=sharing). What has been done during the program can be found in the [Final Progress Report](https://gist.github.com/papachristoumarios/5ccd30c191e1c7051bd364447e4e9b54).

---

## Google Summer of Code 2019

This repository will host the changes and code developped for 3gm as part of the Google Summer of Code 2019. This year's effort mainly aims to enhence NLP functionalities of the project and is based on this [project proposal](https://docs.google.com/document/d/1KT14HmJBIOsKgLSfm4iBz79PCH1G2LUxbNVDINGr_2o/edit?usp=sharing). The timeline of the project is described [here](https://docs.google.com/document/d/1mr633dCmdtp3bLqRKWygj7VoQ_enh-qHvqHgYysRhjM/edit?usp=sharing) and you can also find a [worklog](https://docs.google.com/document/d/1wPAsp_DKi8Xls54dusn0rQQcFnnREFRTKvJsYco4s1k/edit?usp=sharing) documenting the progress made during the development of the project.   

The main goals for GSoC-2019 are populating the database with more types of amendments, widening the range of feature extraction and training a new Doc2Vec model and a new NER annotator specifically for our corpus.

As part of the first week of GSoC-2019 a data mirgation project. In the scope of this project we had to mine the webite of
the [Greek National Printing House](http://www.et.gr/idocs-nph/search/fekForm.html#results) and upload as many GGG issues to the respective [Internet Archive Collection](https://archive.org/details/greekgovernmentgazette). Until now, 66.000 files have been uploaded, in addition to the ~45.000 files that the collection contained initially. This number will continue to surge.

We tried documenting our insights from this process. We would like to evolve this to an entry at the project wiki, titled [" A simple guide to mining the Greek Government Gazette"](https://docs.google.com/document/d/1pcCmRKKRClTmOD1HQav2GRlkM0mLZUgGmIv83HX4wv0/edit?usp=sharing).  

## Google Summer of Code 2018

The project met and exceeded its goals for Google Summer of Code 2018. [Link](https://summerofcode.withgoogle.com/projects/#4875998630248448)

Google Summer of Code participant: Marios Papachristou ([papachristoumarios](https://github.com/papachristoumarios))

Organization: [GFOSS - Open Technologies Alliance](https://gfoss.eu/)

---

## Contibutors

### Mentors for GSOC 2019

* Mentor: Marios Papachristou ([papachristoumarios](https://github.com/papachristoumarios))
* Mentor: Diomidis Spinellis ([dsplinellis](https://github.com/dspinellis))
* Mentor: Ioannis Anagnostopoulos
* Mentor: Panos Louridas ([louridas](https://github.com/louridas))

### Mentors for GSOC 2018

* Mentor: Diomidis Spinellis ([dsplinellis](https://github.com/dspinellis))
* Mentor: Sarantos Kapidakis
* Mentor: Marios Papachristou ([papachristoumarios](https://github.com/papachristoumarios))

### Development

 * Marios Papachristou (Original Developer - Google Summer of Code 2018)
 * Theodore Papadopoulos (AngularJS UI)
 * Sotirios Papadiamantis (Google Summer of Code 2019)
 

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

## Technologies used

1. The project is written in **Python 3.x** using the following libraries: _spaCy, gensim, selenium, pdfminer.six, networkx, Flask_RESTful, Flask, pytest, numpy, pymongo, sklearn, pyocr, bs4, pillow_ and _wand_.
2. The information is stored in **MongoDB** (document-oriented database schema) and is accessible through a **RESTful API**.
3. The UI is based on angular 7 

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

## Mailing List

Development Mailing List: 3gm-dev@googlegroups.com

## License

 The project is [**opensourced**](https://en.wikipedia.org/wiki/Open-source_software) as a part of the Google Summer of Code Program and Vision. Here, the GNU GPLv3 license is adopted. For more information see LICENSE.
