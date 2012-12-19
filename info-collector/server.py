from flask import Flask, jsonify, request,render_template, abort, url_for, redirect
import util
from pluginmanager import list_plugins
from config import *
app = Flask(__name__)

def request_wants_json():
    best = request.accept_mimetypes\
    .best_match(['application/json', 'text/html'])
    return best == 'application/json' and\
           request.accept_mimetypes[best] >\
           request.accept_mimetypes['text/html']

def convert_to_json(form):
    return {
        'name':form['name'].strip(),
        'sources': form['sources'],
        'location': form['location'].strip(),
        'lat':form['lat'].strip(),
        'lon':form['lon'].strip(),
        'distance':form['distance'].strip(),
        'tags': form['tags'].strip()
    }

def validate_job(job):
    if job['name'] is None or len(job['name']) == 0:
        return "Name is required"

    return None


@app.route("/")
def index():
    jobs = util.get_jobs()

    if request_wants_json():
        return jsonify(jobs)
    else:
        return render_template('index.html', jobs=jobs)

@app.route('/create')
def create():
    if request.method == 'POST':

        job = convert_to_json(request.form)
        message = validate_job(job)

        if validate_job(job) is None:
            util.save_job(job)
            redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        return render_template('edit.html', sources=sources, job=None)


@app.route('/edit/<job_name>')
def edit(job_name):
    if request.method == 'POST':

        job = convert_to_json(request.form)
        message = validate_job(job)

        if validate_job(job) is None:
            util.save_job(job)
            redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        return render_template('edit.html', sources=sources, job=util.get_job(job_name))

@app.route('/jobs/<job_name>')
def job(job_name):

    results = util.get_keys(job_name)

    if results is None:
        abort(404)
    else:
        data = util.get_data(results[0],results[1],results[2],results[3])

        if request_wants_json():
            return jsonify(data)
        else:
            return render_template('items.html', data=data, job_name=job_name)


if __name__ == "__main__":
    app.run(port=SERVER_PORT)
