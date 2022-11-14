from flask import Blueprint, jsonify
from security.guards import authorization_guard, permissions_guard, permissions

bp_name = 'api-test-routes'
bp_url_prefix = '/api/test_routes'
bp = Blueprint(bp_name, __name__, url_prefix=bp_url_prefix)

@bp.route("/public", methods=['GET'])
def public():
    print('hitting /public')
    return jsonify(data="successfully hit test route public", message="success", status=200), 200

@bp.route("/protected", methods=['GET'])
@authorization_guard
def protected():
    print('hitting /protected')
    return jsonify(data="successfully hit auth required route", message="success", status=200), 200

@bp.route("/admin")
@authorization_guard
@permissions_guard([permissions.admin_mess_read])
def admin():
    print('hitting /admin')
    return jsonify(data="successfully it admin route", message="success", status=200), 200
