import os
import zipfile
import pandas as pd
import numpy as np
import re
import nltk.data
import logging
from bs4 import BeautifulSoup
from gensim.models import word2vec
from sklearn.cluster import KMeans

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

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

num_features = 750   # Word vector dimensionality
min_word_count = 5    # Minimum word count
num_workers = 4       # Number of threads to run in parallel
context = 25          # Context window size
downsampling = 1e-2   # Downsample setting for frequent words

model = word2vec.Word2Vec(sentences, workers=num_workers, \
            size=num_features, min_count = min_word_count, \
            window = context, sample = downsampling)

model.init_sims(replace=True)

# save the model for later use. You can load it later using Word2Vec.load()
# >>> from gensim.models import Word2Vec
# >>> model = Word2Vec.load("300features_40minwords_10context.w2v")
# TODO add an arg when running the script to create the model or load one and skip everything before this point
model_name = str(num_features) + 'features_' + str(min_word_count) + 'minwords_' + str(context) + 'context.w2v'
model.save(model_name)

paragraphs = []
vectors = []

print 'gathering paragraphs...'
for root, dirs, files in os.walk('.'):
    for filename in files:
        if '.xhtml' in filename:
            full_filepath = root + '/' + filename
            print 'gathering paragraphs from ' + re.sub(r'./(.*?)/.*',r'\1',root) + '\t' + filename
            print full_filepath
            soup = BeautifulSoup(open(full_filepath), 'lxml')
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('epub:switch')]
            for s in soup('p'):
                paragraph = s.get_text()
                if paragraph == '':
                    next
                else:
                        paragraphs.append(paragraph)
                        words = paragraph.split()
                        vector = np.ndarray(num_features)
                        for w in words:
                            if w in model.vocab:
                                vector = vector + model[w]
                        vectors.append(vector)
