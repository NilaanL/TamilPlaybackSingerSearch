from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Index
import json
import pandas as pd
from datetime import datetime
# import queries
#
client = Elasticsearch("http://54.159.5.242")
#client = Elasticsearch(HOST="http://54.159.5.242", PORT=9200,timeout=300)
INDEX = 'nilaan170405l'
print (client)
#
print ("Elasticsearch client version:", client.info()["version"], "\n")
##client.indices.delete(INDEX)
## Creating index if not manually created
def createIndex():
    if(client.indices.exists(index=INDEX,request_timeout=30)==False):
        index = Index(INDEX, using=client)
        res = index.create()
        print(res)
        

def read_all_songs():
    all_songs= pd.read_csv("G:\Acca Folder\SEM 7\IR\Project\mydata\wiki\processed\lyrics.csv")
    all_songs["பாடியவர்கள்"]=all_songs["பாடியவர்கள்"].apply(lambda x: x.strip("[").strip("]").replace("'","").split(","))
    all_songs["பாடியவர்கள்"]=all_songs["பாடியவர்கள்"].apply(lambda x: [i.strip() for i in x])
    all_songs=all_songs.rename(columns={
            "பாடியவர்கள்" : "singers",
            "திரைப்படம்" : "movie",
            "பாடலாசிரியர்" : "Lyricist",
            "இசையமைப்பாளர்" : "composer" ,
            "பாடல்" : "song" ,
            "வருடம்" : "year",
            "பாடல்வரிகள்" : "lyrics",
            "மதிப்பீடு" : "rating",
            "வகை" : "type",
            "நுகர்ச்சி" : " views"})
    jsonRecords = all_songs.to_json(orient="records",force_ascii=False)
    jsondump=json.loads(jsonRecords)
    return jsondump

def read_all_singers():
    singers= pd.read_csv("G:\Acca Folder\SEM 7\IR\Project\mydata\wiki\processed\playbackSingers.csv")
    jsonRecords = singers.to_json(orient="records",force_ascii=False)
    jsondump=json.loads(jsonRecords)
    return jsondump

createIndex()
all_songs = read_all_songs()
all_singers = read_all_singers()
#print(all_songs)
##for i in all_singers[33:34] :
##    print(i.get("Birth"))
##    print(datetime(2000,5,2))
##    print(datetime.now())

#
def genData(song_array,singers_array):
    for record in singers_array:
        name_tamil=record.get("name_tamil",None)
        name_english=record.get("name_english",None)
        url_TU=record.get("url_TU",None)
        url_WIKI=record.get("url_WIKI",None)
        Birth=record.get("Birth",None)
        Death=record.get("Death",None)
        Bio=record.get("Bio",None)
        summary=record.get("summary",None)
        Awards=record.get("Awards",None)
        songs=[]
        
        for srecord in song_array:
            if(name_tamil in srecord.get("singers",[]) ):
                songs.append(srecord)
        if len(songs)==0:
            songs=None
#        print(songs)
        yield {
                "_index":INDEX,
                "_source":{
                "name_tamil":name_tamil,
                "name_english":name_english,
                "url_TU":url_TU,
                "url_WIKI":url_WIKI,
                "Birth":Birth,
                "Death":Death,
                "Bio":Bio,
                "summary":summary,
                "Awards":Awards,
                "songs":songs,
                },
        }
                
helpers.bulk(client,genData(all_songs,all_singers))
#genData(all_songs,all_singers)
print("done")
