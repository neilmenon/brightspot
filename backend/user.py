from flask_login import UserMixin
from api import sql_helper
import mariadb
import api.config as config
cfg = config.config

class User(UserMixin):
    def __init__(self, id_, name, email, profile_image):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_image = profile_image

    @staticmethod
    def get(user_id):
        mdb = mariadb.connect(**(cfg['sql']))
        cursor = mdb.cursor(dictionary=True)
        cursor.execute("SELECT * from users WHERE google_id = {}".format(user_id))
        result = list(cursor)
        mdb.close()
        if not result:
            return None

        return User(id_=result[0]['id'], name=result[0]['name'], email=result[0]['email'], profile_image=result[0]['profile_image'])

    @staticmethod
    def get_dict(user_id):
        mdb = mariadb.connect(**(cfg['sql']))
        cursor = mdb.cursor(dictionary=True)
        cursor.execute("SELECT * from users WHERE id = {}".format(user_id))
        result = list(cursor)
        mdb.close()
        if not result:
            return None

        result[0].pop('google_id')

        return result[0]

    @staticmethod
    def create(id_, name, email, profile_image):
        mdb = mariadb.connect(**(cfg['sql']))
        cursor = mdb.cursor(dictionary=True)
        data = { "google_id": id_, "name": name, "email": email, "profile_image": profile_image }
        print(sql_helper.insert_into("users", data))
        cursor.execute(sql_helper.insert_into("users", data))
        mdb.commit()
        mdb.close()



