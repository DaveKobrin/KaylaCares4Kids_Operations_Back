from flask import Blueprint, jsonify, g, request
from security.guards import authorization_guard, permissions_guard, permissions
import models
from playhouse.shortcuts import model_to_dict

bp_name = 'api-dest-req-item-routes'
bp_url_prefix = '/api/v1/dest-req-item'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

@bp.route('/req/<id>', methods=['GET'])
@authorization_guard
def dest_req_item_index(id):
    '''return all requests in database'''
    result = (models.DestRequestItem.select()
            .where(models.DestRequestItem.dest_req_id == id)
            .order_by(models.DestRequestItem.title_desc, models.DestRequestItem.condition, models.DestRequestItem.format)
            )
    result_list = [model_to_dict(req) for req in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} items'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
def dest_req_create():    
    payload = request.get_json()    
    new_req = models.DestRequest.create(**payload)
    req_dict = model_to_dict(new_req)
    return jsonify(data=req_dict, status={'code': 201, 'message': 'successfully created end user request'}), 201

@bp.route('/<id>', methods=['GET'])
@authorization_guard
def dest_req_show(id):
    req = models.DestRequest.get_by_id(id)
    if req:
        return jsonify(data=model_to_dict(req), status={'code': 200, 'message': 'success'}),200
    else:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: user request at id:{id} was not found'}), 404

@bp.route('/<id>', methods=['PUT', 'DELETE']) # do not allow delete, as this would cause data inconsistancy with items table
@authorization_guard
def dest_req_update(id):
    try:
        req = models.DestRequest.get_by_id(id) # find the destination if it exists
    except: # failed to find the destination
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: user request at id:{id} was not found'}), 404
    else:   # found the destination so now process the PUT
        payload = request.method == 'PUT' and request.get_json() # payload will be the data or false
        query = models.DestRequest.update(**payload).where(models.DestRequest.id == id) if payload else models.DestRequest.delete().where(models.DestRequest.id == id)
        query.execute()
        if payload:
            data = model_to_dict(models.DestRequest.get_by_id(id))
            message = 'successfully updated user request'
        else:
            data = {}
            message = 'successfully deleted user request'

        return jsonify(data=data, status={'code': 200, 'message': message}),200
