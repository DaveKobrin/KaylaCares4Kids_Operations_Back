from flask import Blueprint, jsonify, g, request
from security.guards import authorization_guard, permissions_guard, permissions
import models
from playhouse.shortcuts import model_to_dict

bp_name = 'api-facility-routes'
bp_url_prefix = '/api/v1/facility'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

# select_fields = [
#         models.Facility.name,
#         models.Facility.address1,
#         models.Facility.address2,
#         models.Facility.city,
#         models.Facility.state,
#         models.Facility.country,
#         models.Facility.zipcode,
#         models.Facility.contact_id,
#         models.User.name,
#     ]

@bp.route('/', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def facility_index():
    '''return all facilities in database and the associated contact person'''
    result = (models.Facility.select()
            .order_by(models.Facility.state, models.Facility.city, models.Facility.name)
            )
    result_list = [model_to_dict(facility) for facility in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} facilities'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
@permissions_guard([permissions.org_data_write])
def facility_create():    
    payload = request.get_json()    
    new_facility = models.Facility.create(**payload)
    facility_dict = model_to_dict(new_facility)
    return jsonify(data=facility_dict, status={'code': 201, 'message': 'successfully created facility'}), 201

@bp.route('/<id>', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def facility_show(id):
    
    facility = models.Facility.select().where(models.Facility.id == id)
   
    if facility:
        return jsonify(data=model_to_dict(facility), status={'code': 200, 'message': 'success'}),200
    else:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: facility at id:{id} was not found'}), 404

@bp.route('/<id>', methods=['PUT']) # do not allow delete, as this would cause data inconsistancy with items table
@authorization_guard
@permissions_guard([permissions.org_data_write])
def facility_update(id):
    try:
        facility = models.Item.get_by_id(id) # find the facility if it exists
    except: # failed to find the facility
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: facility at id:{id} was not found'}), 404
    else:   # found the facility so now process the PUT
        payload = request.get_json() # payload will be the data or false
        query = models.Facility.update(**payload).where(models.Facility.id == id)
        query.execute()
        data = model_to_dict(models.Facility.get_by_id(id))
        message = 'successfully updated facility'
        return jsonify(data=data, status={'code': 200, 'message': message}),200


