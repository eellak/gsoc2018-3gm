[![Build Status](https://travis-ci.org/papachristoumarios/gsoc2018-3gm.svg?branch=master)](https://travis-ci.org/papachristoumarios/gsoc2018-3gm)
![license](https://img.shields.io/badge/license-GPL--3.0--or--later-orange.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)



# gsoc2018-3gm

## Installation & Usage

1. [Installation Instructions](https://github.com/eellak/gsoc2018-3gm/wiki/Installation)
2. [Fetching Documents](https://github.com/eellak/gsoc2018-3gm/wiki/Fetching-Documents)
3. [Codifying Laws](https://github.com/eellak/gsoc2018-3gm/wiki/Codifier) (Work in phttps://github.com/eellak/gsoc2018-3gm/wiki/Fetching-Documentsrogress)



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
6. Optionally trained Word2Vec Model for further usage
7. MongoDB Integration

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



