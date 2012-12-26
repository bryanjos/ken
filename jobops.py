import riak
from config import RIAK_HOST, RIAK_PORT, DATE_FORMAT
import time
from job import Job


def convert_form_to_job(job_form):
    return {
        'name':job_form['name'].strip(),
        'time': job_form['time'].strip(),
        'lat':float(job_form['lat'].strip()) if len(job_form['lat'].strip()) > 0 else None,
        'lon':float(job_form['lon'].strip()) if len(job_form['lon'].strip()) > 0 else None,
        'distance':float(job_form['distance'].strip()) if len(job_form['distance'].strip()) > 0 else 1,
        'tags': job_form['tags'].strip().split()
    }

def validate_job(job_json):
    if job_json['name'] is None or len(job_json['name']) == 0:
        return "Name is required"

    if job_json['time'] is None or len(job_json['time']) == 0:
        return "Since is required"

    try:
        time.strptime(job_json['time'], DATE_FORMAT)
    except:
        return "Dates must be in the format 21/12/2012 16:30"

    return None

def get_job(job_slug):
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    job = bucket.get(job_slug).get_data()
    if job is None:
        return None

    return Job(job['name'], job['slug'], job['time'], job['tags'], job['lat'], job['lon'], job['distance'])

def save_job(job):
    dt = time.strptime(job['time'], DATE_FORMAT)
    job['time'] = int(time.strftime('%s',dt))

    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    value = bucket.new(job['slug'], data=job)
    value.store()

def get_job_keys():
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    return bucket.get_keys()

def get_job_keys_and_names():
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    keys = bucket.get_keys()
    keys_and_names = []

    for key in keys:
        job = bucket.get(key).get_data()
        keys_and_names.append({
            'slug': job['slug'],
            'name': job['name']
        })


    return keys_and_names


def get_jobs():
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    keys = bucket.get_keys()
    jobs = []

    for key in keys:
        job = bucket.get(key).get_data()
        jobs.append(Job(job['name'], job['slug'], job['time'], job['tags'], job['lat'], job['lon'], job['distance']))


    return jobs


def process_job(processor, job, page_size, page):
    results = processor.get_keys(job)

    if results:
        return processor.get_data(results, page_size, page)

    return None

def process_job_since(processor, job, since):
    results = processor.get_keys(job)

    if results:
        return processor.get_data_since(results, since)

    return None

