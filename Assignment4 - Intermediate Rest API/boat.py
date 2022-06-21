from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# /boats
@bp.route('', methods=['POST','GET'])
def boats_get_post():
	# Add a boat
	if request.method == 'POST':
		content = request.get_json()
		#check if everything is in content
		if len(content) != 3:
			return (jsonify({"Error": "The request object is missing at least one of the required attributes"}), 400)
		new_boat = datastore.entity.Entity(key=client.key("boats"))

		new_boat.update({'name': content['name'], 'type': content['type'], 'length': content['length'], 'loads': []})
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
			for single_load in e['loads']:
				i = single_load['id']
				selfurl = str(request.url_root) + 'loads/'  + str(i)
				e['loads'] = {
					"id" : i,
					"self" : selfurl
				}
			    #single_load['self'] = request.url_root + "loads/" + str(single_load['id'])


		output = {"boats": results}

		if next_url:
			output["next"] = next_url

		return (jsonify(output),200)
		
	else:
		return 'Method not recogonized'

# /boats/<boat_id>
@bp.route('/<boat_id>', methods=['DELETE','GET'])
def boats_get_delete(boat_id):
	# DELETE boat at boat_id
	if request.method == 'DELETE':
		key = client.key("boats", int(boat_id))
		boat = client.get(key=key)
		if boat == None:
			return (jsonify({"Error": "No boat with this boat_id exists"}), 404)
		if len(boat['loads']) > 0:
			for load in boat['loads']:
				load_obj = client.get(key=client.key("loads", load['id']))
				load_obj['carrier'] = None
				client.put(load_obj)
		client.delete(key)
		return (jsonify(''),204)

	# GET boat information from boat_id
	elif request.method == 'GET':
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)

		if boat == None:
			x = {
					"Error": "No boat with this boat_id exists"
				}
			a_ll = json.dumps(x)
			return (a_ll, 404)

		print(boat['loads'])
		i= boat['loads']
		#i = boat['loads'].keys()
		#print("keys", boat['loads'].keys())
		#print("h", boat['loads'][0])
		y = request.url_root+ 'loads/' 
		print(i)
		print("hi", y)
		for load in boat['loads']:
			i = load['id']
			print(i)
			selfurl= str(request.url_root) + 'loads/'  + str(i)
			boat['loads'] = {
				"id" : i,
				"self" : selfurl
			}

			# new_boat = datastore.entity.Entity(key=client.key("boats"))
			# new_boat.update({"id" : i, "selfload" : new_self})
			# client.put(new_boat)

		boat["id"] = boat_id
		boat["self"] = request.url
		return (jsonify(boat), 200)

	else:
		return ('No boat with this boat_id exists', 404)

# /boat/<boat_id>/loads/<load_id>
@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT','DELETE'])
def add_delete_reservation(boat_id, load_id):
	if request.method == 'PUT':
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)
		load_key = client.key("loads", int(load_id))
		load = client.get(key=load_key)
		if boat == None or load == None:
			#THIhe specified boat and/or load does not exist"
			return (jsonify({"Error": "The specified boat and/or load does not exist"}), 404)
		if load['carrier'] != None:
			return (jsonify({"Error": "The load is already loaded on another boat"}), 403)
		if 'loads' in boat.keys():
			for loads in boat['loads']:
				if loads['id'] == load.key.id:
					return(jsonify({"Error": "Load already assigned to boat"}), 403)
			boat['loads'].append({"id": load.key.id})
			load['carrier'] = {"id": boat.key.id, "name": boat["name"]}
		else:
			boat['loads'] = {"id": load.key.id}
			load['carrier'] = {"id": boat.key.id, "name": boat["name"]}
		client.put(boat)
		client.put(load)
		return(jsonify(''), 204)
	if request.method == 'DELETE':
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)
		load_key = client.key("loads", int(load_id))
		load = client.get(key=load_key)
		if boat == None or load == None:
			return (jsonify({"Error": "No boat with this boat_id is loaded with the load with this load_id"}), 404)
		if load['carrier'] == None or load['carrier']['id'] != boat.key.id:
			return (jsonify({"Error": "No boat with this boat_id is loaded with the load with this load_id"}), 404)
		if 'loads' in boat.keys():
			boat['loads'].remove({"id": load.key.id})
			load['carrier'] = None
			client.put(boat)
			client.put(load)
		return(jsonify(''),204)

# /boat/<boat_id>/loads
@bp.route('/<boat_id>/loads', methods=['GET'])
def boats_get_loads(boat_id):
	boat_key = client.key("boats", int(boat_id))
	boat = client.get(key=boat_key)
	if boat == None:
		print("hi1")
		x = {
			"Error": "No boat with this boat_id exists"
		}
		a_ll = json.dumps(x)
		return (a_ll,404)
	print(boat['loads'])
	load_num = boat['loads']
	i = load_num[0]
	#print(i['id'])
	#print(type(load_num))
	if load_num != None:
		load_key =  client.key(constants.loads, int(i['id']))
		load = client.get(key = load_key)
		if load == None:
			x = {
				"Error": "No load with this load_id exists"
			}
			a_ll = json.dumps(x)
			return (a_ll, 404)
		#if load["carrier"]:
		#    load["carrier"]["self"] = request.url_root + "boats/" + load["carrier"]["id"]
		load["id"] = load_num
		load["self"] = request.url
		
		#return (jsonify(boat), 200)
		return (jsonify(load), 200)
	else:
		return (jsonify([]), 200)