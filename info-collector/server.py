from flask import Flask, jsonify, request,render_template, abort, url_for, redirect, json
import datetime
import jobops
from processors import simple
from pluginmanager import list_plugins
from config import *
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
    jobs = jobops.get_jobs()

    for job in jobs:
        job['time'] = datetime.datetime.fromtimestamp(job['time']).strftime(DATE_FORMAT)

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
            jobops.save_job(job)
            redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        return render_template('edit.html', sources=sources, job=None)


@app.route('/edit/<job_name>', methods=['GET', 'POST'])
def edit(job_name):
    if request.method == 'POST':

        if request_wants_json():
            job = json.dumps(request.json)
        else:
            job = jobops.convert_form_to_job(request.form)

        message = jobops.validate_job(job)

        if message is None:
            jobops.save_job(job)
            redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        job = jobops.get_job(job_name)
        if job:
            job['time'] = datetime.datetime.fromtimestamp(job['time']).strftime(DATE_FORMAT)

        return render_template('edit.html', sources=sources, job=job)

@app.route('/jobs/<job_name>')
def job(job_name):

    data = jobops.process_job(simple.SimpleProcessor(), jobops.get_job(job_name))

    if data is None:
        abort(404)
    else:
        if request_wants_json():
            return jsonify(data)
        else:
            return render_template('items.html', data=data, job_name=job_name)


if __name__ == "__main__":
    app.run(port=SERVER_PORT)
