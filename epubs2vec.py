import os
import zipfile
import re
files = os.listdir('.')

epubs = [x for x in files if '.epub' in x]

for epub in epubs:
    bookid = re.sub(r'(.*).epub',r'\1',epub)
    print 'extracting ' + bookid + '...'
    with zipfile.ZipFile(epub,'r') as z:
        z.extractall('./temp/' + str(bookid))
