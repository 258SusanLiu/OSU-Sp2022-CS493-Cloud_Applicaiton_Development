from flask import Blueprint, request, jsonify, make_response
from google.cloud import datastore
import json
import constants
from json2html import *

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')


def check_name(results, nameStr):
	for object in results:
		if object['name'] == nameStr:
			return True
	return False

def valid_input(input, value):
	if input == "name":
		if len(value) > 16:
			return False
		for i in value:
			if ((i >= 'a' and i <= 'z')) or (i >= 'A' and i <= 'Z'):
				continue
			if (i == ' '):
				continue
			else:
				return False
		return True
	elif input == "type":
		if len(value) > 16:
			return False
		for i in value:
			if ((i >= 'a' and i <= 'z')) or (i >= 'A' and i <= 'Z'):
				continue
			if (i == ' '):
				continue
			else:
				return False
		return True
	elif input == "length":
		change = str(value)
		if len(str(value)) > 7:
			return False
		for i in change:
			try:
				if (int(i) > 9 or int(i) < 0):
					return False
			except:
				return False
		return True
	else:
		return 'Invalid attribute given'

def check_id_valid(results, id):
	for object in results:
		if id == 'null':
			break
		if object.id == int(id):
			return True
	return False

def count_valid(content):
	count = 0
	if "name" in content:
		count += 1
	if "lenght" in content:
		count += 1
	if "type" in content:
		count += 1
	return count


# /boats
# 'GET' is optional
@bp.route('', methods=['POST','GET', 'PUT', 'DELETE'])
def boats_get_post():
	# Add a boat
	if request.method == 'POST':
		print("HI")

		content_type = request.headers.get('Content-Type')
		print(content_type)
		# content is not in json format
		if content_type != 'application/json':
			res = make_response()
			res.status_code = 415
			return res
			#return(jsonify({"Error":"This method only accepts JSON"}), 415)


		content = request.get_json()


		#check if everything is in content
		if len(content) != 3:
			return (jsonify({"Error": "The request object is missing at least one of the required attributes"}), 400)
		query = client.query(kind=constants.boats)
		results = list(query.fetch())

		#check if name is unique if not 403
		if (check_name(results, content['name'])==False):
			new_boat = datastore.entity.Entity(key=client.key("boats"))

			if type(content['name']) != str:
				return(jsonify({"Error": "Name cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
			if valid_input('name', content['name']) == True:
				pass
			else:
				return(jsonify({"Error": "Name cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)

			if type(content['type']) != str:
				return(jsonify({"Error": "Type cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
			if valid_input('type', content['type']) == True:
				pass
			else:
				return(jsonify({"Error": "Type cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
			
			if type(content['length']) != int:
				return(jsonify({"Error": "Length cant be longer than 7 digits. It can also only contain numbers"}), 400)
			if valid_input('length', content['length']) == True:
				if type(content['length']) != int:
					return(jsonify({"Error": "Length cant be longer than 7 digits. It can also only contain numbers"}), 400)
			else:
				return(jsonify({"Error": "Length cant be longer than 7 digits. It can also only contain numbers"}), 400)


			new_boat.update({'name': content['name'], 'type': content['type'], 'length': content['length']})
			client.put(new_boat)
			print(new_boat.key.id)
			new_boat['id'] = new_boat.key.id
			new_boat['self'] = request.url + '/' + str(new_boat.key.id)
			return (jsonify(new_boat), 201)
		else:
			return (jsonify({"Error": "Name must be unique"}), 403)

	# GET all obats
	elif request.method == 'GET':
		query = client.query(kind=constants.boats)
		results = list(query.fetch())
		#print("asdfa/sf", request.mimetype)

		if "application/json" in request.accept_mimetypes:
			for e in results:
				e["id"] = e.key.id
				e["self"] = request.url + '/' + str(e.key.id)
				print(e["self"])

			output = {"boats": results}
			return (jsonify(output),200)

		elif "text/html" in request.accept_mimetypes:
			res = make_response(json2html.convert(json = json.dumps(results)))
			res.headers.set('Content-Type', 'text/html')
			res.status_code = 200
			return res

		else:
			return(jsonify({"Error" : "This type is not supported, must be JSON or HTML"}), 406)

	elif request.method == 'PUT' or request.method == 'DELETE':
		return (jsonify({"Error": "Cannot delete or edit the list of all boats"}),405)
		
	else:
		return 'Method not recogonized'

# /boats/<boat_id>
@bp.route('/<boat_id>', methods=['DELETE','GET','PUT','PATCH'])
def boats_get_delete(boat_id):
	# DELETE boat at boat_id
	if request.method == 'DELETE':
		key = client.key("boats", int(boat_id))
		boat = client.get(key=key)
		if boat == None:
			return (jsonify({"Error": "No boat with this boat_id exists"}), 404)

		client.delete(key)
		return (jsonify(''),204)

	# GET boat information from boat_id
	elif request.method == 'GET':
		print(boat_id)
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)

		if boat == None:
			x = {
					"Error": "No boat with this boat_id exists"
				}
			a_ll = json.dumps(x)
			return (a_ll, 404)

		boat["id"] = boat_id
		boat["self"] = request.url

		if 'application/json' in request.accept_mimetypes:
			return (jsonify(boat), 200)
		elif 'text/html' in request.accept_mimetypes:
			res = make_response(json2html.convert(json = json.dumps(boat)))
			res.headers.set('Content-Type', 'text/html')
			res.status_code = 200
			return res
		else:
			return(jsonify({"Error" : "This type is not supported, must be JSON or HTML"}), 406)
	
	# Put boat info into boat from boat_id
	elif request.method == 'PUT':
		content_type = request.headers.get('Content-Type')
		print(content_type)
		# content is not in json format
		if (content_type != 'application/json'):
			res = make_response()
			res.status_code = 415
			return res
			#return(jsonify({"Error":"This method only accepts JSON"}), 415)
		
		content = request.get_json()

		print(boat_id)
		boat_key = client.key("boats", int(boat_id))
		boat = client.get(key=boat_key)

		if boat == None:
			x = {
					"Error": "No boat with this boat_id exists"
				}
			a_ll = json.dumps(x)
			return (a_ll, 404)
		if (not(content)):
			return(jsonify({"Error" : "This method only accepts JSON"}), 415)
		
		# no need to have id in json
		if "id" in content:
			return(jsonify({"Error" : "ID's arent needed"}), 400)
		
		# the needed items in json
		if "name" not in content or "type" not in content or "length" not in content:
			return(jsonify({"Error" : "The request object is missing at least one of the requried attributes"}), 400)
		
		query = client.query(kind = constants.boats)
		results = list(query.fetch())

		# check if the id is valid
		if check_id_valid(results, boat_id) == False:
			return(jsonify({"Error" : "No boat with that ID exists"}), 404)
		
		if type(content['name']) != str:
			return(jsonify({"Error" :"Name must be string"}), 400)
		
		if type(content['type']) != str:
			return(jsonify({"Error" :"Type must be string"}), 400)

		if type(content['length']) != int:
			return(jsonify({"Error" :"Length must be int"}), 400)

		if (check_name(results, content['name']) == False):
			if valid_input('name', content['name']) == True:
				pass
			else:
				return(jsonify({"Error": "Name cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
			
			if valid_input('type', content['type']) == True:
				pass
			else:
				return(jsonify({"Error": "Type cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)

			if valid_input('length', content['length']) == True:
				if type(content['length']) != int:
					return(jsonify({"Error": "Length cant be longer than 7 digits. It can also only contain numbers"}), 400)
			else:
				return(jsonify({"Error": "Length cant be longer than 7 digits. It can also only contain numbers"}), 400)

			print(count_valid(content))#2
			print(len(content))#3
			if count_valid(content) > len(content) and len(content) != 3: 
				return(jsonify({"Error" : "adding too many attributes"}), 400)
			


			boat.update({"name": content["name"], "type": content["type"],"length": content["length"]})
			client.put(boat)
			boat['id'] = int(boat_id)
			boat['self'] = request.base_url
			return (boat, 303)

		else:
			return(jsonify({"Error" : "Name is not unique"}), 403)

	# Update boat info
	elif request.method == 'PATCH':
		print("HI")
		content_type = request.headers.get('Content-Type')
		print(content_type)
		# content is not in json format
		if (content_type != 'application/json'):
			res = make_response()
			res.status_code = 415
			return res
			#return(jsonify({"Error":"This method only accepts JSON"}), 415)

		
		content = request.get_json()
		if "id" in content:
			return(jsonify({"Error" : "no need for id it is same"}), 400)
		
		# print("test", count_valid(content))
		# if count_valid(content) <= 1:
		# 	return(jsonify({"Error" : "Missing at least one of the required attributes"}), 400)

		query = client.query(kind = constants.boats)
		results = list(query.fetch())

		print(check_id_valid(results, boat_id))

		if check_id_valid(results, boat_id) == False:
			return(jsonify({"Error" : "No boat with this boat_id exists"}), 404)
		
		boat_key = client.key(constants.boats, int(boat_id))
		boat = client.get(key = boat_key)
		count = count_valid(content)

		if "name" in content:
			if type(content["name"]) != str:
				return(jsonify({"Error" : "Name must be string"}), 400)
			if valid_input('name', content['name']) == True:
				if (check_name(results, content['name']) == False):
					boat.update({"name" : content['name']})
				else:
					return(jsonify({"Error" : "Name must be unique"}), 403)
			else:
				return(jsonify({"Error" : "Name cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
		
		if "length" in content:
			if type(content["length"]) != int:
				return(jsonify({"Error" : "Length must be integer"}), 400)
			if valid_input('length', content['length']) == True:
				boat.update({'length' : content['length']})
			else:
				return(jsonify({"Error" : "Length cannot be longer than 7 digits. It can also only contain numbers"}), 400)
		
		if "type" in content:
			if type(content["type"]) != str:
				return(jsonify({"Error" : "Type must be string"}), 400)
			if valid_input('type', content['type']) == True:
				boat.update({'type' : content['type']})
			else:
				return(jsonify({"Error" : "Type cannot be longer than 16 characters. It can also only contain letters of the alphabet"}), 400)
		
		client.put(boat)
		boat['id'] = int(boat_id)
		boat['self'] = request.base_url
		return(boat, 200)

	else:
		return ('No boat with this boat_id exists', 404)


# # /boats/html
# @bp.route('/html', methods=['GET'])
# def boats_get_html():
# 	# GET all obats
# 	if request.method == 'GET':
# 		query = client.query(kind=constants.boats)
# 		results = list(query.fetch())
# 		#print("asdfa/sf", request.mimetype)
# 		for e in results:
# 			e["id"] = e.key.id
# 			e["self"] = request.url + '/' + str(e.key.id)
# 			print(e["self"])

# 		if "text/html" in request.accept_mimetypes:
# 			res = make_response(json2html.convert(json = json.dumps(results)))
# 			res.headers.set('Content-Type', 'text/html')
# 			res.status_code = 200
# 			return res

# 		else:
# 			return(jsonify({"Error" : "This type is not supported, must be JSON or HTML"}), 406)
# 	else:
# 		return 'Method not recogonized'


# @bp.route('/<boat_id>/html', methods=['GET'])
# def boats_id_get_html(boat_id):
# 	# GET boat information from boat_id
# 	if request.method == 'GET':
# 		boat_key = client.key("boats", int(boat_id))
# 		boat = client.get(key=boat_key)

# 		if boat == None:
# 			x = {
# 					"Error": "No boat with this boat_id exists"
# 				}
# 			a_ll = json.dumps(x)
# 			return (a_ll, 404)

# 		boat["id"] = boat_id
# 		boat["self"] = request.url

# 		if 'text/html' in request.accept_mimetypes:
# 			res = make_response(json2html.convert(json = json.dumps(boat)))
# 			res.headers.set('Content-Type', 'text/html')
# 			res.status_code = 200
# 			return res
# 		else:
# 			return(jsonify({"Error" : "This type is not supported, must be JSON or HTML"}), 406)
# 	else:
# 		return 'Method not recogonized'
	