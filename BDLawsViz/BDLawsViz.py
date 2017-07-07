# all the imports
import os
import itertools
import spacy

from flask import jsonify
from pymongo import MongoClient
from nltk.stem.porter import PorterStemmer
from flask.ext.mysql import MySQL
from flask import Flask, request, json, session, g, redirect, url_for, abort, \
     render_template, flash, session



app = Flask(__name__) # create the application instance :)

app.secret_key = 'why would I tell you my secret key?'

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123'
app.config['MYSQL_DATABASE_DB'] = 'KolpoKoushol'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Search Configuration
nlp = spacy.load('en')
client = MongoClient('localhost', 4000)
db = client.law
bigrams = db.bigrams
trigrams = db.trigrams
stemmer = PorterStemmer()

## Routes ##

@app.route("/")
def main():
    return render_template('index.html')


@app.route('/getallnames', methods=['GET'])
def getallnames():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_getAllNames')
        data = cursor.fetchall()

        ret = []
        for u in data:
            u_dict = {
                'Id': u[0],
                'name': u[1]
            }
            ret.append(u_dict)

        return json.dumps(ret)

    except Exception as e:
        return json.dumps("Error occured" + str(e))

    finally:
        cursor.close()
        con.close()


@app.route('/getalledges', methods=['GET'])
def getalledges():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_getAllEdges')
        data = cursor.fetchall()

        ret = []
        for u in data:
            if u[0] == u[1]:
                continue
            u_dict = {
                'source': u[0],
                'destination': u[1]
            }
            ret.append(u_dict)

        return json.dumps(ret)

    except Exception as e:
        return json.dumps("Error occured" + str(e))

    finally:
        cursor.close()
        con.close()


@app.route("/searchname", methods=['POST'])
def search_name():
    try:
        _searchtext = request.form['searchText']

        if _searchtext:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_searchName', (_searchtext,))
            data = cursor.fetchall()

            ret = "There is no law name for this id."
            for u in data:
                ret = u

            return ret
        else:
            return "Error: _searchText empty"

    except Exception as e:
        return "Error occurred:"+str(e)

    finally:
        cursor.close()
        con.close()


@app.route("/searchoutdegree", methods=['POST'])
def search_outdegree():
    try:
        _searchtext = request.form['searchText']

        if _searchtext:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_searchOutDegree', (_searchtext,))
            data = cursor.fetchall()

            ret = []
            for u in data:

                if u[2] == u[0]:
                    continue

                if u[0] and u[1] and u[2] and u[3]:
                    u_dict = {
                        'idS': u[0],
                        'nameS': u[1],
                        'idD': u[2],
                        'nameD': u[3],
                    }
                    ret.append(u_dict)

            return json.dumps(ret)

        else:
            return json.dumps("Error: _searchText empty")

    except Exception as e:
        return json.dumps("Error occurred:"+str(e))

    finally:
        cursor.close()
        con.close()


@app.route("/searchindegree", methods=['POST'])
def search_indegree():
    try:
        _searchtext = request.form['searchText']

        if _searchtext:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_searchInDegree', (_searchtext,))
            data = cursor.fetchall()

            ret = []
            for u in data:

                if u[2] == u[0]:
                    continue

                if u[0] and u[1] and u[2] and u[3]:
                    u_dict = {
                        'idS': u[0],
                        'nameS': u[1],
                        'idD': u[2],
                        'nameD': u[3],
                    }
                    ret.append(u_dict)

            return json.dumps(ret)

        else:
            return json.dumps("Error: _searchText empty")

    except Exception as e:
        return json.dumps("Error occurred:"+str(e))

    finally:
        cursor.close()
        con.close()



## Search Routes

@app.route('/search', methods=['GET'])
def search():
    query = str(request.args.get('query', ''))
    only_ngram_search = bool(int(request.args.get('ngram', True)))
    ids = _search(query, only_ngram_search=only_ngram_search)
    # DEBUG_MSG
    # print("QUERY: {}\nONLY NGRAM SEARCH: {}".format(query, only_ngram_search))
    print(ids)
    print(type(ids))
    return jsonify({
        "ids" : ids,
        "id_count" : len(ids)
    })





## search_script.py

def _search(text, only_ngram_search=True):
    # Ids
    _ids = []

    # Final search text
    ngram_search = ""

    # stemmed text
    text = nlp(u'' + text)

    # Only alphabet is real
    filtered_text = " ".join([stemmer.stem(t.lower_) for t in text if t.is_alpha])


    print(filtered_text)

    # Make a spacy doc
    text_doc = nlp(u'' + filtered_text)

    # Take word count
    word_count = text_doc.__len__()

    # DEBUG_MSG
    # print("WORD COUNT : {}".format(word_count))


    # Make ngram then search
    if (word_count > 1 and word_count < 4):
        # Splitting the keywords into separate words
        search_words = filtered_text.lower().split(' ')

        # DEBUG_MSG
        # print("SEARCH WORDS ", search_words)

        # Creating combination of n-grams
        search_combinations = ["_".join([word for word in combination]) for combination in itertools.permutations(search_words, len(search_words))]

        for combination in search_combinations:
            _ids.append(search_database(combination, ngram_search=True))


        _ids = list(set(sum(_ids, [])))

        # print("NGRAM _ ")


    if only_ngram_search == False or word_count > 3:
        all_key_search = search_database(filtered_text, ngram_search=False, delimiter=" ")

        # Concatening the list
        _ids = _ids + all_key_search

        # DEBUG_MSG
        # print("ALL KEY SEARCH: {}".format(all_key_search))

    return _ids

def search_database(text, ngram_search=True, delimiter='_'):
    _ids = []

    if ngram_search == True:
        for _id in range(1, 705):
            law_bigram = bigrams.find_one({'law_id' : _id})['text']
            law_trigram = trigrams.find_one({'law_id' : _id})['text']
            if text in law_bigram or text in law_trigram:
                _ids.append(_id)
    else:
        keywords = [stemmer.stem(key) for key in text.split(delimiter)]
        for _id in range(1, 705):
            law_bigram = bigrams.find_one({'law_id' : _id})['text']
            found_all = []
            for key in keywords:
                if key in law_bigram.split():
                    found_all.append(1)
            if sum(found_all) == len(keywords):
                _ids.append(_id)

    return _ids
