import riak
from config import RIAK_HOST, RIAK_PORT, DATE_FORMAT
import time


def convert_form_to_job(form):
    return {
        'name':form['name'].strip(),
        'sources': form.getlist('sources'),
        'time': form['time'].strip(),
        'location': form['location'].strip() if len(form['location'].strip()) > 0 else None,
        'lat':float(form['lat'].strip()) if len(form['lat'].strip()) > 0 else None,
        'lon':float(form['lon'].strip()) if len(form['lon'].strip()) > 0 else None,
        'distance':float(form['distance'].strip()) if len(form['distance'].strip()) > 0 else 1,
        'tags': form['tags'].strip().split()
    }

def validate_job(job):
    if job['name'] is None or len(job['name']) == 0:
        return "Name is required"

    if job['time'] is None or len(job['time']) == 0:
        return "Since is required"

    try:
        time.strptime(job['time'], DATE_FORMAT)
    except:
        return "Dates must be in the format 21/12/2012 16:30"

    return None

def get_job(job_name):
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    return bucket.get(job_name).get_data()

def save_job(job):
    dt = time.strptime(job['time'], DATE_FORMAT)
    job['time'] = int(time.strftime('%s',dt))

    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')

    value = bucket.new(job['name'], data=job)
    value.store()

def get_jobs():
    client = riak.RiakClient(host=RIAK_HOST, port=RIAK_PORT)
    bucket = client.bucket('jobs')
    return bucket.get_keys()


def process_job(processor, job):
    results = processor.get_keys(job)

    if results:
        return processor.get_data(results)

    return None

