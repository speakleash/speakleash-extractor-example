import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.robotparser
import os
from lm_dataformat import Archive
import shutil
import spacy
import json
import glob
from urllib.parse import urljoin
import time
import sys

def get_word_stats(txt):
    if not txt:
        return 0, 0, 0, 0, 0, 0

    sentences = 0
    words = 0
    verbs = 0
    nouns = 0
    punctuations = 0
    symbols = 0

    doc = nlp(txt)

    sentences = len(list(doc.sents))
    words = len([token.text for token in doc if not token.is_punct])
    nouns = len([token.text for token in doc if (not token.is_stop and not token.is_punct and token.pos_ == "NOUN")])
    verbs = len([token.text for token in doc if (not token.is_stop and not token.is_punct and token.pos_ == "VERB")])
    punctuations = len([token.text for token in doc if (token.is_punct or token.pos_ == "PUNCT")])
    symbols = len([token.text for token in doc if (token.pos_ == "SYM")])

    return sentences, words, verbs, nouns, punctuations, symbols

def download_file(url):

    ok = False
    txt = ""

    while not ok:
        try:
            txt = requests.get(url, timeout=5).content.decode('utf-8')
            ok = True
            
        except Exception as e:
            time.sleep(10)
            print(e)
            pass

    return ok, txt


rp = urllib.robotparser.RobotFileParser()
rp.set_url('https://clarin-pl.eu/robots.txt')
rp.read()
url = 'https://clarin-pl.eu/dspace/handle/11321/312'
urls = []

if rp.can_fetch('*', url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        urls  = [urljoin(url, node.get('href')) for node in soup.find_all('a', class_='label label-info')
                if node.get('href').endswith('isAllowed=y')]
else:
    print("Cannot access the website")
    sys.exti(1)


ar = Archive('./data')

file_name_zst = './1000_novels_corpus_CLARIN-PL.jsonl.zst'
file_name_manifest = './1000_novels_corpus_CLARIN-PL.manifest'
nlp = spacy.load("pl_core_news_md")

total_len = 0
total_docs = 0
total_sentences = 0
total_words = 0
total_verbs = 0
total_nouns = 0
total_punctuations = 0
total_symbols = 0

for idx, url_txt in enumerate(tqdm(urls, total=len(urls))):
    if rp.can_fetch('*', url_txt):
        ok, txt = download_file(url_txt)
        if ok:
            l = len(txt)
            if l > 100000:
                nlp.max_length = len(txt) + 100
            sentences, words, verbs, nouns, punctuations, symbols = get_word_stats(txt.strip())
            total_words += words
            total_verbs += verbs
            total_nouns += nouns
            total_len += l
            total_docs += 1
            total_sentences += sentences
            total_punctuations += punctuations
            total_symbols += symbols
            meta = {'url' : url_txt, 'length': l, 'sentences': sentences, 'words': words, 'verbs': verbs, 'nouns': nouns, 'punctuations': punctuations, 'symbols': symbols}
            ar.add_data(txt.strip(), meta = meta)


ar.commit()

data_files= glob.glob('./data/*')
file_size = 0

for f in data_files:
    if f.endswith('.zst'):
        shutil.copy(f, os.path.join(file_name_zst))
        file_size = os.path.getsize(file_name_zst)

    os.remove(f)

manifest = {"project" : "SpeakLeash", "name": "1000_novels_corpus_CLARIN-PL", "description": "1000 Novels Corpus, CLARIN-PL ", "license": "Creative Commons - Attribution 4.0 International (CC BY 4.0)", "language": "pl", "file_size" : file_size, "sources": [{"name": "1000_novels_corpus_CLARIN-PL", "url": "https://clarin-pl.eu/dspace/handle/11321/312", "license": "Creative Commons - Attribution 4.0 International (CC BY 4.0)"}], "stats": {"documents": total_docs, "sentences": total_sentences, "words" : total_words, "nouns" : total_nouns, "verbs" : total_verbs, "characters": total_len, "punctuations" : total_punctuations, "symbols" : total_symbols}}
json_manifest = json.dumps(manifest, indent = 4) 

with open(file_name_manifest, 'w') as mf:
    mf.write(json_manifest)

