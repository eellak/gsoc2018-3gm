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
 
Keywords: text mining, government gazette, machine learning, law codification 
