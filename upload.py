from flask import Flask, render_template, request, Response, flash, redirect, session, make_response
from functools import wraps
import json
import uuid
from re import sub
import datetime
from werkzeug.routing import BaseConverter
import config

app = Flask(__name__)

app.config.from_object(config)

mysql = MySQL(app)

app.url_map.converters['int_list'] = IntListConverter

class DateEncoder(json.JSONEncoder):
    def default(self, obj):                     # pylint: disable=E0202
        '''
        to convert datetime format to json acceptable format
        '''
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)

def insert_companies(companies_json):
    '''
    insert each record in companies.json file to database table
    '''
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM companies;")
    for company in companies_json:
        cur.execute("INSERT INTO companies(guid, `index`, company) VALUES (%s, %s, %s);", 
        (str(uuid.uuid4()), int(company["index"]), str(company["company"])))
    mysql.connection.commit()
    cur.close()
    return make_response(json.dumps({'result': 'Upload companies file successful'}), 200)

def insert_people(people_json):
    '''
    insert each record in people.json file to database table
    '''
    fruits = []
    vegetables = []
    with open('config/fruits.txt') as fr:
        fruits = [line.strip().lower() for line in fr]
    with open('config/vegetables.txt') as ve:
        vegetables = [line.strip().lower() for line in ve]

    cur = mysql.connection.cursor()

    # housekeep existing records
    cur.execute("DELETE FROM people;")
    cur.execute("DELETE FROM friends;")
    cur.execute("DELETE FROM foods;")

    for people in people_json:
        # insert into table people
        cur.execute("INSERT INTO people(guid, `index`, has_died, balance, picture, age, \
            eyeColor, name, gender, company_id, email, phone, address, about, registered) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
            (str(people["guid"]), int(people["index"]), bool(people["has_died"]), 
            float(sub(r'[^\d.]', '', people["balance"])), str(people["picture"]), int(people["age"]), 
            str(people["eyeColor"]), str(people["name"]), str(people["gender"]), int(people["company_id"]), 
            str(people["email"]), str(people["phone"]), str(people["address"]), 
            str(people["about"]), str(people["registered"])[:-7]))

        # insert into table friends
        for friend in people["friends"]:
            cur.execute("INSERT INTO friends(`index`, friend_index) VALUES(%s, %s);", 
                (int(people["index"]), int(friend["index"])))

        # insert into table foods
        for food in people["favouriteFood"]:
            food_type = 0
            if food.lower() in fruits:
                food_type = 1
            elif food.lower() in vegetables:
                food_type = 2
            else:
                food_type = 0
            cur.execute("INSERT INTO foods(`index`, food_type, favouriteFood) VALUES (%s, %s, %s);", 
                (int(people["index"]), food_type,  food.lower()))

    mysql.connection.commit()
    cur.close()
    return make_response(json.dumps({'result': 'Upload people file successful'}), 200)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'admin'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# upload page
@app.route('/upload',methods=['GET','POST'])
@requires_auth
def upload():
    '''
    for uploading database json files
    '''
    if request.method == "POST":
        if 'companies' not in request.files and 'people' not in request.files:
            return 'No "companies" or "people" field in html form'
        # process companies.json
        if 'companies' in request.files:
            companies = request.files['companies']
            # if user doesn't select any file
            if companies.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if companies:
                try:
                    companies_json = json.load(request.files['companies']) 
                except: # exception handling
                    return 'Invalid Json file'
                return insert_companies(companies_json)

        # process people.json
        if 'people' in request.files:
            people = request.files['people']
            # if user doesn't select any file
            if people.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if people:
                try:
                    people_json = json.load(request.files['people']) 
                except: # exception handling
                    return 'Invalid Json file'
                return insert_people(people_json)
            #return json.dumps(companies_json)
    return render_template('upload.html')