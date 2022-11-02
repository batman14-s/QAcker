# QAcker

## THEME CHOSEN:

Education

QAcker is the one place solution for analysize, summarizing, paraphrasing and questioning tour text.

## OBJECTIVE AND SOLUTION

- Nowadays teachers and students alike have a lot on their plate, with advancing technology, our application utilises the power of strong machine learning models developed for natural language processing to help them in their daily schedule.
- In most places, english is the primary medium of instruction. If someone is not fluent in Englishlanguage they have to suffer academically, which is very unfortunate, and language shouldn't be something which restricts education.  
- Generating questions for assignments and unseen passages is a monotonous task which can be now automated, and our application aims to do just that.

## FEATURES

Paraphrasing
Question Generation
Answer Prediction
Text summarizer
Text to speech
Real time Speech to Text

## Techstack

- NLP - Natural language processing for performing the various  services mentioned
- Flask  - To develop the backend for the  web-application
- HTML/CSS/JavaScript - For devleoping frontend for the web-application
- Firebase - For providing authorization and storing database.
- Using python library to implement text to speech and speech to text functions.
- Utilizing HugginFace Library, which is an open-source library that provides multiple pipelines for performing various tasks on text data.

## How to start

1. Make Virtual Environment
```
python -m venv venv
source venv/Scripts/activate
```

2. Pip install requirements.txt

```
pip install -r requirements.txt
```

3. Run the following commands 
```
pip install thinc==7.4.2

pip install git+https://github.com/ramsrigouthamg/Questgen.ai
pip install git+https://github.com/boudinfl/pke.git@69337af9f9e72a25af6d7991eaa9869f1322dd72

python -m nltk.downloader universal_tagset
python -m spacy download en 

wget https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2015_md.tar.gz
tar -xvf  s2v_reddit_2015_md.tar.gz

pip install transformers==4.10.2
pip install sentencepiece==0.1.96
```

4. Run the final command for execution 
```
flask run
```
or 
```
python app.py
```

