from flask import Flask, url_for, request
import riak
import psycopg2
from config import *
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route('/create')
def create():
    if request.method == 'POST':
        pass
    else:
        pass

@app.route('/edit/<job_name>')
def edit(job_name):
    if request.method == 'POST':
        pass
    else:
        pass

@app.route('/jobs/<job_name>')
def job(job_name):
    client = riak.RiakClient(port=RIAK_PORT)
    bucket = client.bucket('jobs')

    job = bucket.get(job_name).get_data()

    if job is None:
        return {}


    conn = psycopg2.connect(POSTGRES_DB_STRING)
    cur = conn.cursor()
    cur.execute("SELECT * FROM information where ;")


if __name__ == "__main__":
    app.run(port=SERVER_PORT)
