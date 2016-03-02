import os
import zipfile
import pandas as pd
import numpy as np
import re
import nltk.data
from bs4 import BeautifulSoup
files = os.listdir('.')

epubs = [x for x in files if '.epub' in x]

for epub in epubs:
    bookid = re.sub(r'(.*).epub',r'\1',epub)
    print 'extracting ' + bookid + '...'
    with zipfile.ZipFile(epub,'r') as z:
        z.extractall('./temp/' + str(bookid))

bookids = []
filenames = []
chapters = []

print 'gathering xhtml files...'
for root, dirs, files in os.walk('.'):
    for filename in files:
        if '.xhtml' in filename:
            full_filepath = root + '/' + filename
            bookids.append(re.sub(r'./(.*?)/.*',r'\1',root))
            filenames.append(filename)
            print 'gathering text from ' + re.sub(r'./(.*?)/.*',r'\1',root) + '\t' + filename
            soup = BeautifulSoup(open(full_filepath), 'lxml')
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('epub:switch')]
            filetext = soup.find('body').get_text()
            chapters.append(filetext)

df = pd.DataFrame({'bookids':bookids,'filenames':filenames,'chapters':chapters},columns=['bookids','filenames','chapters'])

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def chapter_to_wordlist(chapter):
    chapter = re.sub("[^a-zA-Z]"," ", chapter)
    chapter_words = chapter.lower().split()
    return(chapter_words)

def chapter_to_sentences( chapter, tokenizer):
    raw_sentences = tokenizer.tokenize(chapter.strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append( chapter_to_wordlist( raw_sentence))
    return sentences

sentences = []

for chapter in df['chapters']:
    sentences += chapter_to_sentences(chapter, tokenizer)

