# Tamil Playback Singers SeachEngine

## Directory Structure 
---
```
 ├──── Server : python scripts
 |──────app.py : Flash backend
 |──────bulkdata.py script to convert csv data to elastic bulkdata and upload
 |──────query.py :  sample query
 |──────search.py : seach script to handle different searches
 |──────templates : html template folder
 |──────static : css 
 |────hunspell :  hunspel library files for tamil ( downloaded from [here](https://github.com/AshokR/TamilNLP/tree/master/tamilnlp/Resources)
 |──────ta_IN.aff
 |──────ta_IN.dic
 ├────mydata : containes scraped data & cleaned data
 |────── wiki_scaper.ipynb : cutome script to scrape selected wiki category
 |────── wiki&TU : data scraped from wikipedia and TU along with cleaned data
 |────────── pre_processor.ipynb : preprocessing pipeline for both TU and Wiki
```

## requirements
-----
* docker 
* python 3.6 
* flask
* postman

## Setup 
---- 
1. run elastic search container 
```
docker run -d --name elasticN -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.15.0 
```
1.1 optionaly kibana service can be edployed using below cmd
```
docker run -d --name kibana -p 5601:5601 -e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" docker.elastic.co/kibana/kibana:7.15.1
```
2. wait for ~2-5 min for image to be downloaded and start the service 
3. now the elastic search service is availbe on localhost:9200
4. send below requet to localhose:9200 to create a index 
```
PUT localhost/9200/nilaan170405l
```
5. close the index by below cURL cmd 
```
POST 'http://localost:9200/nilaan170405l/_close'
```
6. download hunspell tamil dictionary from [here](https://github.com/AshokR/TamilNLP/tree/master/tamilnlp/Resources)
7. copy tamil hunspell dictionary to container
```
docker cp ./ta_IN.aff  elasticN:/usr/share/elasticsearch/config/hunspell/ta_IN/
docker cp ./ta_IN.dic  elasticN:/usr/share/elasticsearch/config/hunspell/ta_IN/
```
8. run below cURL cmd to update analysers 
```
PUT 'http://localost:9200/nilaan170405l/_settings
{
    "analysis": {
        "analyzer": {
            "default": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "indic_normalization",
                    "tamil_stemmer"
                ]
            }
        },
        "filter": {
            "tamil_stemmer": {
                "type": "hunspell",
                "locale": "ta_IN"
            }
        }
    }
}
```
9. now lets create mappings
```
PUT 'http://localost:9200/nilaan170405l/_mapping 
{
    "properties": {
        "Awards": {
            "type": "text"
        },
        "Bio": {
            "type": "text"
        },
        "Birth": {
            "type": "date",
            "format": "yyyy-MM-dd HH:mm:ss"
        },
        "Death": {
            "type": "text"
        },
        "name_english": {
            "type": "text"
        },
        "name_tamil": {
            "type": "text"
        },
        "summary": {
            "type": "text"
        },
        "url_TU": {
            "type": "text",
            "index":false
        },
        "url_WIKI": {
            "type": "text",
            "index":false
        },
        "songs":{
            "type":"nested",
            "properties":{
                "singers":{
                    "type":"text"
                },
                "movie":{
                    "type":"text"
                },
                "Lyricist":{
                    "type":"text"
                },
                "composer":{
                    "type":"text"
                },
                "song":{
                    "type":"text"
                },
                "year":{
                    "type":"integer"
                },
                "lyrics":{
                    "type":"text"
                },
                "rating":{
                    "type":"integer"
                },
                "type":{
                    "type":"keyword"
                },
                "view":{
                    "type":"integer"
                }
            }
        }
    }
}
```
10. optinaly , required Text filed can be set to 'fielddata=true' to support aggregation 
```
PUT 'http://localost:9200/nilaan170405l/_mapping
{
    "properties": {
        "songs":{
            "type":"nested",
            "properties":{
                "movie":{
                    "type":"text",
                    "fielddata":true
                }
            }
        },
        "Bio":{
            "type":"text",
            "fielddata":true
        },
        "summary":{
            "type":"text",
            "fielddata":true
        }
    }
}
```
11. now you need to open the index 
``` POST 'http://localost:9200/nilaan170405l/_open ```

12. optionaly our new analyser can be checked by issuing below cmd
```
POST 'http://localost:9200/nilaan170405l/_analyze
{
    "text": "பூவா இல்ல புஷ்பமாே"
}
```
13. now run the bulkdata.py to update our data to the elastic search(note the host name need to be update accordingly )
14. run app.py to lauch flash server 
15. UI can be accessed at localhost:5000

##Query
---
1. type the query in the seach box  ( alternatively queries can be executed from postman or kibana  )
2. For phrase search use wrap the phrase using quatation marks
eg : "பாடும் ஓர்"
3. To query a specific field follow below format
```
<FieldName> : <query>
```

4.for wildcard query use * to represent wildcard
eg : ரகு*

------------

## Sample Queries 
-----------------
request URL : 
```
GET 'http://localost:9200/nilaan170405l/_search
```

1. simple query 
```
{
    "query": {
        "query_string": {
            "query":"சித் ஸ்ரீராம்"
        }
    }
}
```
2. fieled seacrh ( can be used when you know the name or movie or song)
```
{
    "query": {
        "match": {
            "name_tamil":"மன்னா"
        }
    }
}
```
3. multimatch query 
```
{
    "query": {
        "multi_match": {
            "query":"பாடகர் ",
            "fields":["summary","Bio"],
            "operator":"or",
            "type":"best_fields"    
        }
    }
}
```
4. fuzzy search 
```
{
    "query": {
        "fuzzy": {
            "name_tamil": {
                "value": "சுந்தர",
                "fuzziness": 2,
                "prefix_length": 0,
                "max_expansions": 100,
                "boost": 1
            }
        }
    }
}
```
5. phrase query 
```
{
    "query": {
        "multi_match": {
            "query":"பாடும் ஓர்",
            "type":"phrase",
            "fields":["summary","songs","Awards","Bio"]
        }
    }
}
```
6. sort and select top 10 from results
```
{
    "query": {
        "query_string": {
            "query":"மலையாள மற்றும் தமிழ்"
        }
    } , 
    "size":10,
    "sort":[
        {"songs.rating":{
            "order":"asc"
            }
        }
    ]
} 
```
7. suggest as you type 
```
{
    "suggest":{
            "my-suggestion":{
                "text":"பயமா இருக்குது கருப்ப சாமி",
                "term":{
                    "fields":["summary"]
                }
        }
        }

}
```
8. likeQuery 
```
{
    "query": {
        "more_like_this": {
            "like": "அவர் பல கன்னட படங்களுக்கும் அமிர்ததரே \"நூறு ஜன்மகு மற்றும் \"திரு திருமதி ராமாச்சரி ஆகிய திரைப்படங்களுக்கு குரல் ஒலிச்சேர்க்கை செய்துள்ளார் . கன்னடத்தில் 5000 க்கும் மேற்பட்ட பாடல்கள் தெலுங்கில் 500 பாடல்கள் தமிழ் மற்றும் இந்தி மொழியில் 500க்கும் மேற்பட்ட பாடல்களைப் பாடியுள்ளார் . மேலும் 17 மொழிகளில் பக்தி இசை தொகுப்புகள் கருப்பொருள் இசைத் தொகுப்புகள் மற்றும் விளம்பரங்களுக்காகவும் பாடியுள்ளார் . அவர் பல கன்னட படங்களுக்கும் அமிர்ததரே \"நூறு ஜன்மகு மற்றும் \"திரு திருமதி ராமாச்சரி ஆகிய திரைப்படங்களுக்கு குரல் ஒலிச்சேர்க்கை செய்துள்ளார் . மாருதி சுஜூகி வாகொனார் தொலைக்காட்சி மஞ்சால் சோப்பு இந்துலேகா முடி எண்ணெய் போன்ற நிறுவன விளம்பரங்கள் மற்றும் பிற நிறுவனங்களின் பொருள்களுக்காகவும் ராஜேஷ் விளம்பர மாதிரியாயிருந்தார் . மாருதி சுஜூகி வாகொனார் தொலைக்காட்சி மஞ்சால் சோப்பு இந்துலேகா முடி எண்ணெய் போன்ற நிறுவன விளம்பரங்கள் மற்றும் பிற நிறுவனங்களின் பொருள்களுக்காகவும் ராஜேஷ் விளம்பர மாதிரியாயிருந்தார் . ராஜேஷ் ஜீ கன்னட டி . வி தொலைக்காட்சியில் பல பாடல்களுக்கான நிகழ்ச்சிகளுக்கு குறிப்பாக ச ரி க ம ப இசை நிகழ்ச்சி நீதிபதியாக நியமிக்கப்பட்டார்",
            "fields": [
                "summary",
                "Bio",
                "songs.lyrics"
            ],
            "min_term_freq": 1,
            "max_query_terms": 25
        }
    }
}
```
9. combined query 
```
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "summary": "பாடகராகவும்"
        }
      },
      "filter": [
        {
          "multi_match": {
            "query": "இடம்",
            "fields": [
              "summary","Bio"
            ]
          }
        }
      ],
      "must_not": {
        "term": {
          "summary": "சபேஷ்"
        }
      },
      "should": {
        "term": {
          "songs.lyrics": "வருவேன்"
        }
      }
    }
  },
  "aggs": {
    "Category Filter": {
      "terms": {
        "field": "summary"
      }
    }
    // "types_count" : { "value_count" : { "field" : "songs.type" } }
  }
}
```


--- END --- 
