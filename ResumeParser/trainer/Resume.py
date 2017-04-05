import os
import sys

import re
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
        """index = 0
        self.education = [x for x in self.education if x]
        for i, line in enumerate(self.education):
            if line.startswith('Education'):
                index = i
                break
        if index + 1 <= len(self.education) - 1:
            return self.education[index + 1:]
        else:
            return []"""
        return self.education

    def __get_skills__(self):
        self.skills = [{'name': skill['text'], 'score': skill['relevance']} for skill in self.skills]
        self.skills.sort(key=lambda x: x['score'], reverse=True)
        if len(self.skills) <= max_skill_count:
            return self.skills
        else:
            return self.skills[:max_skill_count]

    def __get_work__(self):
        self.work = []
        for career in self.career_history:
            tmp_dict = {'JobTitle': '',
                        'Company': '',
                        'Duration': '',
                        'type': ''
                        }
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
        return self.work

    def __get_other__(self):
        return self.additional

    def get_name(self):
        try:
            rel_list = [entity['relevance'] for entity in self.names]
            max_rel_index = rel_list.index(max(rel_list))
            return self.names[max_rel_index]['text']
        except Exception as exp:
            print(exp)
            return ''

    def get_templatized_resume(self):
        resume = dict()
        resume['name'] = self.get_name()
        resume['education'] = self.__get_education__()
        resume['skills'] = self.__get_skills__()
        resume['work-experience'] = self.__get_work__()
        resume['additional-info'] = self.__get_other__()
        return resume


def has_all_entities(career_detail):
    career_detail = set([entity[1] for entity in career_detail])
    if len(career_detail) >= 3:
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
    sent = sent[0] + sent[1] + sent[2]
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
    entities, keywords = entities[0], entities[1]
    resume = Resume(word_model='word2vec')
    try:
        resume.raw_lower = '\n'.join(original).lower()
        mlmodel_lstm = MlModel(classifier_model_lstm, model_type='lstm')
        mlmodel_treebased = MlModel(classifer_model_treebased, model_type='randomforest')
        __education_block__ = []
        for i, sent in enumerate(all_sents):
            sent_vector = get_word2vec_vector(sent, word2vec_model, 'word2vec')
            if len(sent_vector) >= 1:
                try:
                    predicted_class_lstm = mlmodel_lstm.predict(sent_vector)
                    predicted_class_treebased = mlmodel_treebased.predict(sent_vector)
                except Exception as exp:
                    print(exp)
                if predicted_class_lstm == 0 or predicted_class_treebased == 0:
                    # resume.education.append(original[i])
                    __education_block__.append(original[i])
                elif predicted_class_lstm == 1 or predicted_class_treebased == 1:
                    # Currently classified skills with ML is disabled because it's
                    # required to be processed before it could be used.
                    # resume.skills.append(original[i])
                    pass
                elif predicted_class_lstm == 2 or predicted_class_treebased == 2:
                    resume.work.append(original[i])
                elif predicted_class_lstm == 3 or predicted_class_treebased == 3:
                    resume.additional.append(original[i])

        resume.skills = keywords

        temp_entity = entities[:]
        entities = []
        entity_flag = dict()
        for index, entity in enumerate(temp_entity):
            if entity_flag.get(entity['text'], 0) == 0:
                entity_flag[entity['text']] = 1
                entities.append(entity)
        del temp_entity

        single_job_title = dict()
        for index, sent in enumerate(resume.work):
            for entity in entities:
                if (entity['type'] in ('JobTitle', 'Company')) and entity['text'] in sent:
                    if entity['type'] == 'JobTitle' and \
                                    str(index) not in single_job_title:
                        resume.career_history.append((entity['text'], entity['type'], index))
                        single_job_title[str(index)] = 1
                    elif entity['type'] != 'JobTitle':
                        resume.career_history.append((entity['text'], entity['type'], index))
                elif (entity['type'] in 'DATE') and \
                        (len(entity['text'].split()) >= 2 or entity['text'] == 'Present') and \
                                entity['text'] in sent:
                    resume.career_history.append((entity['text'], entity['type'], index))
                elif entity['type'] == 'Person':
                    resume.names.append(entity)
        del single_job_title

        organisations_flag = dict()
        for index, sent in enumerate(__education_block__):
            education_item_dict = {'organisation': '',
                                   'course': '',
                                   'duration': ''}
            for entity in entities:
                if entity['type'] == 'Organization' \
                        and entity['text'] in sent \
                        and (entity['text'] not in organisations_flag):
                    education_item_dict['organisation'] = entity['text']
                    organisations_flag[entity['text']] = 1
                    resume.education.append(education_item_dict)
        del __education_block__
        del organisations_flag

        temp_career_history = resume.career_history[:]
        resume.career_history = []
        if len(temp_career_history) >= 1:
            prev = temp_career_history[0]
            tmp_history = [prev]
            for index, entity in enumerate(temp_career_history[1:]):
                if (entity[2] - prev[2]).__abs__() < 2 and \
                        (not (len(tmp_history) > 3 and has_all_entities(tmp_history))):
                    tmp_history.append(entity)
                else:
                    if len(tmp_history) >= 3 and has_all_entities(tmp_history):
                        resume.career_history.append(tmp_history)
                    tmp_history = [entity]
                prev = entity
            if len(tmp_history) >= 3 and has_all_entities(tmp_history):
                resume.career_history.append(tmp_history)

        convert_date_to_duration(resume)

    except Exception as exp:
        print(exp)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        return resume


def enhance_information(talent_data, resume):
    try:
        current_company_index = -1
        if resume['work-experience']:
            for index, career in enumerate(resume['work-experience']):
                if career['type'] == 'Current':
                    current_company_index = index
                    break

        talent_data = talent_data.replace('\nExperience\n', '\nWork-Experience\n')
        lines = talent_data.split('\n')
        work_index = lines.index('Work-Experience')
        work_lines = lines[work_index + 1:work_index + 3]
        current_position = work_lines[0].split(' at ')[0]
        current_company = work_lines[0].split(' at ')[1]
        duration = re.split('(.*Present)\s+\(.*', work_lines[1])
        if len(duration) >= 3:
            duration = duration[1]
        else:
            duration = ''
        career_item = {'JobTitle': current_position, 'Company': current_company, 'Duration': duration,
                       'type': 'Current'}

        if current_company_index != -1:
            resume['work-experience'][current_company_index] = career_item
        else:
            resume['work-experience'].append(career_item)
    except Exception as exp:
        print(exp)
        pass
