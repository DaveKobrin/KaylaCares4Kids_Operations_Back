from flask import Blueprint, jsonify, g, request
from security.guards import authorization_guard, permissions_guard, permissions
import models
from playhouse.shortcuts import model_to_dict

bp_name = 'api-inventory-routes'
bp_url_prefix = '/api/v1/inventory'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

select_fields = [
        models.Item.facility_id,
        models.Facility.name,
        models.Facility.id,
        models.Item.category,
        models.Item.condition,
        models.Item.fair_market_value,
        models.Item.kids_served,
        models.Item.title_desc,
        models.Item.format,
        models.Item.artist,
        models.Item.genre,
        models.Item.age_range,
        models.Item.rating,
        models.Item.location,
        models.Item.upc_code,
        models.Item.date_received,
        models.Item.date_shipped,
        models.Item.destination_id,
        models.Destination.name,
        models.User.name,
        models.User.id,
    ]

@bp.route('/', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def item_index():
    '''return all items in inventory with the name of the Facility where they are located'''
    result = (models.Item.select(select_fields)
            .join(models.Facility)
            .join(models.User)
            .join(models.Destination)
            .order_by(models.Item.title_desc, models.Item.condition, models.Item.date_received)
            )
    result_list = [model_to_dict(item) for item in result]
    print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} items'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
@permissions_guard([permissions.inventory_write])
def item_create():    
    payload = request.get_json()
    if len(payload) == 1:   # create one item
        payload['received_by'] = g.get('curr_user')['id']
        new_item = models.Item.create(**payload)
        item_dict = model_to_dict(new_item)
        return jsonify(data=item_dict, status={'code': 201, 'message': 'successfully created item'}), 201
    elif len(payload) > 1:  # create multiple items at once, allow front end to send a batch (more efficient for item entered in quantity)
        for item in payload:
            item['received_by'] = g.get('curr_user')['id']
        with models.DATABASE.atomic():
            num_inserted = models.Item.insert_many(payload).execute()
        return jsonify(data={'number_inserted': num_inserted}, status={'code': 201, 'message': f'successfully created {len(payload)} items'}), 201
    else:   # should never hit this, but in case there is a bad request
        return jsonify(data={}, status={'code': 400, 'message': 'no items in request'}), 400

@bp.route('/<id>', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def item_show(id):
    
    item = models.Item.select(select_fields).join(models.Facility).join(models.User).where(models.Item.id == id)
    if item:
        return jsonify(data=model_to_dict(item), status={'code': 200, 'message': 'success'}),200
    else:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: items at id:{id} was not found'}), 404

@bp.route('/<id>', methods=['PUT', 'DELETE'])
@authorization_guard
@permissions_guard([permissions.inventory_write])
def item_update_del(id):
    try:
        item = models.Item.get_by_id(id) # find the item if it exists
    except: # failed to find the item
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: items at id:{id} was not found'}), 404
    else:   # found the item so now process the PUT or DELETE
        payload = request.method == 'PUT' and request.get_json() # payload will be the data or false
        query = models.Item.update(**payload).where(models.Item.id == id) if payload else models.Item.delete().where(models.Item.id == id)
        query.execute()
        if payload:
            data = model_to_dict(models.Item.get_by_id(id))
            message = 'successfully updated item'
        else:
            data = {}
            message = 'successfully deleted item'

        return jsonify(data=data, status={'code': 200, 'message': message}),200


