"""
Simple Dataset Creation for 3gm
This tool permits you to create large text data-sets which can be manually 
controlled and annotated. You can use these datasets to train more accurate
spaCy models very easily. An example of a workflow to create such datasets
can be found on the 3gm wiki
Adhering to the GNU GPLv3 Licensing Terms
"""

import re
import argparse
import nltk 
nltk.download('punkt')
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/greek.pickle')
from langdetect import detect 

if __name__ == '__main__':

  
  parser = argparse.ArgumentParser(
	description='''This is a simple tool thaat creates data-sets from Greek Government Gazette corpo<a.
		For more information visit https://github.com/eellak/gsoc2018-3gm/wiki/''')
  required = parser.add_argument_group('required arguments')
  optional = parser.add_argument_group('optional arguments')
  required.add_argument(
		'-input',
		help='Corpus file from which you can create a dataset',
		required=True)
  optional.add_argument(
		'--lang',
		help='Add langage filtering. Reccomended for issue type A',
		action='store_true'
		)

  
  args = parser.parse_args()
  
  input_file =  args.input
  

  # read corpus of texts
  with open(input_file, 'r') as file:
     data = file.read().replace('\n', ' ')

  #pass by punk tokenizer for greek    
  data_set = ''.join(tokenizer.tokenize(data))
  
  #use regular expressions for data cleaning
  data_set = data_set.replace('- ', '')
  data_set = data_set.replace('− ', '')
  data_set = data_set.replace('-\n', '')
  data_set = data_set.replace('α/α   ΟΝΟΜΑΤΕΠΩΝΥΜΟ   ΟΝΟΜΑ ΠΑΤΕΡΑ   ΕΙΔΙΚΟΤΗΤΑ  ΜΗΤΡΩΟ ΑΝΘΡΩΠΙΝΟΥ ΔΥΝΑΜΙΚΟΥ   ΑΡΙΘΜ ', '')
  data_set = data_set.replace('ΕΓΓΡΑΦΗΣ ΣΤΟ   ΕΛΛΗΝΙΚΟΥ ΔΗΜΟΣΙΟΥ: ', '')
  data_set = data_set.replace(' 1  2  3  ', '')
  data_set = data_set.replace('  ', ' ')
  data_set = data_set.replace('ΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ (ΤΕΥΧΟΣ ΠΡΩΤΟ)', '')
  data_set = data_set.replace('•', '')
  
  #split sentences using regex
  sentences = re.split(r' *[\.\?!][\'"\)\]]* *', data_set)


  clean = []

  #filter sentences that do not qualify
  for item in sentences:
    if len(item)>300 and len(item)<1000 and "cid"  not in item:
      clean.append(item)

  if args.lang: 
    clean_1 = []
    for item in clean:
      if detect(item)!='en':
        clean_1.append(item)
    clean = clean_1


  temp_str = "dataset_" + input_file 
  
  #create an write the output file    
  with open(temp_str, 'w') as f:
    for item in clean:
        f.write("%s\n" % item)   
        
  print("You have created a dataset with ",len(clean), "lines")
