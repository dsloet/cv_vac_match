import os

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
MAX_SENTENCES = 10

cwd = os.getcwd()
UPLOAD_DIRECTORY = cwd + '/uploads'