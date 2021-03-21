import config # to hide TMDB API keys
import requests # to make TMDB API calls
import locale # to format currency as USD
locale.setlocale( locale.LC_ALL, '' )

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from urllib.parse import quote
from urllib.request import urlopen
import json
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

import pymysql
import hashlib

app = Flask(__name__)


@app.route("/")
def home():
    response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&sort_by=primary_release_date.desc&include_video=true&with_release_type=5')
    response_animation = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&language=en-US&sort_by=primary_release_date.desc&include_adult=false&include_video=false&page=1&with_genres=16')
    newmovie = response.json()
    newmovie_animation = response_animation.json()
    return render_template("main.html",data=[newmovie,newmovie_animation])


@app.route("/popularity_year")
def popularity_year():
    year = range(1950,2022)
    return render_template("popularity_year.html",data=year)

@app.route("/popularity/<year>")
def popularity(year):
    response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&primary_release_year='+year+'&sort_by=popularity.desc')
    highest_popularity = response.json()
    return render_template("popularity.html",data=highest_popularity)

@app.route("/movie/<id>")
def movie(id):
    response = requests.get('https://api.themoviedb.org/3/movie/'+id+'?api_key=d4db5c0d2cdc601df925e6de360e6bbb')
    movie = response.json()
    return render_template("movie.html",data=movie)

"""@app.route("/contact")
def contact():
    return render_template("contact.html")
"""
@app.route("/search/<movie>")
def search(movie):
    response = requests.get('https://api.themoviedb.org/3/search/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&language=en-US&query='+movie+'&page=1&include_adult=false')
    search = response.json()
    return render_template("search.html",data=search)





@app.route("/formember", methods=['GET','POST'])
def login2():
    if request.method == 'POST':
        if request.form.get('exampleInputName') and request.form.get('exampleInputEmail1') and request.form.get('exampleInputPassword'):
            name = request.form.get("exampleInputName")
            email = request.form.get("exampleInputEmail1")
            password = request.form.get("exampleInputPassword")
            con = pymysql.connect(host = 'brdorzjt80zuhmuuu6xp-mysql.services.clever-cloud.com', user = 'ulywfvgngyregojv', password = 'kF3jScPgTs7oj0Us7N2a', database = 'brdorzjt80zuhmuuu6xp')
            try:
                with con.cursor() as cur:
                    cur.execute("INSERT INTO datauser VALUES(Null, %s, %s, %s)", (name, password, email))
                    con.commit()
            finally:
                con.close()
                return render_template("login2.html")
        elif request.form.get('login') and request.form.get('logintPassword'):
            rows = ()
            mail = request.form.get('login')
            password = request.form.get('logintPassword')
            con = pymysql.connect(host = 'brdorzjt80zuhmuuu6xp-mysql.services.clever-cloud.com', user = 'ulywfvgngyregojv', password = 'kF3jScPgTs7oj0Us7N2a', database = 'brdorzjt80zuhmuuu6xp')
            try:
                with con.cursor() as cur:
                    cur.execute("SELECT * FROM datauser WHERE email=%s AND password=%s", (mail, password))
                    rows = cur.fetchall()
            finally:
                con.close()
            if len(rows) == 1:
                con = pymysql.connect(host = 'brdorzjt80zuhmuuu6xp-mysql.services.clever-cloud.com', user = 'ulywfvgngyregojv', password = 'kF3jScPgTs7oj0Us7N2a', database = 'brdorzjt80zuhmuuu6xp')
                try:
                    with con.cursor() as cur:
                        cur.execute("UPDATE datauser SET time = Now()  WHERE name = %s",(rows[0][1]))
                        con.commit()
                finally:
                    con.close()
                    print("welcome"),rows[0][2]
                    resp = make_response(render_template("formember.html", data=rows[0]))
                    resp.set_cookie('userName', rows[0][1])
                    resp.set_cookie('userEmail', rows[0][3])
                    return resp
            else:
                print("unsucess")
                return render_template("login2.html")

    return render_template("login2.html")


@app.route("/contact")
def contact():
    row = []
    con = pymysql.connect(host = 'brdorzjt80zuhmuuu6xp-mysql.services.clever-cloud.com', user ='ulywfvgngyregojv', password = 'kF3jScPgTs7oj0Us7N2a', database = 'brdorzjt80zuhmuuu6xp')
    try:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM developer')
            rows = cur.fetchall()
            for i in rows:
                row.append(i)
    finally:
            con.close()
    return render_template("contact.html", row=row) 



@app.route("/genres/<genres>")
def genres(genres):
    movie = []
    for n in range(1,21):
        response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&language=en-US&sort_by=primary_release_date.desc&include_adult=false&include_video=false&page='+str(n)+'&with_genres='+genres)
        movie.append(response.json())
    return render_template("genres.html",data=movie)

@app.route('/graph')
def graph():
    response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=d4db5c0d2cdc601df925e6de360e6bbb&language=en-US&sort_by=revenue.desc&include_adult=false&include_video=false&page=1')
    movie = response.json()
    movie_name = [x['original_title'] for x in movie['results']]
    movie_income = [x['vote_average'] for x in movie['results']]
    rng = pd.date_range('1/1/2020', periods=128, freq='H')
    ts = pd.Series(np.random.randn(len(rng)), index=rng)

    graphs = [
        dict(
            data=[
                dict(
                    x=movie_name,  # <-------- x
                    y=movie_income,      # <-------- y
                    type='bar'
                ),
            ],
            layout=dict(
                title='bar-graph'
            )
        ),

        dict(
            data=[
                dict(
                    x=ts.index,
                    y=ts
                )
            ],
            layout=dict(
                title='time-series'
            )
        )
    ]

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           ids=ids,
                           graphJSON=graphJSON)



app.env="development"
app.run(debug=True)


