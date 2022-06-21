from flask import Blueprint, request, jsonify, render_template
from google.cloud import datastore
import json
import constants
from json2html import *

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# /boats
@bp.route('', methods=['POST', 'GET'])
def boats_get_post():
	# Add a boat
	if request.method == 'POST':
		content = request.get_json()

		#check if everything is in content
		if len(content) != 3:
			return (jsonify({"Error": "The request object is missing at least one of the required attributes"}), 400)
		new_boat = datastore.entity.Entity(key=client.key("boats"))

		new_boat.update({'name': content['name'], 'type': content['type'], 'length': content['length']})
		client.put(new_boat)
		new_boat['id'] = new_boat.key.id
		new_boat['self'] = request.url + '/' + str(new_boat.key.id)
		return (jsonify(new_boat), 201)

	# GET all obats
	elif request.method == 'GET':
		query = client.query(kind=constants.boats)
		query_limit = int(request.args.get('limit', '3'))
		query_offset = int(request.args.get('offset', '0'))
		list_iterator = query.fetch(limit = query_limit, offset = query_offset)
		pages = list_iterator.pages
		
		results = list(next(pages))

		if list_iterator.next_page_token:
			next_offset = query_offset + query_limit
			next_url = request.base_url + "?limit=" + str(query_limit) + "&offset=" + str(next_offset)

		else:
			next_url = None

		for e in results:
			e["id"] = e.key.id
			e["self"] = request.url + '/' + str(e.key.id)
			print(e["self"])
		# 	for single_load in e['loads']:
		# 		i = single_load['id']
		# 		selfurl = str(request.url_root) + 'loads/'  + str(i)
		# 		e['loads'] = {
		# 			"id" : i,
		# 			"self" : selfurl
		# 		}
		# 	    #single_load['self'] = request.url_root +loads/" + str(single_load['id'])


		output = {"boats": results}

		if next_url:
			output["next"] = next_url

		outputs = jsonify(output)
		
		#print(json2html.convert(json = output))
		#return (jsonify(output),200)
		#return json2html.convert(json = output)
		return (render_template('list.html', data = json.dumps(output, indent = 4)))
		
	else:
		return 'Method not recogonized'

# /boats/<boat_id>
@bp.route('/<boat_id>', methods=['GET'])
def boats_get_delete(boat_id):
	# # DELETE boat at boat_id
	# if request.method == 'DELETE':
	# 	key = client.key("boats", int(boat_id))
	# 	boat = client.get(key=key)
	# 	if boat == None:
	# 		return (jsonify({"Error": "No boat with this boat_id exists"}), 404)
	# 	if len(boat['loads']) > 0:
	# 		for load in boat['loads']:
	# 			load_obj = client.get(key=client.key("loads", load['id']))
	# 			load_obj['carrier'] = None
	# 			client.put(load_obj)
	# 	client.delete(key)
	# 	return (jsonify(''),204)

	# GET boat information from boat_id
	if request.method == 'GET':
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)

		if boat == None:
			x = {
					"Error": "No boat with this boat_id exists"
				}
			a_ll = json.dumps(x)
			return (a_ll, 404)

		# print(boat['loads'])
		# i= boat['loads']
		# #i = boat['loads'].keys()
		# #print("keys", boat['loads'].keys())
		# #print("h", boat['loads'][0])
		# y = request.url_root+ 'loads/' 
		# print(i)
		# print("hi", y)
		# for load in boat['loads']:
		# 	i = load['id']
		# 	print(i)
		# 	selfurl= str(request.url_root) + 'loads/'  + str(i)
		# 	boat['loads'] = {
		# 		"id" : i,
		# 		"self" : selfurl
		# 	}

			# new_boat = datastore.entity.Entity(key=client.key("boats"))
			# new_boat.update({"id" : i, "selfload" : new_self})
			# client.put(new_boat)

		boat["id"] = boat_id
		boat["self"] = request.url
		#return (jsonify(boat), 200)
		jsonify(boat)
		print(boat)
		#return (render_template('list.html', data = json.dumps(output, indent = 4)
		return (render_template('info.html', data = json.dumps(boat, indent=4)),200)

	else:
		return ('No boat with this boat_id exists', 404)
