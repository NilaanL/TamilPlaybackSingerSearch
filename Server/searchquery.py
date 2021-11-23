# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 12:36:49 2021

@author: NILAAN
"""

from elasticsearch import Elasticsearch
import re
from query import basic_search, standard_analyzer,phrase_query,search_with_field

fields ={"பாடலாசிரியர்" : ":name_tamil",
                "Lyricist":"name_english"}

INDEX = 'nilaan170405l'
client = Elasticsearch("http://54.159.5.242")
print(client.info()["version"])
phraseregex=r'[\"\'][^\"\']+[\"\']'

def search(query):
    phrases=re.findall(phraseregex,query)
    print(phrases)
    if (len(phrases)>0):
#        Do phrase query
        body=phrase_query(phrases[0])
    elif (":" in query):
        phrases=query.replace(":"," : ")
        phrasesl =phrases.split()
        i=phrasesl.index(":",1,-1)
        body=search_with_field(phrasesl[i+1],phrasesl[i-1])
    else:
        body=basic_search(query)
    print(body)
    res = client.search(index=INDEX, body=body,request_timeout=300) 
    return res
#query="\"நடித்த\" \"பல\"" 
#phrases=re.findall(phraseregex,query)
    

#print(search("\"இசையில் நாட்டமும்\""))
