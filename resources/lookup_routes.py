from flask import Blueprint, jsonify, g, request
from security.guards import authorization_guard, permissions_guard, permissions
import models
from playhouse.shortcuts import model_to_dict

bp_name = 'api-lookup-routes'
bp_url_prefix = '/api/v1/lookup'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

@bp.route('/', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def lookup_item_index():
    '''return all items in inventory with the name of the Facility where they are located'''
    # print('in lookup sheet get index')
    result = (models.LookUpSheet.select()
            .order_by(models.LookUpSheet.description)
            )
    result_list = [model_to_dict(item) for item in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} items'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
@permissions_guard([permissions.org_data_write])
def lookup_item_create():    
    payload = request.get_json()
    new_lookup_item = models.LookUpSheet.create(**payload)
    lookup_item_dict = model_to_dict(new_lookup_item)
    return jsonify(data=lookup_item_dict, status={'code': 201, 'message': 'successfully created item'}), 201

@bp.route('/<id>', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.org_data_read])
def lookup_item_show(id):    
    lookup_item = models.LookUpSheet.get_by_id(id) #select().where(models.LookUpSheet.id == id)
    print(lookup_item)

    if lookup_item:
        lookup_dict = model_to_dict(lookup_item)
        print(lookup_dict)
        return jsonify(data=lookup_dict, status={'code': 200, 'message': 'success'}),200
    else:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: items at id:{id} was not found'}), 404

@bp.route('/<id>', methods=['PUT', 'DELETE'])
@authorization_guard
@permissions_guard([permissions.org_data_write])
def lookup_item_update_del(id):
    try:
        lookup_item = models.LookUpSheet.get_by_id(id) # find the item if it exists
    except: # failed to find the item
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: items at id:{id} was not found'}), 404
    else:   # found the item so now process the PUT or DELETE
        payload = request.method == 'PUT' and request.get_json() # payload will be the data or false
        query = models.LookUpSheet.update(**payload).where(models.LookUpSheet.id == id) if payload else models.LookUpSheet.delete().where(models.LookUpSheet.id == id)
        query.execute()
        if payload:
            data = model_to_dict(models.LookUpSheet.get_by_id(id))
            message = 'successfully updated item'
        else:
            data = {}
            message = 'successfully deleted item'

        return jsonify(data=data, status={'code': 200, 'message': message}),200


