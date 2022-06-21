import datetime
import random
from flask import Flask, render_template

from google.cloud import datastore

app = Flask(__name__)


@app.route('/')
def root():
    # Store the current access time in Datastore.
    store_time(datetime.datetime.now(tz=datetime.timezone.utc))

    store_guineapig(random.randint(1,75),datetime.datetime.now(tz=datetime.timezone.utc))

    # Fetch the most recent 10 access times from Datastore.
    times, times1 = fetch_times(10)
    print("Times1:", times1)
    print("Times:", times)
    return render_template('index.html', times=times,  times1=times1, pie="Hi")


datastore_client = datastore.Client()

def store_guineapig(t,dt):
    print("Random int:", t)
    if 1 <= t <= 5:
        piggie = "Butter (Abyssinian Guinea pig)"
    elif 6 <= t <= 10:
        piggie = "Trixi (Teddy Guinea Pig)"
    elif 11 <= t <= 15:
        piggie = "Cleo (Texel Guinea Pig)"
    elif 16 <= t <= 20:
        piggie = "Bacon (American Crested Guinea Pig)"
    elif 21 <= t <= 25:
        piggie = "Ava (Himalayan Guinea Pig)"
    elif 26 <= t <= 30:
        piggie = "Sol (Cuy Guinea Pig)"
    elif 31 <= t <= 35:
        piggie = "Milo (Sheltie Guinea Pig)"
    elif 36 <= t <= 40:
        piggie = "Tiny (Cornet Guinea Pig)"
    elif 41 <= t <= 45:
        piggie = "Max (English Crested Guinea Pig)"
    elif 46 <= t <= 50:
        piggie = "Nugget (Peruvian Guinea Pig)"
    elif 51 <= t <= 55:
        piggie = "Finn (Rex Guinea Pig)"
    elif 56 <= t <= 60:
        piggie = "Jinx (Silkie Guinea Pig)"
    elif 61 <= t <= 65:
        piggie = "Coco (Baldwin Guinea Pig)"
    elif 66 <= t <= 75:
        piggie = "Teddy (Merino Guinea Pig)"

    print("In guinea pig", piggie)
    i = datastore.Entity(key=datastore_client.key('pet'))    
    

    i.update({
        'guineapig': piggie,
        'timestamp' : dt
    })
    print("i", i)

    datastore_client.put(i)


def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_times(limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']
    times = query.fetch(limit=limit)

    query1 = datastore_client.query(kind='pet')
    query1.order = ['-timestamp']
    #query1.order = ['-guineapig']
    #query1.order = ['-__key__']
    #query1.order = ['-pet'] 
    times1 = query1.fetch(limit=limit)

    return times, times1

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True