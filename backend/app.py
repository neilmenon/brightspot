from flask import Flask, redirect, request, url_for, jsonify
from flask_cors import CORS
import json
import time
import os
from user import User
import mariadb

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

import api.config as config
cfg = config.config

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.urandom(36)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(cfg['GOOGLE_CLIENT_ID'])

@login_manager.user_loader
def load_user(user_id):
   return User.get(user_id)

@app.route('/api', methods=['GET'])
def index():
   # return flask.jsonify(current_user)
   if current_user.is_authenticated:
      return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/api/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_image
         )
      )
   else:
      return '<a class="button" href="/api/login">Google Login</a>'

'''
   GOOGLE LOGIN ENDPOINTS
      Thanks to: https://realpython.com/flask-google-login
'''

@app.route("/api/login")
def login():
   # Find out what URL to hit for Google login
   google_cfg = requests.get(cfg['GOOGLE_DISCOVERY_URL']).json()
   authorization_endpoint = google_cfg["authorization_endpoint"]

   # Use library to construct the request for Google login and provide
   # scopes that let you retrieve user's profile from Google
   request_uri = client.prepare_request_uri(
      authorization_endpoint,
      redirect_uri=request.base_url + "/callback",
      scope=["openid", "email", "profile"],
   )
   return redirect(request_uri)

@app.route("/api/login/callback")
def callback():
   # Get authorization code Google sent back with login
   code = request.args.get("code")

   google_cfg = requests.get(cfg['GOOGLE_DISCOVERY_URL']).json()
   token_endpoint = google_cfg["token_endpoint"]

   # Prepare and send a request to get tokens
   token_url, headers, body = client.prepare_token_request(
      token_endpoint,
      authorization_response=request.url,
      redirect_url=request.base_url,
      code=code
   )
   token_response = requests.post(
      token_url,
      headers=headers,
      data=body,
      auth=(cfg['GOOGLE_CLIENT_ID'], cfg['GOOGLE_CLIENT_SECRET']),
   )

   # Parse the tokens
   client.parse_request_body_response(json.dumps(token_response.json()))

   # Now that you have tokens (yay) let's find and hit the URL
   # from Google that gives you the user's profile information,
   # including their Google profile image and email
   userinfo_endpoint = google_cfg["userinfo_endpoint"]
   uri, headers, body = client.add_token(userinfo_endpoint)
   userinfo_response = requests.get(uri, headers=headers, data=body)

   # You want to make sure their email is verified.
   # The user authenticated with Google, authorized your
   # app, and now you've verified their email through Google!
   if userinfo_response.json().get("email_verified"):
      unique_id = userinfo_response.json()["sub"]
      users_email = userinfo_response.json()["email"]
      picture = userinfo_response.json()["picture"]
      users_name = userinfo_response.json()["name"]
   else:
      return "User email not available or not verified by Google.", 400

   # Create a user in your db with the information provided
   # by Google
   user = User(id_=unique_id, name=users_name, email=users_email, profile_image=picture)

   # Doesn't exist? Add it to the database.
   if not User.get(unique_id):
      User.create(unique_id, users_name, users_email, picture)

   # Begin user session by logging the user in
   login_user(user)

   # Send user back to homepage
   return redirect(url_for("index"))

@app.route("/api/logout")
@login_required
def logout():
   logout_user()
   return redirect(url_for("index"))

'''
   COMMENT ENDPOINTS
'''

@app.route("/api/comments", methods=['GET'])
def comments():
   mdb = mariadb.connect(**(cfg['sql']))
   cursor = mdb.cursor(dictionary=True)

   # get all comments
   cursor.execute("SELECT * FROM comments;")
   result = list(cursor)

   

   mdb.close()
   return jsonify(result)

if __name__ == "__main__":
   # localhost or server?
   if cfg['server']:
      app.run(host='0.0.0.0')
   else:
   #  app.run(ssl_context="adhoc")
      app.run()