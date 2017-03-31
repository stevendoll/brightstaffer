from nltk.tag.stanford import StanfordNERTagger
from watson_developer_cloud import AlchemyLanguageV1

from ResumeParser.conf.parameters import *


def get_entity_date(tagged):
    ent = []
    tmp = []
    prev = ''
    for keyword in tagged:
        if prev == keyword[1]:
            tmp.append(keyword[0])
        else:
            ent.append((' '.join(tmp), prev))
            prev = keyword[1]
            tmp = [keyword[0]]
    ent.append((' '.join(tmp), prev))
    date_ent = []
    for item in ent:
        if 'DATE' in item[1]:
            date_ent.append(item)
    return date_ent

def get_entity_other(entities_dict, sent):
    keyword_list = []
    for item in entities_dict:
        if item['type'] == ('Company', 'JobTitle') and item['text'] in sent:
            # if item['type'] == "Organization":
            keyword_list.append((item['text'].lower(), item['type']))
    return list(set(keyword_list))

def fetch_entities_from_alchemy_api(user_data):
    d = {}
    try:
        alchemy_language = AlchemyLanguageV1(api_key=Alchemy_api_key)
        d = alchemy_language.combined(text=user_data,
                                      extract='entities,keywords',
                                      max_items=alchemy_max_entities)
        #d = json.loads(data)
        #Projects.objects.filter(id=project_id).update(description_analysis=d)
    except Exception as e:
        print (e)
    return d['entities']

def fetch_entities_stanford_ner(user_data):
    tagger = StanfordNERTagger(tagger_model_file, stanford_tagger_jar)
    resume_keywords = user_data.split()
    tagged = get_entity_date(tagger.tag(resume_keywords))
    return tagged


def get_entities(user_data):
    stanford_ner_entities = fetch_entities_stanford_ner(user_data)
    alchemy_ner_entities = fetch_entities_from_alchemy_api(user_data)
    for entity in stanford_ner_entities:
        alchemy_ner_entities.append({'type':'DATE','text':entity[0]})
    alchemy_ner_entities.append({'type':'DATE','text':'Present'})
    return alchemy_ner_entities