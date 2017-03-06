import gensim
import smart_open
import os

import ResumeParser.conf.parameters as params

def create_ngram(sents):
    ngram = gensim.models.Phrases.load(params.ngram_model)

    #sent = "I understand design patterns and object oriented programming".lower().split()
    res = []
    if isinstance(sents, list) and isinstance(sents[0], list):
        for item in sents:
            res.append(ngram[item])
    else:
        res.append(ngram[sents])
    return res