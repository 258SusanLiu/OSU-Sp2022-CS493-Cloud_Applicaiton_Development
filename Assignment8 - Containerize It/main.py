from google.cloud import datastore
from flask import Flask, request, render_template
import json
import constants
import boat

#pip freeze > requirements.txt

app = Flask(__name__)
app.register_blueprint(boat.bp)

@app.route('/')
def index():
    return render_template('index.html')
    #return "Welcome! Please navigate to /boats to use this API"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)