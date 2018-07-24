[![Build Status](https://travis-ci.org/papachristoumarios/gsoc2018-3gm.svg?branch=master)](https://travis-ci.org/papachristoumarios/gsoc2018-3gm)
![license](https://img.shields.io/badge/license-GPL--3.0--or--later-orange.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)


# gsoc2018-3gm

Welcome to _Government Gazette text mining, cross linking, and codification Project_ (or 3gm for short) using Natural Language Processing Methods and Practices.
This project aims to provide with the most recent versions of each law (codex).
The project is hosted at [3gm.ellak.gr](https://3gm.ellak.gr) and [openlaws.ellak.gr](https://openlaws.ellak.gr)

### Google Summer of Code 2018

 * Google Summer of Code participant: Marios Papachristou

#### Mentors (alphabetically)

* Mentor: Alexios Zavras (zvr)
* Mentor: Sarantos Kapidakis
* Mentor: Diomidis Spinellis ([dsplinellis](https://github.com/dspinellis))

---

## Installation & Usage

1. [Installation Instructions](https://github.com/eellak/gsoc2018-3gm/wiki/Installation)
2. [Fetching Documents](https://github.com/eellak/gsoc2018-3gm/wiki/Fetching-Documents)
3. [Codifying Laws](https://github.com/eellak/gsoc2018-3gm/wiki/Codifier)

For a tutorial on getting started click [here](https://github.com/eellak/gsoc2018-3gm/wiki/Tutorial)


#### Current Progress

##### Working

1. Document **parser** can parse PDFs from Government Gazette Issues (see the  `data` for examples). The documents are split into articles in order to detect amendments.
2. **Parser** for existing laws.
3. **Named Entities** for Legal Acts (e.g. Laws, Legislative Decrees etc.) encoded in regular expressions.
4. **Similarity analyzer** using topic models for finding Government Gazette Issues that have the same topics.
    1. We use an _unsupervised model_ to extract the topics and then group Issues by topics for **cross-linking** between Government Gazette Documents. Topic modelling is done with the [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) algorithm as illustrated in the [Wiki Page](https://github.com/eellak/gsoc2018-3gm/wiki/Topic-Modelling). The source code is located at `3gm/topic_models.py`.
    2. There is also a [Doc2Vec approach](https://github.com/eellak/gsoc2018-3gm/wiki/Document-Embeddings-with-Doc2Vec).
5. Documented end-2-end procedure at [Project Wiki](https://github.com/eellak/gsoc2018-3gm/wiki)
6. **MongoDB** Integration
7. **Fetching Tool** for automated fetching of documents from ET
8. Parallelized tool for **batch conversion of documents with pdf2txt** (for newer documents) or Google Tesseract 4.0 (for performing OCR on older documents)
9. **Digitalized archive** of Government Gazette Issues from 1976 - today in [PDF](https://archive.org/details/GreekGovernmentGazette) and [plaintext](https://pithos.okeanos.grnet.gr/public/7Z2GQvF0boDbCjYWFnmyc) format. Conversion of documents is done either via `pdfminer.six` or `tesseract` (for OCR on older documents).
10. **Web application** written in Flask located at `3gm/app.py`
11. **RESTful API** written in `flask-restful` for providing versions of the laws and
12. Unit tests



##### In Progress

1. Heuristic methods for detecting amendments. For example (taken from Greek Government Gazette):

Amendment

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

```
{'action': 'αντικαθίσταται', 'law': {'article': { '_id': '9AA', 'content': 'Πεδίο εφαρμογής και προϋποθέσεις της υποχρεωτικής αυτόματης ανταλλαγής πληροφοριών όσον αφορά στην Έκθεση ανά Χώρα
1. Η Τελική Μητρική Οντότητα ενός Ομίλου Πολυεθνικής Επιχείρησης (Ομίλου ΠΕ) που έχει τη φορολογική της κατοικία στην Ελλάδα ή οποιαδήποτε άλλη Αναφέρουσα Οντότητα, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ, υποβάλλει την Έκθεση ανά Χώρα όσον αφορά το οικείο Φορολογικό Έτος Υποβολής Εκθέσεων εντός δώδεκα (12) μηνών από την τελευταία ημέρα του Φορολογικού
Έτους Υποβολής Εκθέσεων του Ομίλου ΠΕ, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ.'}, '_id': 'ν. 4170/2013'}, '_id': 14}
```
* And is translated to a MongoDB operation (in this case insertion into the database). Then the information is stored to the database.

For more information visit the [corresponding Wiki Page](https://github.com/eellak/gsoc2018-3gm/wiki/Algorithms-for-analyzing-Government-Gazette-Documents)

#### Challenges

1. Government Gazette Issues may not always follow guidelines
2. Improving heuristics
3. Gathering Information
