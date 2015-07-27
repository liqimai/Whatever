#coding=utf-8
import os
import time
import urllib2
import sys
from bs4 import BeautifulSoup
import socket
from Indexbuild import IndexBuilder
import json
class crawl:
	baseurl=''
	req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
	req_timeout = 54
	urlqueue=[]
	urls=[]
	indegree=[]
	outdegree=[]
	length = []
	head=[]
	totalcount=0
	count=0
	read_web=set()
	graph = []
	
	def __init__(self,baseurl='http://www.cc98.org',urllist='urllist',queue='queue',invertedindex='invertedindex',graph='graph'):#将主网址加入集合
		self.baseurl=baseurl
		self.queueName = queue
		self.urllistName = urllist
		self.graphName = graph
		if os.path.exists(self.urllistName) and os.path.exists(self.queueName) and os.path.exists(self.graphName):
			self.indexbuilder = IndexBuilder(invertedindex)
			self.fillset(self.urllistName, self.queueName, self.graphName) #检查是否继续上次爬取
		else:
			self.indexbuilder = IndexBuilder()
	
	def user_agent(self, loopnum): #宽度优先遍历网页
		if self.urlqueue:
			url_parent = self.urlqueue.pop(0)
			url = url_parent[0]
			parent = url_parent[1]
		else:
			url = self.baseurl
			parent = self.baseurl
		while self.count < loopnum:
			try:
				if(url in self.read_web):
					try:
						urlid = self.urls.index(url)
					except Exception as e:
						print e
					try:
						self.indegree[urlid]+=1
					except Exception as e:
						print e
					try:
						self.graph[urlid][self.urls.index(parent)] = 1
					except Exception as e:
						print e,e.args
				else:
					self.read_web.add(url)
					tmpoutdegree=0
					print("it's the %d time"%(self.count))
					self.count=self.count+1#搜索网页数
					req = urllib2.Request(url,None,self.req_header)
					page = urllib2.urlopen(req,None,self.req_timeout)
					html = page.read()
					page.close()
					soup = BeautifulSoup(html)			
					self.urls.append(url)
					self.graph.append([])
					for i in xrange(len(self.urls)-1): 
						self.graph[i].append(0)
						self.graph[len(self.urls)-1].append(0)
					self.graph[len(self.urls)-1].append(0)
					self.indegree.append(1)
					self.graph[len(self.graph)-1][self.urls.index(parent)] = 1

					self.length.append(self.indexbuilder.process(soup,len(self.urls)-1))

					a = soup.find_all(['a'])
					for i in a:
						suburl=i.get('href')
						if(suburl is not None and suburl.find('javascript')==-1):
							if(suburl.find('http')==-1):
								suburl=self.baseurl+'/'+suburl
							if(suburl.find('www.cc98.org')!=-1):
								# print(suburl)
								self.urlqueue.append([suburl,url])
								suburl=''
								tmpoutdegree=tmpoutdegree+1
					#c=raw_input()
					self.outdegree.append(tmpoutdegree)
					time.sleep(0.2)
			except urllib2.URLError as e:
				print type(e), e.message, e.args
				print url
			except socket.timeout as e:
				print type(e), e.message, e.args
				print url
			except Exception as e:
				print e
				print url
			if(len(self.urlqueue)>0):
				url_parent = self.urlqueue.pop(0)
				url = url_parent[0]
				parent = url_parent[1]
			#结束了
	def save(self):
		self.indexbuilder.save()
		with open(self.queueName,'w') as qq:
			sys.stderr.write('Writing queue back into file...\n')
			for item in self.urlqueue:
				try:
					if(item is not None):
						qq.write(item[0]+' '+item[1]+'\n')
				except:
					sys.stderr.write('queue wrong but things well\n')
					pass
	
		with open(self.urllistName,'w') as uu:
			uu.write('%d\n'%(len(self.urls)))
			i=0
			print('Writing urllist back into file...')
			for item in self.urls:
				try:
					uu.write('%d %s %d %d %d\n'%(i, item, self.indegree[i], self.outdegree[i], self.length[i]))
					i+=1
				except:
					sys.stderr.write('%d %s %d %d %d\n'%(i, item, self.indegree[i], self.outdegree[i], self.length[i])+'\n')
					sys.stderr.write('urls output wrong\n')
					pass
			#return html
		with open(self.graphName,'w') as gg:
			print('Writing graph back into file...')
			try:
				json.dump(self.graph,gg,indent = 1)
			except Exception as e:
				sys.stderr.write(repr(e)+'\n')
				sys.stderr.write('Graph store error\n')

		with open('graph.txt','w') as file:
			print('Writing graph.txt back into file...')
			try:
				for line in self.graph:
					for entry in line:
						file.write(str(entry)+' ')
					file.write('\n')
			except Exception as e:
				sys.stderr.write(repr(e)+'\n')
				sys.stderr.write('Graph.txt write error\n')

	def fillset(self,urllist,queue,graph):#将以前访问过的网站加入set，重新获取queue
		with open(urllist,'r') as FILE:
			totalcount=FILE.readline()
			for item in FILE.readlines():
				try:
					(tmpid,tmpurl,tmpind,tmpoud,tmplen)=(item.strip('\n').split(' '))
					self.urls.append(tmpurl)
					self.read_web.add(tmpurl)
					self.indegree.append(int(tmpind))
					self.outdegree.append(int(tmpoud))
					self.length.append(int(tmplen))
				except Exception as e:
					sys.stderr.write(repr(e))
					sys.stderr.write('read in data error\n')

		with open(queue,'r') as FILE:
			for item in FILE.readlines():
				try:
					self.urlqueue.append(item.strip('\n').split(' '))
				except Exception as e:
					sys.stderr.write(repr(e))
					sys.stderr.write('read queue in error but well\n')

		with open(graph,'r') as FILE:
			try:
				self.graph = json.load(FILE)
			except Exception as e:
				sys.stderr.write(repr(e))
				sys.stderr.write('Read graph error\n')

#main
if __name__ == '__main__':
	cc=crawl()
	cc.user_agent(int(sys.argv[1]))
	cc.save()