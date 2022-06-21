from flask import Blueprint, request
from google.cloud import datastore
import json
from json2html import *
import constants

client = datastore.Client()

bp = Blueprint('slip', __name__, url_prefix='/slips')

# /slip
@bp.route('', methods=['POST','GET'])
def slips_get_post():
    # POST slip
    if request.method == 'POST':
        content = request.get_json()

        if "number" in content:
            new_slips = datastore.entity.Entity(key=client.key(constants.slips))

            new_slips.update({"number": content["number"], "current_boat": None})
            client.put(new_slips)

            slip_key = client.key(constants.slips, new_slips.key.id)
            
            slip = client.get(key=slip_key)
            
            slip["id"] = new_slips.key.id
            return (json.dumps(slip), 201)
        
        else:
            x = {
                "Error": "The request object is missing the required number"
            }
            a_ll = json.dumps(x)
            return (a_ll, 400)
    # GET all slips
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        
        results = list(query.fetch())

        for e in results:
            e["id"] = e.key.id
        return (json.dumps(results),200)
    else:
        return ('The request object is missing the required number', 400)

# /slips/<slip_id>
@bp.route('/<slip_id>', methods=['PUT','DELETE'])
def slips_get_delete(slip_id):
    print(request)
    print("IN slips_get_delete")

    # DELETE the slip at slip_id
    if request.method == 'DELETE':
        
        print("IN delete")
        slip_key = client.key(constants.slips, int(slip_id))
        if slip_key != None:
            slip = client.get(key = slip_key)
            if slip != None:
                client.delete(slip_key)
                return ('', 204)
            # slip is None
            else:
                x = {
                    "Error": "No slip with this slip_id exists"
                }
                a_ll = json.dumps(x)
                return (a_ll,404)
        # slip_key is None
        else:
            x = {
                "Error": "No slip with this slip_id exists"
            }
            a_ll = json.dumps(x)
            return (a_ll,404)

    # GET slip_id json information
    elif request.method == 'GET':
        print("IN get")
        #content = request.get_json()
        
        print("IN get")
        slip_key = client.key(constants.slips, int(slip_id))
        
        if slip_key != None:
            print("IN get")
            slip = client.get(key=slip_key)
            print("IN get1")
            print(slip)
            if slip != None:
                slip["id"] = slip.key.id
                
                return (json.dumps(slip), 200)
            # slip is None
            else:
                x = {
                    "Error": "No slip with this slip_id exists"
                }
                a_ll = json.dumps(x)
                return (a_ll, 404)
        # slip_key is None
        else:
            x = {
                "Error": "No slip with this slip_id exists"
            }
            a_ll = json.dumps(x)
            return (a_ll, 404)

    else:
        print("Not in get or delete")
        return ('No slip with this slip_id exists', 404)

@bp.route('/<slip_id>/<boat_id>', methods=['PUT','DELETE'])
def slips_boat_put_delete(slip_id, boat_id):
    # PUT boat into a slip, if it is occupied slip["current_boat"] != None
    if request.method == 'PUT':
        slip_key = client.key(constants.slips, int(slip_id))
        if slip_key != None:
            slip = client.get(key=slip_key)
            if slip != None:
                current_boats = slip["current_boat"]
                boat_key = client.key(constants.boats, int(boat_id))
                boat = client.get(key=boat_key)
                if boat != None:
                    query = client.query(kind=constants.slips)
                    results = list(query.fetch())
                    for e in results:
                        try:
                            current_boats = e["current_boat"]
                        except:
                            continue
                # boat is None
                else:
                    x = {
                        "Error": "The specified boat and/or slip does not exist"
                    }
                    a_ll = json.dumps(x)
                    return (a_ll, 404)
                if slip["current_boat"] != None:
                    x = {
                        "Error": "The slip is not empty"
                    }
                    a_ll = json.dumps(x)
                    return (a_ll, 403)
            # slip is None
            else:
                x = {
                    "Error": "The specified boat and/or slip does not exist"
                }
                a_ll = json.dumps(x)
                return (a_ll, 404)
        # slip_key is None
        else:
            x = {
                "Error": "The specified boat and/or slip does not exist"
            }
            a_ll = json.dumps(x)
            return (a_ll, 404)
        
        slip.update({"number": slip["number"], "current_boat": int(boat_id)})
        client.put(slip)
        return ('',204)
    
    # DELETE boat from slip, the boat is no longer at slip
    elif request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(slip_id))
        if slip_key != None:
            slip = client.get(slip_key)
            if slip != None:
                try:
                    current_boat = slip["current_boat"]
                    if current_boat != None:
                        if int(current_boat) == int(boat_id):
                            slip.update({"number": slip["number"], "current_boat": None})
                            client.put(slip)
                            return('', 204)
                        
                        else:
                            x = {
                                "Error": "No boat with this boat_id is at the slip with this slip_id"
                            }
                            a_ll = json.dumps(x)
                            return (a_ll, 404)
                    #current_boat is None
                    else:
                        x = {
                                "Error": "No boat with this boat_id is at the slip with this slip_id"
                        }
                        a_ll = json.dumps(x)
                        return (a_ll, 404)
                except:
                    x = {
                        "Error": "No boat with this boat_id is at the slip with this slip_id"
                    }
                    a_ll = json.dumps(x)
                    return (a_ll, 404)
            #slip is none
            else:
                x = {
                    "Error": "No boat with this boat_id is at the slip with this slip_id"
                }
                a_ll = json.dumps(x)
                return (a_ll, 404)
        #slip_key is none
        else:
            x = {
                    "Error": "No boat with this boat_id is at the slip with this slip_id"
            }
            a_ll = json.dumps(x)
            return (a_ll, 404)
  
    else:
        return ('No slip with this slip_id exists', 404)