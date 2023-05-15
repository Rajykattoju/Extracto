# %%
#import necessary pacakages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
#import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#nltk.download('stopwords')
import re

# %%
#read the url file into the pandas object
df = pd.read_excel('Input.xlsx')

url_id_list = []
#loop throgh each row in the excel
for index, row in df.iterrows():
  url = row['URL']
  url_id = row['URL_ID']
  url_id_list.append(url_id)

  # make a request to url
  header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
  try:
    response = requests.get(url,headers=header)
  except:
    print("Page not found on urlId {}".format(url_id))
  #create a beautifulsoup object
  try:
    soup = BeautifulSoup(response.content, 'html.parser')
  except:
    print("Page not found on urlId {}".format(url_id))
  #extract title
  try:
    title = soup.find('h1').get_text()
  except:
    print("Title not found on urlId {}".format(url_id))
    title = ""
  #extract blog data
  try:
    articlebody = [p.get_text() for p in soup.find_all("div", {'class':'td-post-content'})]
    article = '\n'.join(articlebody)
  except:
    print("Text not found on urlId {}".format(url_id))

  #Create a dir for text files if not found
  path = "Extracted Text Files"
  if not os.path.exists(path):
    os.makedirs(path)

  #create file name with urlid
  file_name = 'Text File ' + str(url_id) + '.txt'
  
  #Write the extracted data to txt file
  with open(os.path.join(path, file_name), 'w', encoding="utf-8") as file:
    file.write(title + '\n' + article) if title!='' else 0


# %%
text_files_directory = "Extracted Text Files"
stopwords_dir = "StopWords"
master_dictionary_directory = "MasterDictionary"

# load all stop wors from the stopwords directory and store in the set variable
stop_words = set()
for files in os.listdir(stopwords_dir):
  with open(os.path.join(stopwords_dir,files),'r',encoding="ISO-8859-1") as f:
    stop_words.update(set(f.read().splitlines()))

# load all text files  from the  directory and store in a list(docs)
docs = []
for id in url_id_list:
  text_file = 'Text File ' + str(id) + '.txt'
  with open(os.path.join(text_files_directory,text_file),'r',encoding="ISO-8859-1") as f:
    text = f.read()
#tokenize the given text file
    words = word_tokenize(text)
# remove the stop words from the tokens
    filtered_text = [word for word in words if word.lower() not in stop_words]
# add each filtered tokens of each file into a list
    docs.append(filtered_text)

# store positive, Negative words from the directory
positive_words_set=set()
negitive_words_set=set()

for files in os.listdir(master_dictionary_directory):
  if files =='positive-words.txt':
    with open(os.path.join(master_dictionary_directory,files),'r',encoding="ISO-8859-1") as f:
      positive_words_set.update(f.read().splitlines())
  else:
    with open(os.path.join(master_dictionary_directory,files),'r',encoding="ISO-8859-1") as f:
      negitive_words_set.update(f.read().splitlines())

# now collect the positive  and negative words from each file
# calculate the scores from the positive and negative words 
positive_words = []
Negative_words =[]
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

#iterate through the list of docs
for i in range(len(docs)):
  positive_words.append([word for word in docs[i] if word.lower() in positive_words_set])
  Negative_words.append([word for word in docs[i] if word.lower() in negitive_words_set])
  positive_score.append(len(positive_words[i]))
  negative_score.append(len(Negative_words[i]))
  polarity_score.append((positive_score[i] - negative_score[i]) / ((positive_score[i] + negative_score[i]) + 0.000001))
  subjectivity_score.append((positive_score[i] + negative_score[i]) / ((len(docs[i])) + 0.000001))


# %%


# Average Sentence Length = the number of words / the number of sentences
# Percentage of Complex words = the number of complex words / the number of words 
# Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)

avg_sentence_length = []
Percentage_of_Complex_words  =  []
Fog_Index = []
complex_word_count =  []
avg_syllable_word_count =[]
stop_words = set(stopwords.words("english"))
def measure(file):
  if(os.stat(text_files_directory +'/'+file).st_size==0):
    return 0, 0, 0, 0, 0
  with open(os.path.join(text_files_directory, file),'r', encoding='ISO-8859-1') as f:
    text = f.read()
# remove punctuations 
    text = re.sub(r'[^\w\s.]','',text)
# split the given text file into sentences
    sentences = text.split('.')
# total number of sentences in a file
    num_sentences = len(sentences)
# total words in the file
    words = [word  for word in text.split() if word.lower() not in stop_words ]
    num_words = len(words)
 
# complex words having syllable count is greater than 2
# Complex words are words in the text that contain more than two syllables.
    complex_words = []
    for word in words:
      vowels = 'aeiou'
      syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
      if syllable_count_word > 2:
        complex_words.append(word)

# Syllable Count Per Word
# We count the number of Syllables in each word of the text by counting the vowels present in each word.
#  We also handle some exceptions like words ending with "es","ed" by not counting them as a syllable.
    syllable_count = 0
    syllable_words =[]
    for word in words:
      if word.endswith('es'):
        word = word[:-2]
      elif word.endswith('ed'):
        word = word[:-2]
      vowels = 'aeiou'
      syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
      if syllable_count_word >= 1:
        syllable_words.append(word)
        syllable_count += syllable_count_word

    avg_sentence_len = num_words / num_sentences
    avg_syllable_word_count = syllable_count / len(syllable_words)
    Percent_Complex_words  =  len(complex_words) / num_words
    Fog_Index = 0.4 * (avg_sentence_len + Percent_Complex_words)

    return avg_sentence_len, Percent_Complex_words, Fog_Index, len(complex_words),avg_syllable_word_count

# iterate through each file or doc
for f in url_id_list:
  file = 'Text File ' + str(f) + '.txt'
  x,y,z,a,b = measure(file)
  avg_sentence_length.append(x)
  Percentage_of_Complex_words.append(y)
  Fog_Index.append(z)
  complex_word_count.append(a)
  avg_syllable_word_count.append(b)


# %%
# Word Count and Average Word Length Sum of the total number of characters in each word/Total number of words
# We count the total cleaned words present in the text by 
# removing the stop words (using stopwords class of nltk package).
# removing any punctuations like ? ! , . from the word before counting.

def calculate_cleaned_words(file):
  words = []
  average_word_length = 0
  with open(os.path.join(text_files_directory,file), 'r', encoding='ISO-8859-1') as f:
    text = f.read()
    if(len(text)!=0):
      text = re.sub(r'[^\w\s]', '' , text)
      words = [word  for word in text.split() if word.lower() not in stop_words]
      length = sum(len(word) for word in words)
      average_word_length = length / len(words)
  return len(words),average_word_length

word_count = []
average_word_length = []
for f in url_id_list:
  file = 'Text File ' + str(f) + '.txt'
  x, y = calculate_cleaned_words(file)
  word_count.append(x)
  average_word_length.append(y)


# To calculate Personal Pronouns mentioned in the text, we use regex to find 
# the counts of the words - “I,” “we,” “my,” “ours,” and “us”. Special care is taken
#  so that the country name US is not included in the list.
def calculate_personal_pronouns(file):
  with open(os.path.join(text_files_directory,file), 'r', encoding='ISO-8859-1') as f:
    text = f.read()
    if(len(text)==1): return 0
    personal_pronouns = ["I", "we", "my", "ours", "us"]
    count = 0
    for pronoun in personal_pronouns:
      count += len(re.findall(r"\b" + pronoun + r"\b", text)) # \b is used to match word boundaries
  return count

personal_pronoun_count = []
for file in os.listdir(text_files_directory):
  x = calculate_personal_pronouns(file)
  personal_pronoun_count.append(x)

# %%
output_data_frame = pd.read_excel('Output Data Structure.xlsx')

# URL_ID 44 ,57, 144 does not exists i,e. page does not exist, throughs 404 error
# so we are going to drop these rows from the table
#output_data_frame.drop([44-37,57-37,144-37], axis = 0, inplace=True)

def format_values(variable_list):
  return [round(i,2) for i in variable_list]

# These are the required parameters 
variables = [positive_score,
            negative_score,
            polarity_score,
            subjectivity_score,
            avg_sentence_length,
            Percentage_of_Complex_words,
            Fog_Index,
            avg_sentence_length,
            complex_word_count,
            word_count,
            avg_syllable_word_count,
            personal_pronoun_count,
            average_word_length]

# write the values to the dataframe
for i, var in enumerate(variables):
  #check the scores by printing var for debugging
  output_data_frame.iloc[:,i+2] = format_values(var)
  #print(format_values(var))

#now save the dataframe to the disk
output_data_frame.to_csv('Output_Data.csv')


