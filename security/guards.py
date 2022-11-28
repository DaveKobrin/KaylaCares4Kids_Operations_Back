from functools import wraps
from http import HTTPStatus
from types import SimpleNamespace
import models
from playhouse.shortcuts import model_to_dict
from flask import request, g

from security.auth0_service import auth0_service
from security.utils import json_abort

unauthorized_error = {
    "message": "Requires authentication"
}

invalid_request_error = {
    "error": "invalid_request",
    "error_description": "Authorization header value must follow this format: Bearer access-token",
    "message": "Requires authentication"
}

permissions = SimpleNamespace(
    admin_mess_read = "read:admin-messages",
    user_read = "read:users",
    user_update = "update:user",
    inventory_read = "read:inventory",
    inventory_write = "write:inventory",
    org_data_read = "read:org-data",
    org_data_write = "write:org-data"
)


def get_bearer_token_from_request():
    authorization_header = request.headers.get("Authorization", None)

    if not authorization_header:
        json_abort(HTTPStatus.UNAUTHORIZED, unauthorized_error)
        return

    authorization_header_elements = authorization_header.split()

    if len(authorization_header_elements) != 2:
        json_abort(HTTPStatus.BAD_REQUEST, invalid_request_error)
        return

    auth_scheme = authorization_header_elements[0]
    bearer_token = authorization_header_elements[1]

    if not (auth_scheme and auth_scheme.lower() == "bearer"):
        json_abort(HTTPStatus.UNAUTHORIZED, unauthorized_error)
        return

    if not bearer_token:
        json_abort(HTTPStatus.UNAUTHORIZED, unauthorized_error)
        return

    return bearer_token

def authorization_guard(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        token = get_bearer_token_from_request()
        validated_token = auth0_service.validate_jwt(token)

        g.access_token = validated_token

        return function(*args, **kwargs)

    return decorator


def permissions_guard(required_permissions=None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            access_token = g.get("access_token")
            if not access_token:
                json_abort(401, unauthorized_error)
                return
            if required_permissions is None:
                return function(*args, **kwargs)
            if not isinstance(required_permissions, list):
                json_abort(500, {
                    "message": "Internal Server Error"
                })
            token_permissions = access_token.get("permissions")
            if not token_permissions:
                json_abort(403, {
                    "message": "Permission denied"
                })
            required_permissions_set = set(required_permissions)
            token_permissions_set = set(token_permissions)
            if not required_permissions_set.issubset(token_permissions_set):
                json_abort(403, {
                    "message": "Permission denied"
                })
            return function(*args, **kwargs)
        return wrapper
    return decorator

def verify_user_logged_in():
    access_token = g.get('access_token')
    namespace = g.get('NAMESPACE')
    # print('hitting /login')
    # print(access_token)
    # print(namespace, '    namespace')
    try:
        # user found in db log in and return user data
        user = models.User.get(models.User.email == access_token[namespace+'/email'])

    except models.DoesNotExist:
        # user not found in db register new user 
        payload = {}    
        payload['email'] = access_token[namespace+'/email']
        payload['name'] = access_token[namespace+'/name'] if (namespace+'/name') in access_token.keys() else 'none given'
        payload['phone'] = access_token[namespace+'/phone'] if (namespace+'/phone') in access_token.keys() else 'none given'
        print(payload, '   payload')
        user = models.User.create(**payload)

    user_dict = model_to_dict(user)
    g.curr_user = user_dict
    return user_dict
