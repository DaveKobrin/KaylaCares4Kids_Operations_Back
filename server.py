from flask import Flask, g
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
from json import JSONEncoder
from datetime import date
from getenv_path import env_path

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

# load environment variables
load_dotenv(dotenv_path=env_path)
if env_path.exists:
    print(env_path)

AUTH0_AUDIENCE      = env.get('AUTH0_AUDIENCE')
AUTH0_DOMAIN        = env.get('AUTH0_DOMAIN')
CLIENT_ORIGIN_URL   = env.get('CLIENT_ORIGIN_URL')
ORIGINS             = env.get('ORIGINS')
PORT                = env.get('PORT', 5000)
FLASK_ENV           = env.get('FLASK_ENV')
if FLASK_ENV == 'development':
    DEBUG = True
else:
    DEBUG = False

if not (CLIENT_ORIGIN_URL and AUTH0_AUDIENCE and AUTH0_DOMAIN):
    raise NameError("The required environment variables are missing. Check .env file.")

# CLIENT_SECRET   = env.get('AUTH0_CLIENT_SECRET')
# CLIENT_ID       = env.get('AUTH0_CLIENT_ID')
# SECRET_KEY      = env.get('APP_SECRET_KEY')

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
    g.db.close()
    return response

# api wide CORS policy
CORS(
    app,
    resources={"/api/*": {"origins":["http://localhost:3000", "https://kaylacares4kidsops.netlify.app"]}},
    allow_headers=["Authorization", "Content-Type"],
    methods=["GET", "POST", "PUT", "DELETE"],
    supports_credentials=True,
    max_age=86400
    )


# CORS(exception_routes.bp, 
#     origins=["http://localhost:3000", "https://kayla-cares-4-kids-operations.herokuapp.com"],
#     allow_headers=["Authorization", "Content-Type"],
#     methods=["GET", "POST", "PUT", "DELETE"],
#     supports_credentials=True,
#     max_age=86400
#     )
# CORS(test_routes.bp, 
#     origins=["http://localhost:3000", "https://kayla-cares-4-kids-operations.herokuapp.com"],
#     allow_headers=["Authorization", "Content-Type"],
#     methods=["GET", "POST", "PUT", "DELETE"],
#     supports_credentials=True,
#     max_age=86400
#     )
# CORS(user_routes.bp, 
#     origins=["http://localhost:3000", "https://kayla-cares-4-kids-operations.herokuapp.com"],
#     allow_headers=["Authorization", "Content-Type"],
#     methods=["GET", "POST", "PUT", "DELETE"],
#     supports_credentials=True,
#     max_age=86400
#     )
# CORS(inventory_routes.bp, 
#     origins=["http://localhost:3000", "https://kayla-cares-4-kids-operations.herokuapp.com"],
#     allow_headers=["Authorization", "Content-Type"],
#     methods=["GET", "POST", "PUT", "DELETE"],
#     supports_credentials=True,
#     max_age=86400
#     )

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
    return 'Hello, World!'

if __name__ == "__main__":
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
