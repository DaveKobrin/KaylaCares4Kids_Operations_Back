from flask import Blueprint, jsonify, g, request, json
from security.guards import authorization_guard, permissions_guard, permissions, verify_user_logged_in
import models
from playhouse.shortcuts import model_to_dict
from peewee import *
import requests

bp_name = 'api-inventory-routes'
bp_url_prefix = '/api/v1/inventory'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

select_fields = [
        models.Item.facility_id,
        # models.Facility.name,
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
        # models.Destination.name,
        models.Item.received_by,
        # models.User.name,
    ]

@bp.route('/', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def item_index():
    '''return all items in inventory with the name of the Facility where they are located'''
    # print ('here trying to get all items')
    # try:
    result = (models.Item.select()
            # .join(models.Facility, on=(models.Item.facility_id == models.Facility.id))
            # .switch(models.Item)
            # .join(models.User, on=(models.Item.received_by == models.User.id))
            # .switch(models.Item)
            # .join(models.Destination, on=(models.Item.destination_id == models.Destination.id))
            .order_by(models.Item.title_desc, models.Item.condition, models.Item.date_received)
            )
    # print(result)
    result_list = [model_to_dict(item) for item in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} items'}), 200
    # except:
    #     print('select failed')
    #     return jsonify(data={}, status={'code': 200, 'message': f'found no items'}), 200

@bp.route('/', methods=['POST'])
@authorization_guard
@permissions_guard([permissions.inventory_write])
def item_create():    
    payload = request.get_json()
    user = verify_user_logged_in()
    # print('payload: ', payload)
    # print('curr_user: ', user)
    if len(payload) == 1:   # create one item
        payload[0]['received_by'] = user['id']
        new_item = models.Item.create(**payload[0])
        item_dict = model_to_dict(new_item)
        return jsonify(data=item_dict, status={'code': 201, 'message': 'successfully created item'}), 201
    elif len(payload) > 1:  # create multiple items at once, allow front end to send a batch (more efficient for item entered in quantity)
        for item in payload:
            item['received_by'] = user['id']
        with models.DATABASE.atomic():
            num_inserted = models.Item.insert_many(payload).execute()
        return jsonify(data={'number_inserted': num_inserted}, status={'code': 201, 'message': f'successfully created {len(payload)} items'}), 201
    else:   # should never hit this, but in case there is a bad request
        return jsonify(data={}, status={'code': 400, 'message': 'no items in request'}), 400

@bp.route('/<id>', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_read])
def item_show(id):
    # print(id)
    try:
        item = models.Item.get_by_id(id)
        # print(jsonify(model_to_dict(item)).get_data(as_text=True))
    except:
        return jsonify(data={}, status={'code': 404, 'message': f'FAILED: items at id:{id} was not found'}), 404
    else:
        return jsonify(data=model_to_dict(item), status={'code': 200, 'message': 'success'}),200

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
        # print('payload: ', payload)
        query = models.Item.update(**payload).where(models.Item.id == id) if payload else models.Item.delete().where(models.Item.id == id)
        # print('query: ', query)
        query.execute()
        if payload:
            data = model_to_dict(models.Item.get_by_id(id))
            message = 'successfully updated item'
        else:
            data = {}
            message = 'successfully deleted item'

        return jsonify(data=data, status={'code': 200, 'message': message}),200

@bp.route('upc/<upc>', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.inventory_write])
def item_upc_lookup(upc):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
        }
        resp = requests.get(f'https://api.upcitemdb.com/prod/trial/lookup?upc={upc}', headers=headers)
        # print('resp: ',resp)
        data = json.loads(resp.text)
        # print('data: ', data)
        return jsonify(data=data, status={'code': 200, 'message': 'success'}),200
    except:
        return jsonify(data={}, status={'code': 500, 'message': 'error in request'}), 500