# Whatever
Whatever is a toy search engine base on python2.7 and django1.8. It supports 
* Boolean Search
* Vector space model
* Top K approximate search
* Wildcard search
* Phrase search
* Spell check
* Generating abstracts
* Synonym search

## How to run
### Dependency
1. Python 2.7
2. Django 1.8
Please visit www.python.org to install python2.7, and then install django by

```bash
pip install django==1.8
```

If you use anaconda and the current environment is python of other versions,
please create a virtual environment of python 2.7, 
the details can be found in https://conda.io/docs/using/envs.html.
Here we briefly show how to do this in Linux or MacOS:
```bash
conda create --name py27 python=2.7
source activate py27
python --version
```
You will see the current version of python has already changed to 2.7.
Anytime you need python2.7 environment, you can enter it by
```bash
source activate py27
```
Now install django by:
```bash
conda install django==1.8
```
### The Corpus Requirements
Corpus is a collection of documents you want to search, 
we provide a small corpus in corpus folder.
It contains several `*.txt` file and a `index.txt`. 
`index.txt` saves file names of all documents you want to search on.
You can use your own corpus, but a `index.txt` must be provided.

### Build the index
Before starting search, whatever need to do some processing job. Type following command:
```bash
cd corpus
python -m http.server 9000
```
Then open another terminal, in the root directory of project, input:
```bash
python whatever/crawl.py
```
Wait for a while, dependent on how big the corpus is.

### Run the website
```bash
python manage.py runserver 8000
```

## Usage
Just input your query and push the `search` button.
### Boolean Search
We support `(`, `)`, `NOT`, `AND`, `OR`, the priority decrease orderly, 
and the AND between two words can be omitted. An querry example is 
```
automobile AND (tesla OR benz) AND NOT ferrari
```

### Wildcard
Support `'*'` in the begin, middle and end of a word.
`app*`, `tr*e`, `*cate` all are legal query.


