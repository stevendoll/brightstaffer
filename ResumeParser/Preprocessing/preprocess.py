import re
import string

from nltk import word_tokenize


def raw_resume_to_data_tri_sentences(talent_data):
    all_sentences = []
    string.punctuation = '!"#$%&()*,./:;<=>?[\]^_`{|}~'
    raw = talent_data
    raw_text = raw.split('\n')
    sentences = [sent.lower() for sent in raw_text]
    sentences += [u'', u'']

    for sent in zip(sentences[:-2], sentences[1:], sentences[2:]):
        sent_1 = re.compile('[^a-zA-Z\s]').sub('', sent[0])
        sent_2 = re.compile('[^a-zA-Z\s]').sub('', sent[1])
        sent_3 = re.compile('[^a-zA-Z\s]').sub('', sent[2])
        sent = (sent_1.translate(string.punctuation),
                sent_2.translate(string.punctuation),
                sent_3.translate(string.punctuation))
        sent = (word_tokenize(sent[0]), word_tokenize(sent[1]), word_tokenize(sent[2]))
        all_sentences.append(sent)
    return all_sentences, raw_text
