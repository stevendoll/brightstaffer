import string

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.externals import joblib


from ResumeParser.Ngram.Ngram import create_ngram
from ResumeParser.Utility.utility import convert_date_to_duration
from ResumeParser.conf.parameters import *

nltk.data.path.append(nltk_data_path)

class MlModel:
    def __init__(self, model, **kwargs):
        self.mlmodel = model
        self.model_type = kwargs['model_type']
    def predict(self, input_vector):
        if self.model_type == 'lstm':
            input_vector = np.reshape(np.array(input_vector),
                                      (1, 1, len(input_vector)))
            predicted_class = np.argmax(self.mlmodel.predict(input_vector),
                                        axis=1)
            return predicted_class[0]
        else:
            predicted_class = self.mlmodel.predict([input_vector])
            if predicted_class[0][0] == 1:
                return 0
            elif predicted_class[0][1] == 1:
                return 1
            elif predicted_class[0][2] == 1:
                return 2
            elif predicted_class[0][3] == 1:
                return 3

class Resume:
    def __init__(self, *args, **kwargs):
        self.__entities__ = []
        self.education = []
        self.skills = []
        self.work = []
        self.raw_lower = ''
        self.career_history = []
        self.additional = []
        self.names = []
        self.model_type = kwargs['word_model']

    def __get_education__(self):
        return self.education

    def __get_skills__(self):
        """string.punctuation = '!"#$%&()*/:;<=>?[\]^_`{|}~'
        skills = ','.join(self.skills).\
            translate(string.punctuation).\
            replace('years', '').\
            split(',')
        self.skills = skills
        del skills"""
        no_of_skills = len(self.skills)
        self.skills = [{'name':skill[0],'score':(skill[1]/no_of_skills)} for skill in self.skills]
        return self.skills

    def __get_work__(self):
        self.work = []
        tmp_dict = {}
        for career in self.career_history:
            for entity in career:
                if entity[1] == 'JobTitle':
                    tmp_dict['JobTitle'] = entity[0]
                elif entity[1] == 'Company':
                    tmp_dict['Company'] = entity[0]
                elif entity[1] == 'Duration':
                    tmp_dict['Duration'] = entity[0]
                    if 'Present' in entity[0]:
                        tmp_dict['type'] = 'Current'
                    else:
                        tmp_dict['type'] = 'Past'
            self.work.append(tmp_dict)
            tmp_dict = {}
        return self.work
    def __get_other__(self):
        return self.additional


    def get_name(self):
        rel_list = [ entity['relevance'] for entity in self.names ]
        max_rel_index = rel_list.index(max(rel_list))
        return self.names[max_rel_index]['text']


    def get_templatized_resume(self):
        resume = {}
        resume['name'] = self.get_name()
        resume['education'] = self.__get_education__()
        resume['skills'] = self.__get_skills__()
        resume['work-experience'] = self.__get_work__()
        resume['additional-info'] = self.__get_other__()
        return resume

def has_all_entities(career_detail):
    career_detail = set([entity[1] for entity in career_detail])
    if len(career_detail) >=3:
        return True
    else:
        return False

def get_word2vec_vector(sent, model, model_type):
    """

    :param model_type:
    :param sent:
    :param model:
    :return:
    """
    if model_type == "doc2vec":
        return model.infer_vector(sent)

    stop = set(nltk.corpus.stopwords.words('english'))
    sent_vector = []
    sent = sent[0]+sent[1]+sent[2]
    for j, word in enumerate(sent):
        word = WordNetLemmatizer().lemmatize(word)
        if word in model.wv.vocab and word not in stop:
            if len(sent_vector) == 0:
                sent_vector = np.array(model[word])
            else:
                sent_vector += np.array(model[word])

    return sent_vector



def extract_information_from_resume(all_sents, original, word2vec_model,
                                    classifier_model_lstm, classifer_model_treebased,
                                    entities):
    """
    :param original:
    :param classifier_model_lstm:
    :param classifer_model_treebased:
    :param entities:
    :param all_sents:
    :param word2vec_model:
    :return:
    """
    resume = Resume(word_model='word2vec')
    resume.raw_lower = '\n'.join(original).lower()
    mlmodel_lstm = MlModel(classifier_model_lstm, model_type='lstm')
    mlmodel_treebased = MlModel(classifer_model_treebased, model_type='randomforest')
    for i, sent in enumerate(all_sents):
        sent_vector = get_word2vec_vector(sent, word2vec_model, 'word2vec')
        if len(sent_vector) >= 1:
            try:
                predicted_class_lstm = mlmodel_lstm.predict(sent_vector)
                predicted_class_treebased = mlmodel_treebased.predict(sent_vector)
            except Exception as exp:
                print (exp)
                print (sent_vector)
            if predicted_class_lstm == 0 or predicted_class_treebased == 0:
                resume.education.append(original[i])
            elif predicted_class_lstm == 1 or predicted_class_treebased == 1:
                #resume.skills.append(original[i])
                pass
            elif predicted_class_lstm == 2 or predicted_class_treebased  == 2:
                resume.work.append(original[i])
            elif predicted_class_lstm == 3 or predicted_class_treebased == 3:
                resume.additional.append(original[i])
    skill_model = joblib.load(skill_model_file)
    all_sents = [sent[0] for sent in all_sents]
    all_sents = create_ngram(all_sents)
    for i, sent in enumerate(all_sents):
        for word in sent:
            if word.lower() in skill_model:
                if '_' in word:
                    word = word.replace('_', ' ')
                resume.skills.append((word.title(),resume.raw_lower.count(word.lower())))
    resume.skills = list(set(resume.skills))
    temp_entity = entities[:]
    entities = []
    entity_flag = {}
    for index, entity in enumerate(temp_entity):
        if entity_flag.get(entity['text'], 0) == 0:
            entity_flag[entity['text']] = 1
            entities.append(entity)
    del temp_entity
    for index,sent in enumerate(resume.work):
        for entity in entities:
            if (entity['type'] in ('JobTitle','Company')) and entity['text'] in sent:
                resume.career_history.append((entity['text'],entity['type'],index))
            elif (entity['type'] in 'DATE') and \
                    (len(entity['text'].split())>=2 or entity['text']=='Present') and \
                            entity['text'] in sent:
                resume.career_history.append((entity['text'],entity['type'],index))
            elif entity['type'] == 'Person':
                resume.names.append(entity)

    temp_career_history = resume.career_history[:]
    resume.career_history = []
    if len(temp_career_history)>=1:
        prev = temp_career_history[0]
        tmp_history = [prev]
        for index,entity in enumerate(temp_career_history[1:]):
            if (entity[2] - prev[2]).__abs__() < 2 and \
                (not(len(tmp_history) > 3 and has_all_entities(tmp_history))):
                tmp_history.append(entity)
            else:
                if len(tmp_history) >= 3 and has_all_entities(tmp_history):
                    resume.career_history.append(tmp_history)
                tmp_history = [entity]
            prev = entity
        if len(tmp_history) >= 3 and has_all_entities(tmp_history):
            resume.career_history.append(tmp_history)

    convert_date_to_duration(resume)

    return resume