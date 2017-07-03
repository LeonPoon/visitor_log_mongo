from flask import Flask, send_from_directory, jsonify, request
from json import JSONEncoder
from datetime import datetime
import calendar


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, ObjectId):
                return str(obj)
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis - (8 * 3600 * 1000)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.config['ZODB_STORAGE'] = 'file:///home/pyapp1/visitor_wall/zodb.fs'
app.json_encoder = CustomJSONEncoder

#from flask.ext.zodb import ZODB
#db = ZODB(app)

from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient()
db = client.db1
col = db.collection1
posts = col.posts

class Person(object):
	def __init__(self, n, dt):
		self.name= n
		self.datetime = dt
	def todict(self):
		return { 'name': self.name, 'datetime': self.datetime }

@app.route('/', methods=['GET'])
def show_html():
	return send_from_directory('', 'index.html')

@app.route('/people', methods=['GET'])
def show_visitors():
	return jsonify(list(dict(x) for x in posts.find()))

@app.route('/person', methods=['POST'])
def add_visitor():
	name = request.json['name']
	if name:
		name = name.strip()
	if not name:
		return jsonify(None)		
	person = Person(request.json['name'], datetime.now())
	object_id = posts.insert_one(person.todict()).inserted_id
	return jsonify(dict(posts.find_one({'_id': object_id})))

