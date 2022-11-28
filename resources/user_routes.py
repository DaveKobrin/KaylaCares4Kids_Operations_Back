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
    # access_token = g.get('access_token')
    # namespace = g.get('NAMESPACE')
    # print('hitting /login')
    # print(access_token)
    # print(namespace, '    namespace')
    try:
    #     # user found in db log in and return user data
    #     user = models.User.get(models.User.email == access_token[namespace+'/email'])
    #     user_dict = model_to_dict(user)
    #     g.curr_user = user_dict
        user = verify_user_logged_in()
        # print(user)
        return jsonify(data=user, status={'code': 200, 'message': 'logged in'}), 200
    except:
        return jsonify(data={}, status={'code': 400, 'message': 'Error logging in'}), 400
    # except models.DoesNotExist:
    #     # user not found in db register new user 
    #     payload = {}    
    #     payload['email'] = access_token[namespace+'/email']
    #     payload['name'] = access_token[namespace+'/name'] if (namespace+'/name') in access_token.keys() else 'none given'
    #     payload['phone'] = access_token[namespace+'/phone'] if (namespace+'/phone') in access_token.keys() else 'none given'
    #     print(payload, '   payload')
    #     user = models.User.create(**payload)
    #     user_dict = model_to_dict(user)
    #     g.curr_user = user_dict
    #     return jsonify(data=user_dict, status={'code': 201, 'message': 'registered'}), 201

@bp.route("/logout", methods=['GET'])
def logout():
    if g.get('curr_user'):
        g.curr_user = {}
    return jsonify(data=g.get('curr_user'), status={'code': 200, 'message': 'logged out'}), 200

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

