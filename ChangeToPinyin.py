#coding:UTF-8
from pinyin import PinYin
import heapq
import json

class word_fre:
    def __init__(self,word,fre):
        self.word=word
        self.fre=fre
    def __cmp__(x,y):
        return x.fre-y.fre

class changetopinyin:
    wf_dict={}
    
    def __init__(self):
        self.test=PinYin()
        self.test.load_word()


    def change(self,filename):
        with open(filename,'r') as ff:
            for item in ff.readlines():
                word,fre=item.split(' ')[0],int(item.split(' ')[1])
                wf=word_fre(word,fre)
                self.addtodict(wf)
        for item in self.wf_dict.itervalues():
            i=0
            for ii in item:
                try:
                    item[i]=(ii.word,ii.fre)
                except Exception as e:
                    print(e)
                i+=1
        self.save('pinyin_dict2')


    def addtodict(self,wf):
        pp=self.test.hanzi2pinyin_split(wf.word,'_')
        if(pp in self.wf_dict):
            if(len(self.wf_dict[pp])<=5):
                heapq.heappush(self.wf_dict[pp],wf)
            else:
                heapq.heappushpop(self.wf_dict[pp],wf)
        else:
            self.wf_dict[pp]=[]
            self.wf_dict[pp].append(wf)

    def save(self,filename):
        with open(filename,'w') as wff:
            try:
                wff.write(json.dumps(self.wf_dict))
            except Exception as e:
                print(e)


if __name__ == '__main__':
    cc=changetopinyin()
    try:
        cc.change('./jieba/dict.txt')
    except Exception as e:
        print(e)
