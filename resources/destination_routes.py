from flask import Blueprint, jsonify, g, request
from security.guards import authorization_guard, permissions_guard, permissions
import models
from playhouse.shortcuts import model_to_dict

bp_name = 'api-destination-routes'
bp_url_prefix = '/api/v1/destination'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

@bp.route('/', methods=['GET'])
@authorization_guard
def destination_index():
    '''return all facilities in database and the associated contact person'''
    result = (models.Destination.select()
            .order_by(models.Destination.state, models.Destination.city, models.Destination.name)
            )
    result_list = [model_to_dict(destination) for destination in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} destinations'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
def destination_create():    
    payload = request.get_json()    
    new_destination = models.Destination.create(**payload)
    destination_dict = model_to_dict(new_destination)
    return jsonify(data=destination_dict, status={'code': 201, 'message': 'successfully created destination'}), 201

@bp.route('/<id>', methods=['GET'])
@authorization_guard
def destination_show(id):
    destination = models.Destination.get_by_id(id)
    if destination:
        return jsonify(data=model_to_dict(destination), status={'code': 200, 'message': 'success'}),200
    else:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: destination at id:{id} was not found'}), 404

@bp.route('/<id>', methods=['PUT']) # do not allow delete, as this would cause data inconsistancy with items table
@authorization_guard
def destination_update(id):
    try:
        destination = models.Destination.get_by_id(id) # find the destination if it exists
    except: # failed to find the destination
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: destination at id:{id} was not found'}), 404
    else:   # found the destination so now process the PUT
        payload = request.get_json() # payload will be the data or false
        query = models.Destination.update(**payload).where(models.Destination.id == id)
        query.execute()
        data = model_to_dict(models.Destination.get_by_id(id))
        message = 'successfully updated destination'
        return jsonify(data=data, status={'code': 200, 'message': message}),200


