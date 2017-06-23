# -*- coding: utf-8 -*-
import collections
from parse import parser
from copy import copy
class Spelling(object):
    ALPHA = "abcdefghijklmnopqrstuvwxyz"
    PUNCTUATION = [',','.',':','?',';','(',')','[',']','&','!','*','@','#','$','%','+','<','>','\"']

    def __init__(self, path):
        self.path = path
        self.feature = []

    def load(self):
        for path in self.path:
            fin = open(path)
            for item in fin.readlines():
                self.feature.append(item.strip())
        

    def train(self):
        '''
        Counts the words in the given corpora
        '''
        n = len(self.feature)
        self.model = collections.defaultdict(lambda:1)
        for f in self.feature:
            self.model[f.lower()] += 1
        
    def edit1(self, word):
        '''
        Return a set of words with edit distance 1 from the given word.
        '''
        n = len(word)
        deletetion = [word[0:i]+word[i+1:] for i in range(n)]
        transposition = [word[0:i]+word[i+1]+word[i]+word[i+2:] for i in range(n-1)]
        alteration = [word[0:i]+c+word[i+1:] for i in range(n) for c in Spelling.ALPHA]
        insertion = [word[0:i]+c+word[i:] for i in range(n+1) for c in Spelling.ALPHA]
        return set(deletetion + transposition + alteration + insertion)

    def edit2(self, word):
        '''
        Return a set of words with edit distance 2 from the given word.
        '''
        return set(e2 for e1 in self.edit1(word) for e2 in self.edit1(e1))

    def know(self, words):
        return set(w for w in words if w in self.model)

    def correct(self, word):
        word = word.lower()
        if len(word) == 1:
            return [(word, 1.0)] # I
        if word in Spelling.PUNCTUATION:
            return [(word, 1.0)] # .?!
        if word.replace(".", "").isdigit():
            return [(word, 1.0)] # 1.5
        candidates = self.know([word]) or self.know(self.edit1(word)) or self.know(self.edit2(word)) or set([word])
        candidates = [(self.model[c], c) for c in candidates]
        s = float(sum(p for p, word in candidates))
        candidates = sorted(((p / s, word) for p, word in candidates), reverse=True)
        return candidates
        #print candidates
        #return candidates[0]

    def correct_string(self, string):
        words = parser.cut(string)
        wc_list = [words_confidence([],1)]
        for word in words:
            new_wc_list = []
            for corredted_word in self.correct(word):
                for old_words in wc_list:
                    wc = words_confidence(copy(old_words.words),
                                          old_words.confidence*corredted_word[0])
                    wc.words.append(corredted_word[1])
                    new_wc_list.append(wc)
            wc_list = new_wc_list
        wc_list.sort()
        if wc_list[0].words == words:
            return []
        else:
            return [' '.join(wc.words) for wc in wc_list if wc.confidence > 0.5]
        # return wc_list

class words_confidence:
    def __init__(self, words, confidence):
        self.words = words
        self.confidence = confidence

    def __cmp__(self, other):
        if self.confidence > other.confidence:
            return -1
        elif self.confidence == other.confidence:
            return 0
        elif self.confidence < other.confidence:
            return 1
    def __repr__(self):
        return str(self.confidence)+' '+str(self.words)

if __name__=="__main__":
    from vocabulary.vocabulary import Vocabulary as vb
    import json
    try:
        car_synonyms = json.loads(vb.synonym("qertadf"))
    except Exception as e:
        car_synonyms = []
    print(car_synonyms)
    # print(vb.synonym("car"))
    # corrector = Spelling(["corpora/words_extend","corpora/words_domain"])
    # corrector.load()
    # corrector.train()
    # print corrector.correct("tape")
    # print corrector.correct("chinaa")
    # print corrector.correct("speling'")
    # print corrector.correct("bycycle")
    # print corrector.correct("inconvient")
    # print corrector.correct("arrainged")
    # print corrector.correct("peotry")
    # print corrector.correct("peotryy")
    # print corrector.correct("quintessential")
    # print corrector.correct_string('inconvient arrainged')
    # assert correction('speling') == 'spelling'              # insert
    # assert correction('korrectud') == 'corrected'           # replace 2
    # assert correction('bycycle') == 'bicycle'               # replace
    # assert correction('inconvient') == 'inconvenient'       # insert 2
    # assert correction('arrainged') == 'arranged'            # delete
    # assert correction('peotry') =='poetry'                  # transpose
    # assert correction('peotryy') =='poetry'                 # transpose + delete
    # assert correction('word') == 'word'                     # known
    # assert correction('quintessential') == 'quintessential' # unknown
