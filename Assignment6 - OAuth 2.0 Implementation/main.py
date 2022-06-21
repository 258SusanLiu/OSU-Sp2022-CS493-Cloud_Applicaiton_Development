from google.cloud import datastore
from flask import Flask, request, jsonify, render_template, redirect, session
import json
import requests
import string
import random
import flask
import constants
from datetime import datetime
from google.cloud import datastore
datastore_client = datastore.Client()

app = Flask(__name__)
client = datastore.Client()

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

mestring = randomString(10)
@app.route('/')
def index():
	global state
	# global keyID
	state = randomString(10)
	# https://joining-in.uw.r.appspot.com/
	link = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=499938882837-c6rurjceojlncsj010vfsph7d6aoaukq.apps.googleusercontent.com&redirect_uri=https://working-joinin.uw.r.appspot.com/oauth&scope=email"
	endl = "%20profile&state=" + state
	fullurl = link+endl
	print("FULL URL", fullurl)
	print("STATE: ", state)
	x = {
		'fullurl' : fullurl,
		'state' : state,
		'time' : datetime.now().strftime("%H:%M:%S")
	}
	i = datastore.Entity(key=datastore_client.key('state'))

	i.update(x)

	datastore_client.put(i)	
	return render_template('index.html', data=x)
	

@app.route('/oauth', methods = ['GET'])
def oauth_data():
	if request.method == 'GET':
		# info_key = client.key("state", state)
		# info = client.get(key=info_key)
		# #info["state"] = state
		# print("info_key1", info)

		# print("STATE: ", state)
		# #if keyID !- 
		
		data = {
			'client_id': "499938882837-c6rurjceojlncsj010vfsph7d6aoaukq.apps.googleusercontent.com",
			'grant_type': 'authorization_code',
			'client_secret': "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",
			'redirect_uri': "https://working-joinin.uw.r.appspot.com/oauth",
			'code' : request.args.get('code')
		}

		#print("Hi\n", data['code'])
		#https://accounts.google.com/o/oauth2/v2/auth
		#responsive = requests.post("https://www.googleapis.com/oauth2/v4/token", data=data, verify=False) 
		#content = responsive.json()
		responsive = requests.post("https://oauth2.googleapis.com/token", data=data, verify=False)
		#print("RES", responsive)
		new_content = responsive.json()
		#print("JSON ", new_content)
		token= new_content['access_token']
		#print(new_content["scope"])
		print("TOKEN", token)

		headers = {
			'Authorization' : 'Bearer {}'.format(token)
		}
		new_response = requests.get("https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses", headers=headers)
		new_content = new_response.json()
		
		print("\n")
		print(new_content)
		print("\n")
		
		info = {
			'names' : new_content['names'],
			'emailAddresses' : new_content['emailAddresses'],
			'state' : state
		}
		return render_template('info.html', data = info)

@app.errorhandler(404)
def errors(e):
	return json.dumps({"Error": "Page does not exist"}), 404, {"Content-Type": "application/json"}

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)