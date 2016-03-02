import os
import zipfile
import re
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
