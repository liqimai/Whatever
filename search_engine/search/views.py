#coding: utf-8
from __future__ import print_function
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template import RequestContext
from whatever.searchfunc import searcher, add_synonyms
# from whatever.correct import correction
from whatever.spelling import Spelling
import sys
import re

ssss = None
corrector = None
if ssss == None:
    ssss = searcher()
if corrector == None:
    sys.stderr.write('Initializing Corrector...')
    corrector = Spelling(["corpora/words_extend","corpora/words_domain"])
    corrector.load()
    corrector.train()
    sys.stderr.write('[Success]\n')

def search_form(request):
    return render_to_response('search_form.html')
def search(request):
    if request.GET['q']:
        q = request.GET['q']
        select_algo = request.GET['select_algo']
        k = int(request.GET['k'])
        if k == 0:
            k = 50

        # wildcard
        original_q = q
        if select_algo == u'boolean':
            def wildcard2orexp(match):
                wildcard = match.group(0)
                word_list = ssss.wildcard2word(wildcard)
                return '(' + ' OR '.join(word_list) + ')'
            q = re.sub(r'(\w+\*\w+)|(\w+\*)|(\*\w+)', wildcard2orexp, q)
        else:
            q = q.split()
            extended_wildcard = []
            for word in q:
                if '*' in word:
                    extended_wildcard.extend(ssss.wildcard2word(word))
                else:
                    extended_wildcard.append(word)
            q = ' '.join(extended_wildcard)

        # correction
        search_url = u'http://127.0.0.1:8000/search/?q={}&select_algo={}&k={}'
        correct_result = []
        for corrected_query in corrector.correct_string(q):
            correct_address = search_url.format(corrected_query,select_algo,k)
            correct_result.append({'url_addre': correct_address, 'url_name': corrected_query})

        # synonyms
        if select_algo != u'boolean':
            q = add_synonyms(q)

        if select_algo == u'boolean':
            finalresult = ssss.boolean(q, k)
        elif select_algo == u'tf_idf':
            finalresult = ssss.search_cos(q, k, False)
        elif select_algo == u'tf_idf_pagerank':
            finalresult = ssss.search_cos(q, k, True)
        elif select_algo == u'Okapi':
            finalresult = ssss.search_rsv(q, k, False)
        elif select_algo == u'Okapi_pagerank':
            finalresult = ssss.search_rsv(q, k, True)
        elif select_algo == u'lm':
            finalresult = ssss.lm(q, k, False)
        else:
            finalresult = ssss.lm(q, k, True)
        #finalresult stores the target urlids
        search_result = []
        for urlid_term in finalresult:
            url = ssss.urllist[urlid_term][0]
            #print thewebsite
            title = ssss.htmls[urlid_term][0]
            theabstract1 = ssss.abstract(q, urlid_term)
            theabstract = []
            for ab1_item in theabstract1:
                theabstract.append({'abstract1': ab1_item[0], 'abstract2': ab1_item[1], 'abstract3': ab1_item[2]})
            # print theabstract
            search_result.append({'url': url, 'title': title, 'abstract': theabstract})
        total_number = len(finalresult)     

        # search_result = [
        # {'url':'http://www.baidu.com/', 'name': '百度'}, 
        # {'url': 'http://www.cc98.org/', 'name': 'CC98'},
        # {'url':'http://www.sina.com.cn/', 'name': '新浪'},
        # {'url':'http://www.cc98.org/hottopic.asp', 'name': '24小时热门话题'},
        # {'url':'http://www.cc98.org/list.asp?boardid=152', 'name': '缘分天空'},
        # {'url':'http://www.cc98.org/list.asp?boardid=114', 'name': '郁闷小屋'}]
     #    total_number = 6


        return render(request, 'result.html', {'search_result': search_result, 'total_number': total_number,
                                               'correct_result': correct_result, 'q': original_q})
    else:
        return render_to_response('search_form.html')
