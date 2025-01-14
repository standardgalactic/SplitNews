import requests
import json
from urllib.parse import urlparse
import re
import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from news_analysis.bias_detector import get_bias
import json

def textsummarize(body, size):
    text = body

    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    #tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text.lower() not in word_frequencies:
                    word_frequencies[word.text.lower()] = 1
                else:
                    word_frequencies[word.text.lower()] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency

    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    select_length = int(len(sentence_tokens)*size)
    summary = nlargest(select_length, sentence_scores, key = sentence_scores.get)
    final_summary = [word.text for word in summary]
    temp = '<ul><li>'
    temp += '</li><li>'.join(final_summary)
    temp += '</li></ul>'

    return temp

def leftandright(biases):
    returnlist = []
    leftstring = ""
    for i in biases[0]:
        leftstring = leftstring + i['body']
    if leftstring != "":
        returnlist.append(textsummarize(leftstring, .05))
    else:
        returnlist.append("")


    central = ""
    for i in biases[1]:
        central = central + i['body']
    if central != "":
        returnlist.append(textsummarize(central, .05))
    else:
        returnlist.append("")

    rightstring = ""
    for i in biases[2]:
        rightstring = rightstring + i['body']
    if rightstring != "":
        returnlist.append(textsummarize(rightstring, .05))
    else:
        returnlist.append("")
    return returnlist

def search(term):
    subscription_key = "82439de0d47c4c80924cdda033e1c8d0"
    search_url = "https://splitnews.cognitiveservices.azure.com/bing/v7.0/news/search"

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    urllist = []
    for i in search_results['value']:
        urllist.append(i['url'])



    fullstack = get_bias(urllist)
    hugefirstreturnthing = leftandright(fullstack)
    ret_urls = []
    for q in fullstack:
        for site in q:
            ret_urls.append(site['url'])
    totalinformation = []
    for i in search_results['value']:
        totalinformation.append(i)

    finaldict = {}
    for i in range(len(urllist)):
        if urllist[i] not in ret_urls:
            continue
        if urllist[i] not in finaldict.keys():
            finaldict[urllist[i]] = [totalinformation[i]['name'], totalinformation[i]['url'], totalinformation[i]['image'], 0, "", ""]

    for i in fullstack[0]:
        finaldict[i['url']][3] = i['bias']
        finaldict[i['url']][4] = textsummarize(i['body'], .1)
        finaldict[i['url']][5] = textsummarize(i['body'], .3)

    for i in fullstack[1]:
        finaldict[i['url']][3] = i['bias']
        finaldict[i['url']][4] = textsummarize(i['body'], .1)
        finaldict[i['url']][5] = textsummarize(i['body'], .3)

    for i in fullstack[2]:
        finaldict[i['url']][3] = i['bias']
        finaldict[i['url']][4] = textsummarize(i['body'], .1)
        finaldict[i['url']][5] = textsummarize(i['body'], .3)
    
    return (hugefirstreturnthing, list(finaldict.values()))


