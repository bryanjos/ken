from flask import Flask, jsonify, request,render_template, abort, url_for, redirect, json
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import datetime
import jobops
from processors import simple
from pluginmanager import list_plugins
from config import *
from serverops import *

app = Flask(__name__)
app.config.from_object('config')


def request_wants_json():
    best = request.accept_mimetypes\
    .best_match(['application/json', 'text/html'])
    return best == 'application/json' and\
           request.accept_mimetypes[best] >\
           request.accept_mimetypes['text/html']


@app.route("/")
def index():
    jobs = jobops.get_job_keys_and_names()

    if request_wants_json():
        return jsonify(jobs)
    else:
        return render_template('index.html', jobs=jobs)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':

        if request_wants_json():
            job = json.dumps(request.json)
        else:
            job = jobops.convert_form_to_job(request.form)

        message = jobops.validate_job(job)

        if message is None:
            print 'message: %s' % message
            job['slug'] = slugify(job['name'],jobops.get_job_keys())
            jobops.save_job(job)

            if request_wants_json():
                return "OK"
            else:
                redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        return render_template('edit.html', sources=sources, job=None)


@app.route('/edit/<job_slug>', methods=['GET', 'POST'])
def edit(job_slug):
    if request.method == 'POST':

        if request_wants_json():
            job = json.dumps(request.json)
        else:
            job = jobops.convert_form_to_job(request.form)

        message = jobops.validate_job(job)

        if message is None:
            job['slug'] = job_slug
            jobops.save_job(job)

            if request_wants_json():
                return "OK"
            else:
                redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        job = jobops.get_job(job_slug)
        if job:
            job['time'] = datetime.datetime.fromtimestamp(job['time']).strftime(DATE_FORMAT)

        return render_template('edit.html', sources=sources, job=job)

@app.route('/jobs/<job_slug>/', defaults={'page': 1})
@app.route('/jobs/<job_slug>/<int:page>')
def job(job_slug, page=1):

    job =  jobops.get_job(job_slug)
    data = jobops.process_job(simple.SimpleProcessor(), job, 30, page)

    if data is None:
        abort(404)
    else:
        print data
        if request_wants_json():
            return jsonify(data)
        else:
            return render_template('items.html', data=data, job_name=job['name'], job_slug=job['slug'])


@app.route('/api/<job_slug>')
def api(job_slug):
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            job =  jobops.get_job(job_slug)
            if message['page']:
                data = jobops.process_job(simple.SimpleProcessor(), job, 30, message['page'])
            else:
                data = jobops.process_job(simple.SimpleProcessor(), job, 30, 1)

            ws.send(data)
    return

@app.route('/api/<job_slug>/update')
def api(job_slug):
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            job =  jobops.get_job(job_slug)
            if message['time']:
                data = jobops.process_job_since(simple.SimpleProcessor(), job, message['time'])
            else:
                data = jobops.process_job_since(simple.SimpleProcessor(), job, message['time'])

            ws.send(data)
    return


if __name__ == "__main__":
    http_server = WSGIServer(('',SERVER_PORT), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
