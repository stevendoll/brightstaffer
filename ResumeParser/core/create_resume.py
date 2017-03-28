import keras
from gensim.models import Word2Vec
from sklearn.externals import joblib

from ResumeParser.Ner.entities import get_entities
from ResumeParser.Preprocessing.preprocess import raw_resume_to_data_tri_sentences
from ResumeParser.conf.parameters import *
from ResumeParser.trainer.Resume import extract_information_from_resume


def create_resume(talent_data):
    """

    :return:
    """
    model = Word2Vec.load(model_file)
    classifier_model_treebased = joblib.load(classifier_model_file)
    classifier_model_lstm = keras.models.load_model(keras_model_file)
    entities = get_entities(talent_data)

    data, original = raw_resume_to_data_tri_sentences(talent_data)
    resume = extract_information_from_resume(data, original,
                                             model,
                                             classifier_model_lstm,
                                             classifier_model_treebased,
                                             entities)
    formated_resume = resume.get_templatized_resume()

    return formated_resume