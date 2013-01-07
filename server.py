from flask import Flask, jsonify, request,render_template, url_for, redirect, json, Response
import datetime
import jobops
from pluginmanager import list_plugins
from config import *
import re
import redis
from pymongo import *
from geo_atom import GeoAtomFeed

app = Flask(__name__)
app.config.from_object('config')

def request_wants_json():
    best = request.accept_mimetypes\
    .best_match(['application/json', 'text/html'])
    return best == 'application/json' and\
           request.accept_mimetypes[best] >\
           request.accept_mimetypes['text/html']



_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value, job_slugs):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    slug = _slugify_hyphenate_re.sub('-', value)
    count = 0

    for key in job_slugs:
        if slug in key:
            count = count + 1

    if count > 0:
        slug = slug + str(count)

    return slug


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
@app.route('/edit/<job_slug>', methods=['GET', 'POST'])
def edit(job_slug = None):
    if request.method == 'POST':

        if request_wants_json():
            job = json.dumps(request.json)
        else:
            job = jobops.convert_form_to_job(request.form)

        message = jobops.validate_job(job)

        if message is None:
            if job_slug is None:
                job['slug'] = slugify(job['name'],jobops.get_job_keys())
            else:
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
        if job_slug:
            job = jobops.get_job(job_slug)
            if job:
                job.time = datetime.datetime.fromtimestamp(job.time).strftime(DATE_FORMAT)
                job.tags = ','.join(job.tags)

            return render_template('edit.html', sources=sources, job=job)
        else:
            return render_template('edit.html', sources=sources, job=None)

@app.route('/<job_slug>.atom')
@app.route('/<job_slug>.atom/<time>')
def job_feed(job_slug,time=None):
    job = jobops.get_job(job_slug)
    feed = GeoAtomFeed(job.name, feed_url=request.url, url=request.url_root )
    articles = get_data(job_slug, time)
    for article in articles:
        if len(article['coordinate_string']) > 0:
            lat_lon = [str(article['coordinates']['lat']), str(article['coordinates']['lon'])]
        else:
            lat_lon = None

        feed.add(article['data'][:10] + '...', unicode(article['data']),
            content_type='html',
            author=article['source'] + '/' + article['creator'],
            id=article['id'],
            url='',
            updated=article['time'],
            published=article['time'],
            lat_lon=lat_lon)
    Response.content_type = 'application/atom+xml; charset=utf-8'
    return feed.get_response()


def get_data(job_slug, time=None):
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    db = connection['ken']
    collection = db['job_info']

    if time is None:
        articles = collection.find(
            {
                "job_slug": job_slug
            }
        ).limit(PAGE_COUNT).sort("time", DESCENDING)
    else:
        time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
        articles = collection.find(
            {
                "time": {"$lt": time },
                "job_slug": job_slug
            }
        ).limit(PAGE_COUNT).sort("time", DESCENDING)

    return articles

@app.route('/jobs/previous/<job_slug>', methods=['POST'])
def get_previous_info(job_slug):
    time = datetime.datetime.strptime(request.form['time'], '%Y-%m-%dT%H:%M:%S+00:00')

    results = get_data(job_slug, time)

    data = []

    for item in results:
        data.append({
            'source': item['source'],
            'creator': item['creator'],
            'time': item['time'].strftime('%Y-%m-%dT%H:%M:%S+00:00'),
            'data': item['data'],
            'coordinate_string': item['coordinate_string']
        })

    print 'data: %s' % json.dumps(data)

    return json.dumps(data)


@app.route('/jobs/<job_slug>')
def job(job_slug):
    job = jobops.get_job(job_slug)
    return render_template('items.html', data=[], job_name=job.name, job_slug=job.slug)


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
