from flask import Blueprint, jsonify, g
from security.guards import authorization_guard, permissions_guard, permissions, verify_user_logged_in
import models
from playhouse.shortcuts import model_to_dict
from resources import seed_data

bp_name = 'api-user-routes'
bp_url_prefix = '/api/v1/users'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

@bp.route("/login", methods=['GET'])
@authorization_guard
def login():
    try:
    #     # user found in db log in and return user data
        user = verify_user_logged_in()
        print('user in /login', user)
        return jsonify(data=user, status={'code': 200, 'message': 'logged in'}), 200
    except Exception as e:
        print(f'An unexpected error logging in has occurred: {e}')
        return jsonify(data={}, status={'code': 400, 'message': 'Error logging in'}), 400

@bp.route("/logout", methods=['GET'])
def logout():
    if g.get('curr_user'):
        g.curr_user = {}
    return jsonify(data=g.get('curr_user'), status={'code': 200, 'message': 'logged out'}), 200

@bp.route('/', methods=['GET'])
@authorization_guard
@permissions_guard([permissions.user_read])
def user_index():
    '''return all users in database'''
    # print ('here trying to get all items')
    # try:
    result = models.User.select()
    # print(result)
    result_list = [model_to_dict(item) for item in result]
    # print(result_list)
    return jsonify(data=result_list, status={'code': 200, 'message': f'successfully found {len(result_list)} users'}), 200


@bp.route("/seed")
# @authorization_guard
# @permissions_guard([permissions.admin_mess_read])
def seed():
    # print('hitting seed')
    seeded_data = False
    
    with models.DATABASE.atomic():
        if not models.Role.select():
            models.Role.insert_many(seed_data.role_data).execute()
            seeded_data = True
        if not models.Permission.select():
            models.Permission.insert_many(seed_data.permission_data).execute()
            seeded_data = True
        if not models.LookUpSheet.select():
            models.LookUpSheet.insert_many(seed_data.lookup_data).execute()
            seeded_data = True
        if not models.Facility.select():
            models.Facility.insert_many(seed_data.facility_data).execute()
            seeded_data = True
        if not models.Destination.select():
            models.Destination.insert_many(seed_data.destination_data).execute()
            seeded_data = True

    if seeded_data:
        return jsonify(data="successfully seeded data", message="success", status=200), 200
    else:
        return jsonify(data="data already exists", message="no change", status=202), 202

