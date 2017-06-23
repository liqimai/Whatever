#coding:utf-8
from pinyin import PinYin
from parse import Parser
import json
import copy
import heapq
import os

class tup:
    def __init__(self,term,fre):
        self.term=term
        self.fre=fre

    def __cmp__(x,y):
        if x.fre<y.fre:
            return -1
        else:
            if x.fre==y.fre:
                return 0
            else:
                return 1

class correction:

    def __init__(self):
        self.pa=Parser()
        self.pp=PinYin()
        self.pp.load_word()
        with open(os.path.join(os.path.dirname(__file__),'pinyin_dict'),'r') as ff:
            line=ff.readline()
            self.jj_dict=json.loads(line)
            ff.close()


    def correct(self,word,choose):
        if choose==1:
            phrase_list=self.pa.normalize(word)
        else:
            if choose==2:
                i=0
                phrase_list=[]
                while i < len(word):
                    phrase_list.append(word[i])
                    i+=1
        termlist=[]
        flag=False

        newplist=self.recompose(phrase_list)
        '''for item in newplist:
            for item2 in item:
                print(item2.encode('utf-8'))'''
        for nnlist in newplist:
            i=0
            tmp_correct=[]
            correct_num=[]
            for item in nnlist:
                py=self.pp.hanzi2pinyin_split(item,'_')
                tmp=[]
                tmp_correct.append(tmp)
                if(py in self.jj_dict):
                    for item2 in self.jj_dict[py]:
                        tmp_correct[i].append(item2)
                else:
                    tmp_correct[i].append((item,1))
                correct_num.append(0)
                i+=1
            
            length=len(tmp_correct)
            notend=True
            while notend:
                i=0
                tmpstr=''
                score=0
                for j in xrange(0,length):
                    tmps=tmp_correct[j][correct_num[j]][0]
                    tmpstr+=tmps
                    score+=int(tmp_correct[j][correct_num[j]][1])*len(tmps)**7
                termlist.append(tup(tmpstr,score))
                correct_num[0]+=1
                while correct_num[i]>=len(tmp_correct[i]):
                    correct_num[i]=0
                    if i<length-1:
                        correct_num[i+1]+=1
                        i+=1
                    else:
                        notend=False
        
        result_list=self.sscore(termlist)
        comstr=''
        for item in phrase_list:
            comstr+=item
        if result_list[0]==comstr:
            result_list=[]
        else:
            if comstr in result_list:
                result_list.pop(result_list.index(comstr))
        return result_list


    def sscore(self,termlist):
        heap=[]
        result_list=[]
        for item in termlist:
            heap.append(item)
        heapq.heapify(heap)
        while len(heap) > 5:
            
            a=heapq.heappop(heap)
        while len(heap) > 0:
            result_list.append(heapq.heappop(heap).term)
        
        result_list.reverse()
        return result_list

    def recompose(self,phrase_list):
        position=[]
        attach={}
        cpl=[]    #the consequence:list of list 
        i=0       #position of single word
        for item in phrase_list:
            if(len(item)==1):
                position.append(i)
                attach[i]=0
            i+=1

        notend=True
        length=len(position)
        if length>0:
            while notend:
                gap=0
                tmp_list=copy.deepcopy(phrase_list)
                tmp_position=copy.deepcopy(position)
                pi=0
                while pi < len(tmp_position):
                    item2=tmp_position[pi]
                    if(attach[item2]==0):
                        if item2-1-gap>=0:
                            tmp_list[item2-1-gap]+=tmp_list[item2-gap]
                            k=tmp_position.index(item2)
                            tmp_position.pop(k)
                            tmp_list.pop(item2-gap)
                            gap+=1
                        else:
                            pi+=1
                            '''while k < len(tmp_position):
                                tmp_position[k]-=gap
#print(tmp_position[k])
                                attach[tmp_position[k]]=attach[tmp_position[k]+gap]
                                k+=1'''
                    else:
                        if attach[item2]==1:
                            if item2+1-gap<len(tmp_list):
                                tmp_list[item2+1-gap]=tmp_list[item2-gap]+tmp_list[item2+1-gap]
                                k=tmp_position.index(item2)
                                tmp_position.pop(k)
                                tmp_list.pop(item2-gap)
                                gap+=1
                                if item2+1 in tmp_position:
                                    tmp_position.pop(tmp_position.index(item2+1))
                            else:
                                pi+=1
                        else:
                             pi+=1
                        '''while k < len(tmp_position):
                            tmp_position[k]-=gap
                            attach[tmp_position[k]]=attach[tmp_position[k]+gap]
                            k+=1'''
                '''flag=True
                for item3 in tmp_list:
                    if len(item3)==1:
                        flag=False
                if flag:'''
                if tmp_list not in cpl:
                    cpl.append(tmp_list)

                attach[position[0]]+=1 #每次变换一个
                i=0
                while attach[position[i]]>=3:
                        attach[position[i]]=0
                        if i<length-1:
                            attach[position[i+1]]+=1
                            i+=1
                        else:
                            notend=False
        else:
            cpl.append(phrase_list)
        return cpl


if __name__ == '__main__':
    word=raw_input('输入纠正词: ').decode('utf-8')
    choose=input('输入选择：1.普通查找 2.精确查找\n')
    cc=correction()
    '''for ii in phrase_list:
        print(ii.encode('utf-8'))'''
    print('________________before correct________________')
    ll=cc.correct(word,choose)
    if len(ll)==0:
        print('no correct')
    else:
        for item in ll:
            print(item.encode('utf-8'))

    '''cc=correction()
        ll.cc.correct(word,choose)'''
