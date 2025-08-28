from flask import Flask, g, request, jsonify
# , jsonify, redirect, render_template, session, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from os import environ as env
import models
from flask_talisman import Talisman
from security.auth0_service import auth0_service
from resources import destination_routes
from resources import exception_routes
from resources import facility_routes
from resources import inventory_routes
from resources import lookup_routes
from resources import test_routes
from resources import user_routes
import json
from datetime import date
from getenv_path import env_path

# control JSON conversion of date objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return json.JSONEncoder.default(self, obj)

# load environment variables
load_dotenv(dotenv_path=env_path)
# if env_path.exists:
#     print(env_path)

AUTH0_AUDIENCE      = env.get('AUTH0_AUDIENCE')
AUTH0_DOMAIN        = env.get('AUTH0_DOMAIN')
CLIENT_ORIGIN_URL   = env.get('CLIENT_ORIGIN_URL')
ORIGINS             = json.loads(env.get('ORIGINS'))
PORT                = env.get('PORT', 5000)
FLASK_ENV           = env.get('FLASK_ENV')

if FLASK_ENV == 'development':
    DEBUG = True
else:
    DEBUG = False

if not (CLIENT_ORIGIN_URL and AUTH0_AUDIENCE and AUTH0_DOMAIN):
    raise NameError("The required environment variables are missing. Check .env file.")

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

# HTTP Security Headers
csp = {
    'default-src': ['\'self\''],
    'frame-ancestors': ['\'none\'']
}

Talisman(app,
            frame_options='DENY',
            content_security_policy=csp,
            referrer_policy='no-referrer'
            )

auth0_service.initialize(AUTH0_DOMAIN, AUTH0_AUDIENCE)

# open the database connection before each request
@app.before_request
def before_request():
    g.NAMESPACE = AUTH0_AUDIENCE
    print('connecting to database')
    g.db = models.DATABASE
    g.db.connect

# set response headers and close the database connection
@app.after_request
def after_request(response):
    response.headers['X-XSS-Protection'] = '0'
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    g.db.close()
    print('After Request - Setting response headers - close database')
    return response

# api wide CORS policy
CORS(
    app,
    resources={"/api/*": {"origins":ORIGINS}},
    allow_headers=["Authorization", "Content-Type"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True,
    max_age=86400
    )

# put routes or blueprints here

app.register_blueprint(destination_routes.bp)
app.register_blueprint(exception_routes.bp)
app.register_blueprint(facility_routes.bp)
app.register_blueprint(inventory_routes.bp)
app.register_blueprint(lookup_routes.bp)
app.register_blueprint(test_routes.bp)
app.register_blueprint(user_routes.bp)

@app.route('/')
def hello():
    # function that gets called when the route is hit
    if env_path.exists:
        print(env_path)
    print('hit home route!')
    return jsonify(data={'result': 'Successfully Hit Default Route!'}, status={'code': 200, 'message': 'SUCCESS!'}), 200

if __name__ == "__main__":
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
