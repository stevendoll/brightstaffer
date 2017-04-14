import os

dir_path = os.path.dirname(os.path.abspath(__file__))
previous_path = os.path.split(dir_path)[0]


# basepath = os.path.basename()
# Keras training parameters
keras_model_file = 'models/keras_lstm_trisent_3class_classifier.h5'
keras_model_file = os.path.join(previous_path, keras_model_file)


# Resume Creator parameters
nltk_data_path = 'nltk_data'
nltk_data_path = os.path.join(previous_path, nltk_data_path)
word_model = "word2vec"
model_file = "models/resumevectors_5_0"
model_file = os.path.join(previous_path, model_file)
classifier_model_file = "models/classifer-3-class_trisent_2_0.pkl"
classifier_model_file = os.path.join(previous_path, classifier_model_file)
skill_model_file = 'models/skill.pkl'
skill_model_file = os.path.join(previous_path, skill_model_file)
max_skill_count = 200

#N Gram model parameters
ngram_model = 'models/ngram_3_0'
ngram_model = os.path.join(previous_path, ngram_model)

#Ner Tagger
tagger_model_file = 'models/english.muc.7class.distsim.crf.ser.gz'
tagger_model_file = os.path.join(previous_path, tagger_model_file)
stanford_tagger_jar = 'models/stanford-ner.jar'
stanford_tagger_jar = os.path.join(previous_path, stanford_tagger_jar)

Alchemy_api_key = "770b5c0b1a4b6f1c8140e1b2b4b912d1fd392d8f"
alchemy_max_entities = 100
