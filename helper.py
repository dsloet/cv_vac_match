try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile

import numpy as np
import heapq
import os, random, shutil
import dash_html_components as html
import base64
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

from config import UPLOAD_DIRECTORY, PARA, TEXT, S3_BUCKET, S3_KEY, S3_SECRET

from urllib.parse import quote as urlquote

nltk.download('punkt')


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def generate_unique_path():
    """Generate a unique path"""
    random_folder = randomString()
    path = os.path.join(UPLOAD_DIRECTORY + '/' + random_folder)
    os.makedirs(path)
    return path

def upload_to_s3(path, file):
    session = boto3.Session(
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    )
    s3 = session.resource('s3')
    s3.meta.client.upload_file(Filename=path, Bucket=S3_BUCKET, Key=file)

def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return('\n\n'.join(paragraphs))

def save_file(name, content, UPLOAD_DIRECTORY = UPLOAD_DIRECTORY):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files(UPLOAD_DIRECTORY=UPLOAD_DIRECTORY):
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)

def remove_files(UPLOAD_DIRECTORY):
    
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        os.remove(path)

def remove_directory(UPLOAD_DIRECTORY):
    try:
        shutil.rmtree(UPLOAD_DIRECTORY)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
 

def get_file_names(UPLOAD_DIRECTORY):
    doc_names = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        doc_names.append(os.path.join(UPLOAD_DIRECTORY, filename))
    return doc_names



stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
dutch_stop_words = open('dutch_stopwords.txt').read().split() + list(string.punctuation)

def stem_tokens(tokens):
    #return(tokens) 
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words=dutch_stop_words)

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


def generate_summary(text, max_sentences = 5):
    
    # Word frequency list
    word_frequencies = {}  
    for word in nltk.word_tokenize(text):  
        if word not in dutch_stop_words:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    # Maximum frequency
    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
    maximum_frequency
    
    # Create sentences list
    sentence_list = nltk.sent_tokenize(text)
    
    # Create summary of text
    
    sentence_scores = {}
    word_count = 0
    for sent in sentence_list:
        
        #print(sent)
        for word in nltk.word_tokenize(sent.lower()):
            word_count += 1
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
        summary_sentences = heapq.nlargest(max_sentences, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
    sentence_count = np.count_nonzero(sentence_list)
    return(word_frequencies, summary, sentence_scores, sentence_count, word_count)


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )