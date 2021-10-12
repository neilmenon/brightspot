from flask_login import UserMixin
from api import sql_helper
from api import api_logger as logger
import mariadb
import api.config as config
cfg = config.config

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
      logger.log("A database error occured: {}".format(e))

   mdb.close()
   return records

class User(UserMixin):
    def __init__(self, id_, name, email, profile_image):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_image = profile_image

    @staticmethod
    def get(user_id):
        result = execute_db("SELECT * from users WHERE google_id = {}".format(user_id))
        if not result:
            return None

        return User(id_=result[0]['id'], name=result[0]['name'], email=result[0]['email'], profile_image=result[0]['profile_image'])

    @staticmethod
    def get_dict(user_id):
        result = execute_db("SELECT * from users WHERE id = {}".format(user_id))
        if not result:
            return None

        result[0].pop('google_id')

        return result[0]

    @staticmethod
    def create(id_, name, email, profile_image):
        data = { "google_id": id_, "name": name, "email": email, "profile_image": profile_image }
        execute_db(sql_helper.insert_into("users", data), commit=True)


