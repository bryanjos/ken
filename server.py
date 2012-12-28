from flask import Flask, jsonify, request,render_template, abort, url_for, redirect, json, Response
import datetime
import jobops
from processors import simple
from pluginmanager import list_plugins
from config import *
from serverops import *
import redis

app = Flask(__name__)
app.config.from_object('config')


def request_wants_json():
    best = request.accept_mimetypes\
    .best_match(['application/json', 'text/html'])
    return best == 'application/json' and\
           request.accept_mimetypes[best] >\
           request.accept_mimetypes['text/html']


@app.route("/about")
def about():
    return render_template('about.html', version=VERSION, plugins=', '.join(list_plugins()))

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
                return redirect(url_for('index'))
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
                return redirect(url_for('index'))
        else:
            return message


    else:
        sources = list_plugins()
        job = jobops.get_job(job_slug)
        if job:
            job.time = datetime.datetime.fromtimestamp(job.time).strftime(DATE_FORMAT)
            job.tags = ' '.join(job.tags)

        return render_template('edit.html', sources=sources, job=job)

@app.route('/jobs/<job_slug>/', defaults={'page': 1})
@app.route('/jobs/<job_slug>/<int:page>')
def job(job_slug, page=1):

    job =  jobops.get_job(job_slug)
    data = jobops.process_job(simple.SimpleProcessor(), job, 30, page)

    import datetime
    for d in data:
        d.time = datetime.datetime.fromtimestamp(d.time).strftime("%a, %d %b %Y %H:%M:%S +0000")
        d.data = d.data.decode('ascii','ignore')
        d.coordinate_string = '%s %s' % (d.lat, d.lon) if d.lat > 0.0 and d.lon > 0.0 else ''

    if data is None:
        abort(404)
    else:
        print data
        if request_wants_json():
            return jsonify(data)
        else:
            return render_template('items.html', data=data, job_name=job.name, job_slug=job.slug)


def event_stream(job_slug):
    red = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    pub_sub = red.pubsub()
    pub_sub.subscribe(job_slug)
    for message in pub_sub.listen():
        yield 'data: %s\n\n' % message['data']





@app.route('/stream/<job_slug>')
def stream(job_slug):
    return Response(event_stream(job_slug), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(port=SERVER_PORT, threaded=True)
