[![Build Status](https://travis-ci.org/papachristoumarios/gsoc2018-3gm.svg?branch=master)](https://travis-ci.org/papachristoumarios/gsoc2018-3gm)
![license](https://img.shields.io/badge/license-GPL--3.0--or--later-orange.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)



# gsoc2018-3gm

## Abstract

### Problem Statement

In the recent years plenty of attention has been gathering around analyzing public sector texts via text mining methods enabled by modern libraries, algorithms and practices and bought to to the forefront by open source projects such as textblob, spaCy, SciPy, Tensorflow and NLTK. These collaborative productive efforts seem to be a shift towards more efficient understanding of natural language by machines which can be used in conjunction with public documents in order to provide a more robust organization and codification in the legal sector.  

This proposal  aims to extend the existing Government Gazette (GG) text mining code by implementing features in order to organize and (cross)-link GG texts with legal texts and detect the signatories via heuristic and machine learning methods. This will enable elimination of bureaucratic processes and huge time savings for jurists who for example seek legal documents in the ISOKRATIS database of legal texts (which is an applicable case study).   

### Project Proposal

For this purpose, the GG documents have to be downloaded as PDFs and parse them to raw text files. Heuristic rules and Named Entity Recognition methodologies have to be applied in order to detect competent ministers and references to other legal texts which will be converted into hypertext format.

This process is either targeted in detecting amendments proposed and signed in the GG documents so that they can be incorporated within other laws or detecting similar categories of amendments and merging them under a common law, also referred as law codification. The newly “merged” / edited / codified laws coProject: Greek Government Gazette Text Mining, Cross-Linking and Codificationuld be then legislated. The project will be coded preferably in the Python programming language.   

The project is divided into main stages / milestones described below as well as their deliverables. A first metric of the evaluation of the project could be the successful categorization of laws referring to a certain category of laws (e.g. regarding mediation or new laws) and are contained in different GG articles. A second key metric would be the extension of this to a large number of law categories. Last but not least, the project can be tested with the NLP library spaCy.io which is also a proposed project through this year’s Google Summer of Code proposals by GFOSS, which can also be tested beyond the scope of this GSoC.

Through the case of analyzing, categorizing and codifying Government Gazette articles this proposal sets out to illustrate key points such as elimination of bureaucracy and efficient management of public documents for the implementation of tangible solutions enabling huge savings of time for jurists. The synergy of machine learning algorithms combined with in vitro processing of legal texts signifies the potential for broader usage of machine learning in the public sector; an area with ample amounts of unorganized data.

**Keywords:** _text mining, government gazette, machine learning, law codification_

**Timeline** You can have a look of the current timeline [here](https://docs.google.com/document/d/1AnbAzqE2HCsJy2q2zWHcRBvtmBbimoYIqm8AQ4bQrZA/edit#heading=h.jdgk2e6qwr2v)

## Google Summer of Code 2018

 * Google Summer of Code participant: Marios Papachristou

#### Mentors (alphabetically)

* Mentor: Alexios Zavras (zvr)
* Mentor: Sarantos Kapidakis
* Mentor: Diomidis Spinellis

#### Current Progress

##### Working

1. Document **parser** can parse PDFs from Government Gazette Issues (see the  `data` for examples). The documents are split into articles in order to detect ammenmends.
2. Parser for existing laws.
3. **Named Entities** for Legal Acts (e.g. Laws, Legislative Decrees etc.) encoded in regular expressions.
4. Topic models for finding Government Gazette Issues that have the same topics. We use an unsupervised model to extract the topics and then group Issues by topics for **cross-linking** between Government Gazette Documents. You can then visualize these topic models with `pyLDAvis`. Topic modelling is done with LDA and NMF algorithms as illustrated in the [Wiki Page](https://github.com/eellak/gsoc2018-3gm/wiki/Topic-Modelling). The source code is located at `src/topic_models.py`.
5. [Project Wiki](https://github.com/eellak/gsoc2018-3gm/wiki)

##### In Progress

1. Heuristic methods for detecting ammendments. For example (taken from Greek Government Gazette):

Ammendment

> Μετά το άρθρο 9Α του ν. 4170/2013, που προστέθηκε με το άρθρο 3 του ν. 4474/2017, **προστίθεται** _άρθρο 9ΑΑ_, ως εξής:

Main Body / Extract

> Άρθρο 9ΑΑ

> Πεδίο εφαρμογής και προϋποθέσεις της υποχρεωτικής αυτόματης ανταλλαγής πληροφοριών όσον αφορά στην Έκθεση ανά Χώρα
1. Η Τελική Μητρική Οντότητα ενός Ομίλου Πολυεθνικής Επιχείρησης (Ομίλου ΠΕ) που έχει τη φορολογική της κατοικία στην Ελλάδα ή οποιαδήποτε άλλη Αναφέρουσα Οντότητα, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ, υποβάλλει την Έκθεση ανά Χώρα όσον αφορά το οικείο Φορολογικό Έτος Υποβολής Εκθέσεων εντός δώδεκα (12) μηνών από την τελευταία ημέρα του Φορολογικού
Έτους Υποβολής Εκθέσεων του Ομίλου ΠΕ, σύμφωνα με το Παράρτημα ΙΙΙ Τμήμα ΙΙ.

The above text signifies the addition of an article to an existing law. We are following heuristic methods since there are no good tools for syntactic analysis for these kind of documents:

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

#### Challenges

1. Government Gazette Issues may not always follow guidelines
2. Improving heuristics
3. Gathering Information


---

## Licensing

The project is opensourced as a part of the Google Summer of Code Programme and Vision. Here, the GNU GPLv3 license is adopted. For more information see `LICENSE`.

## Methods & Practices

### Heuristic methods for detecting ammendments

This project uses heuristics for detecting ammendments. You can have a look at `src/syntax.py` module for more information.  

### Storing data

This project has to do with a lot of documents so selecting a NoSQL database like MongoDB would be a perfect fit for the project. The articles are organized in collections by paragraphs. It uses the `pymongo` module to communicate with the MongoDB database server. The scripts used for communication with the database as well as query building from syntactic analysis is found in the `src/database.py` module.

### Unit testing & Continuous Integration

This project uses the `pytest` module for running unit tests. You can install `pytest` and run the tests via:

```bash
sudo pip3 install pytest
cd ./src/
pytest tests.py
```

The tests are also run on Travis CI which is used for continuous integration in this project. The configuration file for Travis CI is `.travis.yml`.
