from gensim.models import Word2Vec, Doc2Vec
from sklearn.externals import joblib

from Resume.Resume import raw_resume_to_data, build_resume
from conf.parameters import *

def create_resume(resumetext):
    if word_model == "word2vec":
        model = Word2Vec.load(model_file)
    else:
        model = Doc2Vec.load(model_file)

    classifier_model = joblib.load(classifier_model_file)

    data, original = raw_resume_to_data(resumetext)
    resume = build_resume(data, original, model, classifier_model, word_model)
    formated_resume = resume.get_templatized_resume()
    # print json.dumps(resume.get_templatized_resume())
    return formated_resume
