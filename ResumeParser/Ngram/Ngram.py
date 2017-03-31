import gensim

import ResumeParser.conf.parameters as params

def create_ngram(sents):
    ngram = gensim.models.Phrases.load(params.ngram_model)
    res = []
    if isinstance(sents, list) and isinstance(sents[0], list):
        for item in sents:
            res.append(ngram[item])
    else:
        res.append(ngram[sents])
    return res