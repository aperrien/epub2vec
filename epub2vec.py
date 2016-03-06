import os
import zipfile
import pandas as pd
import numpy as np
import re
import nltk.data
import csv
import logging
import time
from bs4 import BeautifulSoup
from gensim.models import word2vec
from sklearn.cluster import KMeans

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

start_time = time.time()
print 'started at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(start_time))

files = os.listdir('epub-input/')

epubs = [x for x in files if '.epub' in x]
epubids = []

for epub in epubs:
    bookid = re.sub(r'(.*).epub',r'\1',epub)
    epubids.append(bookid)
    # print 'extracting ' + bookid + '...'
    with zipfile.ZipFile('epub-input/' + str(epub),'r') as z:
        z.extractall('./www/epub-output/' + str(bookid))

log_time = time.time()
print 'books extracted at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))

bookids = []
filenames = []
chapters = []

print 'gathering xhtml or html files...'
for root, dirs, files in os.walk('.'):
    for filename in files:
        if '.xhtml' in filename or '.html' in filename:
            full_filepath = root + '/' + filename
            bookid = re.sub(r'.*/epub-output/(.*?)/.*',r'\1',root)
            print bookid
            if bookid in epubids:
                bookids.append(bookid)
                filenames.append(filename)
                # print 'gathering text from ' + bookid + '\t' + filename
                soup = BeautifulSoup(open(full_filepath), 'lxml')
                [s.extract() for s in soup('script')]
                [s.extract() for s in soup('epub:switch')]
                filetext = soup.find('body').get_text()
                chapters.append(filetext)
            else:
                # print 'skipping files for ' + str(bookid) + ' from old run'

log_time = time.time()
print 'chapters extracted at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))

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

log_time = time.time()
print 'sentences extracted at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))

num_features = 750   # Word vector dimensionality
min_word_count = 10    # Minimum word count
num_workers = 6       # Number of threads to run in parallel
context = 20          # Context window size
downsampling = 1e-3   # Downsample setting for frequent words

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

log_time = time.time()
print 'word2vec model saved at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))

paragraphs = []
vectors = []
locations = []
p_bookids = []

print 'gathering paragraphs...'
for root, dirs, files in os.walk('.'):
    for filename in files:
        if '.xhtml' in filename:
            full_filepath = root + '/' + filename
            # print 'gathering paragraphs from ' + re.sub(r'./temp/(.*?)/.*',r'\1',root) + '\t' + filename
            soup = BeautifulSoup(open(full_filepath), 'lxml')
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('epub:switch')]
            for s in soup('p'):
                paragraph = s.get_text()
                if paragraph == '':
                    next
                else:
                    location_id = s.parent.get('id')
                    if location_id is None:
                        location_id = s.parent.parent.get('id')
                    if location_id is None:
                        next
                    else:
                        location = filename + '#' + str(location_id)
                        locations.append(location)
                        p_bookids.append(re.sub(r'./temp/(.*?)/.*',r'\1',root))
                        paragraphs.append(paragraph)
                        words = paragraph.split()
                        vector = np.zeros(num_features,dtype=float)
                        in_model_count = 0
                        for w in words:
                            if w in model.vocab:
                                in_model_count += 1
                                vector = vector + model[w]
                        if in_model_count > 0:
                            average_vector = vector / in_model_count
                        else:
                            average_vector = vector
                        vectors.append(average_vector)

num_paragraphs = len(paragraphs)

log_time = time.time()
print str(num_paragraphs) + ' paragraph vectors computed at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))

# Set "k" (num_clusters) to be 1/21th of the number of paragraph vectors, or an
# average of 20 "similar paragraphs" per paragraph
p_vectors = np.array(vectors)
num_clusters = num_paragraphs / 21

kmeans_clustering = KMeans( n_clusters = num_clusters, n_jobs = -1 )
cluster_indices = kmeans_clustering.fit_predict( p_vectors )

log_time = time.time()
print 'k-means clustering complete at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(log_time))


with open('cluster_output.csv', 'w') as cluster_output:
    fieldnames = ['cluster_id','book', 'location', 'text']
    writer = csv.DictWriter(cluster_output, fieldnames=fieldnames)
    writer.writeheader()

    # Print out some clusters!
    for cluster in range(0,num_clusters):
        p_indices = []
        for i in range(0,num_paragraphs):
            if( cluster_indices[i] == cluster ):
                p_indices.append(i)

        # print 'Outputting cluster %d' % cluster + ' - ' + str(len(p_indices)) + ' paragraphs.'

        for p_index in p_indices:
            writer.writerow({'cluster_id':cluster,'book': p_bookids[p_index], 'location': locations[p_index], 'text':paragraphs[p_index].encode('utf-8')})

end_time = time.time()
print 'finished outputting csv at: ' + time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(end_time))
print 'total time elapsed: ' + str(end_time - start_time) + ' seconds.'
