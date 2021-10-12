from flask import Flask, redirect, request, url_for, jsonify, make_response, abort
from flask.helpers import total_seconds
from flask_cors import CORS
import json
import time
import os
from user import User
import mariadb
import datetime

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

import api.api_logger as logger

import api.sql_helper as sql_helper

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.urandom(36)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(cfg['GOOGLE_CLIENT_ID'])

def execute_db(sql, commit=False):
   mdb = mariadb.connect(**(cfg['sql']))
   cursor = mdb.cursor(dictionary=True)

   try:
      logger.log("Executing SQL: {}".format(sql))
      cursor.execute(sql)
      records = [] if commit else list(cursor)
      if commit:
         mdb.commit()
   except mariadb.Error as e:
      mdb.close()
      abort(make_response(jsonify(error="A database error occured: {}".format(e)), 500))

   mdb.close()
   return records

@login_manager.user_loader
def load_user(user_id):
   return User.get(user_id)

@app.route('/api', methods=['GET'])
def index():
   # return flask.jsonify(current_user)
   if current_user.is_authenticated:
      return jsonify({"data": "Signed in"})
   else:
      return jsonify({"data": "Guest"})

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

   userinfo_endpoint = google_cfg["userinfo_endpoint"]
   uri, headers, body = client.add_token(userinfo_endpoint)
   userinfo_response = requests.get(uri, headers=headers, data=body)

   if userinfo_response.json().get("email_verified"):
      unique_id = userinfo_response.json()["sub"]
      users_email = userinfo_response.json()["email"]
      picture = userinfo_response.json()["picture"]
      users_name = userinfo_response.json()["name"]
   else:
      return "User email not available or not verified by Google.", 400

   user = User(id_=unique_id, name=users_name, email=users_email, profile_image=picture)

   if not User.get(unique_id):
      User.create(unique_id, users_name, users_email, picture)

   login_user(user)

   # Send user back to homepage
   return redirect(cfg['frontend_root'])

@app.route("/api/logout")
@login_required
def logout():
   logout_user()
   return redirect(cfg['frontend_root'])

@app.route("/api/user", methods=['GET'])
def get_user():
   if current_user.is_authenticated:
      data = { "id": current_user.id, "name": current_user.name, "email": current_user.email, "profile_image": current_user.profile_image }
      return jsonify(data)
   return jsonify(None)
   # return jsonify(User.get_dict(1))

'''
   COMMENT ENDPOINTS
'''

def construct_replies(parent, c_replies):
   replies = list(filter(lambda x: x['parent_id'] == parent['id'], c_replies))
   if not len(replies):
      return []
   else:
      for reply in replies:
         reply['replies'] = construct_replies(reply, c_replies)
      return replies


@app.route("/api/comments", methods=['GET'])
def comments():
   # get all comments
   result = execute_db("SELECT comments.*, users.name AS author_name, users.email AS author_email, users.profile_image FROM comments LEFT JOIN users ON comments.author_id = users.id ORDER BY unix_timestamp DESC;")
   total_comments = len(result)
   # get likes and dislikes for the comments
   for comment in result:
      reactions = execute_db("SELECT user_id, type, unix_timestamp FROM likes_dislikes WHERE comment_id = {};".format(comment['id']))
      comment['likes_dislikes'] = reactions

   # format the comments list as a nested object for the frontend
   c_final = []
   c_parent = []
   c_replies = []
   
   # append all the parent comments and pop them
   for comment in result:
      if not comment['parent_id']:
         c_parent.append(comment)
      else:
         c_replies.append(comment)

   # recursively loop through rest of comments and assign parents
   for parent in c_parent:
      parent['replies'] = construct_replies(parent, c_replies)
      c_final.append(parent)

   return jsonify({"total": total_comments, "comments": c_final})

@app.route("/api/comment", methods=['POST', 'PUT'])
def create_comment():
   if not current_user.is_authenticated:
      abort(401)

   params = request.get_json()
   try:
      id = params['id'] # if null, then CREATE, if not null then UPDATE
      author_id = params['author_id']
      body = params['body']
      parent_id = params['parent_id']
   except KeyError as e:
      abort(make_response(jsonify(error="Missing required parameter: " + str(e.args[0]) + "."), 400))
   
   unix_timestamp = str(int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()))
   data = { "id": id, "author_id": author_id, "body": sql_helper.esc_db(body), "unix_timestamp": unix_timestamp, "parent_id": parent_id }
   if not parent_id:
      data.pop("parent_id")
   if not id: # CREATE mode
      data.pop("id")
      sql = sql_helper.insert_into("comments", data)
   else: # UPDATE mode
      sql = "UPDATE comments SET body = '{}' WHERE id = {};".format(body, id)
   
   execute_db(sql, commit=True)

   return jsonify(True)

@app.route("/api/comment/<int:comment_id>/delete", methods=['DELETE'])
def delete_comment(comment_id):
   if not current_user.is_authenticated:
      abort(401)

   # delete the comment itself | foreign keys should cascade all replies
   execute_db("DELETE FROM comments WHERE id = {};".format(comment_id), commit=True)
   return jsonify(True)

@app.route("/api/comment/<int:comment_id>/react", methods=['POST', 'PUT'])
def react(comment_id):
   if not current_user.is_authenticated:
      abort(401)
   
   params = request.get_json()
   try:
      user_id = params['user_id']
      type = params['type']
   except KeyError as e:
      abort(make_response(jsonify(error="Missing required parameter: " + str(e.args[0]) + "."), 400))

   if type != "like" and type != "dislike" and type != "remove":
      abort(make_response(jsonify(error="Invalid reaction type. Must be 'like' or 'dislike'"), 400))

   # remove any existing reactions for this comment and user
   execute_db("DELETE FROM likes_dislikes WHERE user_id = {} AND comment_id = {}".format(user_id, comment_id), commit=True)
   if type == "remove":
      return jsonify(True)

   data = { "user_id": user_id, "comment_id": comment_id, "type": type, "unix_timestamp": str(int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())) }
   execute_db(sql_helper.insert_into("likes_dislikes", data), commit=True)
   return jsonify(data)

if __name__ == "__main__":
   # localhost or server?
   if cfg['server']:
      app.run(host='0.0.0.0')
   else:
      # app.run(ssl_context="adhoc")
      app.run()