import re
import string

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from ResumeParser.Ngram.Ngram import create_ngram
from ResumeParser.conf.parameters import *

nltk.data.path.append('/Users/jademaddy/Desktop/brightstaffer/ResumeParser/nltk_data')


class Resume:
    def __init__(self, *args, **kwargs):
        self.education = []
        self.skills = []
        self.work = []
        self.additional = []
        self.model_type = kwargs['word_model']

    def __get_education__(self):
        return self.education

    def __get_skills__(self):
        return self.skills

    def __get_work__(self):
        return self.work

    def __get_other__(self):
        return self.additional

    def get_templatized_resume(self):
        resume = {}
        resume['education'] = self.__get_education__()
        resume['skills'] = self.__get_skills__()
        resume['work-experience'] = self.__get_work__()
        resume['additional-info'] = self.__get_other__()
        return resume


def raw_resume_to_data(resumetext):
    all_sents = []
    original_sents = []
    string.punctuation = '!"#$%&()*,./:;<=>?[\]^_`{|}~'
    raw = resumetext
    text = (raw.lower()).decode('utf-8')
    raw_text = sent_tokenize(raw.decode('utf-8'))
    sents = sent_tokenize(text)
    # raw_text = raw.split('\n')
    # sents = text.split('\
    for sent in sents:
        sent = re.compile('[^a-zA-Z\s]').sub('', sent)
        all_sents.append(
            word_tokenize(
                sent.translate(string.punctuation)))
    return all_sents, raw_text


def get_word2vec_vector(sent, model, model_type):
    """

    :param sent:
    :param model:
    :return:
    """
    if model_type == "doc2vec":
        return model.infer_vector(sent)

    stop = set(nltk.corpus.stopwords.words('english'))
    sent_vector = []
    for j, word in enumerate(sent):
        word = WordNetLemmatizer().lemmatize(word)
        if word in model.wv.vocab and word not in stop:
            if len(sent_vector) == 0:
                sent_vector = np.array(model[word])
            else:
                sent_vector += np.array(model[word])

    return sent_vector


def build_resume(all_sents, original, word2vec_model, classifier_model, model_type):
    """

    :param all_sents:
    :param word2vec_model:
    :param classifier_model:
    :return:
    """
    resume = Resume(word_model=model_type)
    for i, sent in enumerate(all_sents):
        sent_vector = get_word2vec_vector(sent, word2vec_model, model_type)
        if len(sent_vector) >= 1:
            predicted_class = classifier_model.predict([sent_vector])
            if predicted_class[0][0] == 1:
                resume.education.append(original[i])
            elif predicted_class[0][1] == 1:
                #resume.skills.append(original[i].trim())
                pass
            elif predicted_class[0][2] == 1:
                resume.work.append(original[i])
            elif predicted_class[0][3] == 1:
                resume.additional.append(original[i])
    skillfile = open(skill_repo).read().strip().split(',')
    all_sents = create_ngram(all_sents)
    for i, sent in enumerate(all_sents):
        for word in sent:
            if word.lower() in skillfile:
                resume.skills.append(word.title())
    resume.skills = list(set(resume.skills))

    return resume
