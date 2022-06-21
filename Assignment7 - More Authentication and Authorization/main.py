from google.cloud import datastore
from flask import Flask, request, jsonify, render_template
import json
import string
import random
import flask
import constants

# now can run locally
import os
from datetime import datetime
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt

from google.auth.transport import requests


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
dclient = datastore.Client()
app = Flask(__name__)


# oauth 2 info stuff
client_id = constants.clientID
client_secret = constants.clientSecret
redirect_uri = constants.redirectURL


# identify users
urls = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']
oauth = OAuth2Session(client_id, redirect_uri = redirect_uri, scope = urls)

@app.route('/')
def index():
	# citation:
	# site: https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html
	# used to create the oauth.authorization_url
	# date: 5/16/2022

	authorization_url, state = oauth.authorization_url(
	'https://accounts.google.com/o/oauth2/auth',
	# access_type and prompt are Google specific extra
	# parameters.
	# https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=499938882837-c6rurjceojlncsj010vfsph7d6aoaukq.apps.googleusercontent.com&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2Foauth&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&state=hjU0ToOUkBxRa3JwRmlLh2QkrLJaGt&access_type=offline&prompt=select_account
	access_type="offline", prompt="select_account")
	print(authorization_url)
	#return '<h1>Welcome</h1>\n <p>Click <a href=%s>here</a> to get your JWT.</p>' % authorization_url
	url = {
		'url' : authorization_url
	}
	return render_template('index.html', data = url)


@app.route('/oauth', methods = ['GET'])
def oauth_data():
	
	token = oauth.fetch_token('https://oauth2.googleapis.com/token', authorization_response=request.url, client_secret=client_secret)
	req = requests.Request()
	print("HIHI", token)
	id_info = id_token.verify_oauth2_token(token['id_token'], req, client_id)

	tokens = {
		'id_token' : token['id_token']
	}

	
	return(jsonify({"jwt" : token['id_token']}), 200)
	#render_template('info.html', data = tokens)


# citation:
# site: https://developers.google.com/identity/sign-in/web/backend-auth
# used to help verify if jwt is correct in each functions below
# date: 5/16/2022

@app.route('/boats', methods = ['POST', "GET"])
def get_post_boats():
	if request.method == 'GET':
		isListPublic = False

		# Get JWT from Authorization header/token
		req = requests.Request()
		jwtInfo = request.headers.get('Authorization')

		# check if jwt is valid. If not only show public boats
		print(jwtInfo)
		if jwtInfo != None:
			jwtInfo = jwtInfo.split(" ")[1]
			try:
				jwtClaim = id_token.verify_oauth2_token(jwtInfo, req, client_id)['sub']
			except:
				isListPublic = True
		else:
			isListPublic = True

		# find elements in database
		query = dclient.query(kind=constants.boat)

		if isListPublic:
			query.add_filter("public", "=", True)
		else:
			query.add_filter("owner", "=", jwtClaim)

		results = list(query.fetch())

		# Add entity id for each boat
		for e in results:
			e["id"] = e.key.id

		return (jsonify(results), 200)

	elif request.method == 'POST':
		# Get JWT from Authorization header/token
		req = requests.Request()
		jwtInfo = request.headers.get('Authorization')

		# check if jwtInfo is given
		if jwtInfo != None:
			jwtInfo = jwtInfo.split(" ")[1]
			print(jwtInfo)
			# print(req)
			# print(client_id)

			# if JWT is valid save the 'sub' value
			try:
				jwtClaim = id_token.verify_oauth2_token(jwtInfo, req, client_id)['sub']
			
			# if JWT is not valid return 401
			except:
				return('Could not verify JWT is valid!\n', 401)
		
		else:
			return (jsonify('No JWT was given!'), 401)

		# Grab content from request body
		content = request.get_json()

		# checking if body is valid (shouldent need to be validated)
		if len(content) != 4:
			return (jsonify({"Error": "The request object is missing at least one of the required attributes (name, type, length or public)"}), 400)

		# Create a new boat entity
		# boat name uniqueness is not enforced
		new_boat = datastore.entity.Entity(key=dclient.key(constants.boat))
		new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"], "public": content["public"], "owner": jwtClaim})
		
		# put boat into datastore (dclient)
		dclient.put(new_boat)

		# Return boat
		return (jsonify({"id": new_boat.key.id, "name": content["name"], "type": content["type"], "length": content["length"], "public": content["public"], "owner": jwtClaim}), 201)

	else:
		return 'Method not recogonized'



@app.route('/boats/<boat_id>', methods=['DELETE'])
def delete_boat(boat_id):
	if request.method == 'DELETE':
		# Get JWT from Authorization header/token
		req = requests.Request()
		jwtInfo = request.headers.get('Authorization')
		
		# checking jwtInfo
		if jwtInfo != None:
			jwtInfo = jwtInfo.split(" ")[1]
			
			# Check to see if JWT is valid
			try:
				jwtClaim = id_token.verify_oauth2_token(jwtInfo, req, client_id)['sub']
			except:
				return('Could not verify JWT!\n', 401)
		else:
			# Now JWT was given
			return (jsonify('No JWT was given!'), 401)
		
		# find boat with boat_id
		boat_key = dclient.key(constants.boat, int(boat_id))
		boat = dclient.get(key=boat_key)

		# error if no boat at id
		if boat == None:
			return (jsonify({'Error': 'No boat with this boat_id exists'}), 403)
		
		# error if the JWT ownter does not own the boat
		elif boat['owner'] != jwtClaim:
			return (jsonify({'Error': 'This boat is owned by someone else!'}), 403)

		# Delete boat from Datastore
		dclient.delete(boat_key)
		return (jsonify({'Result': 'Deleted the boat'}), 204)



@app.route('/owners/<owner_id>/boats', methods=['GET'])
def get_owner_of_boats(owner_id):
	if request.method == 'GET':
		# Search the database for all boats with the owner_id and that are public
		query = dclient.query(kind=constants.boat)

		# filters out owner by id and the boats that are public
		query.add_filter("owner", "=", owner_id)
		query.add_filter("public", "=", True)

		# return the boats that meet both requrments
		results = list(query.fetch())

		# add new id for each boat
		for e in results:
			e["id"] = e.key.id

		return (jsonify(results), 200)


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)