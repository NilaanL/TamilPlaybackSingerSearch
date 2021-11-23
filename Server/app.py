# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 12:33:46 2021

@author: NILAAN
"""

from flask import Flask, render_template, request
from searchquery import search
from elasticsearch_dsl import Index

app = Flask(__name__)
@app.route('/',methods=['GET','POST'])
def server():
    print("server started")
    if request.method == 'POST':
        query = request.form['searchTerm']
        res = search(query)
        print(res)
        hits = res['hits']['hits']
        time = res['took']
        # aggs = res['aggregations']
        num_results =  res['hits']['total']['value']

        return render_template('index.html', query=query, hits=hits, num_results=num_results,time=time)

    if request.method == 'GET':
        return render_template('index.html', init='True')  

if __name__=='__main__':
    app.run()
    