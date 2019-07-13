from flask import Blueprint, render_template, request, Response, flash, redirect, session, make_response
from functools import wraps
from db import mysql
import json
import datetime
from werkzeug.routing import BaseConverter
import config
from auth import requires_auth

class DateEncoder(json.JSONEncoder):
    '''
    to convert datetime format to json acceptable format
    '''
    def default(self, obj):                     # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)

class IntListConverter(BaseConverter):
    '''
    To format the multiple id in url, e.g. 1,2,3
    '''
    regex = r'\d+(?:,\d+)*$'
    def to_python(self, value):
        return [int(x) for x in value.split(',')]
    def to_url(self, value):
        return ','.join(str(x) for x in value)

def add_app_url_map_converter(self, func, name=None):
    '''
    to map int list like 1,2 in URL
    '''
    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func
    self.record_once(register_converter)

# create int_list converter for blueprint
Blueprint.add_app_url_map_converter = add_app_url_map_converter

mod = Blueprint('v1', __name__, url_prefix='/api/v1')

# add converter to blueprint module, so it can be used in URL
mod.add_app_url_map_converter(IntListConverter, 'int_list')


@mod.route('/companies', methods=['GET'])
@requires_auth
def get_companies():
    '''
    Query companies, e.g. http://localhost:5000/api/v1/companies
    '''
    cur = mysql.connection.cursor()
    cur.execute("SELECT `index`, company FROM companies;")
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    cur.close()
    json_data=[]
    for row in rows:
        json_data.append(dict(zip(row_headers,row)))
    return json.dumps(json_data)

@mod.route('/company/<int:company_id>/employees', methods=['GET'])
@requires_auth
def get_company_by_index(company_id):
    '''
    Query company, e.g. http://localhost:5000/api/v1/company/1/employees
    '''
    json_data = []
    users_data = {}
    json_data_all = {}

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM people WHERE company_id = %s;", (company_id,))
    row_headers=[x[0] for x in cur.description]
    rows = cur.fetchall()
    cur.close()

    for row in rows:
        json_data.append(dict(zip(row_headers,row)))
    users_data["users"] = json_data
    users_data["total_count"] = len(rows)
    json_data_all.update(users_data)
    return json.dumps(json_data_all, cls=DateEncoder)

@mod.route('/people/<int_list:people_id>', methods=['GET'])
@requires_auth
def get_people(people_id):
    '''
    Query 1 people, e.g. http://localhost:5000/api/v1/people/1
    Query 2 people, e.g. http://localhost:5000/api/v1/people/3,4
    people list like 3,4 is stored in list people_id
    '''
    # for 1 people query
    if len(people_id)==1:
        json_data={}

        cur = mysql.connection.cursor()
        cur.execute("SELECT name as username, age FROM people WHERE `index` = %s;", (people_id[0],))
        row_headers=[x[0] for x in cur.description]
        rows = cur.fetchall()
        for row in rows:
            json_data.update(dict(zip(row_headers,row)))
        
        # obtain fruits data
        cur.execute("SELECT favouriteFood FROM foods WHERE `index` = %s and food_type = 1;", (people_id[0],))
        fruits = [item[0] for item in cur.fetchall()]
        fruit_data = {}
        fruit_data["fruits"] = fruits
        json_data.update(fruit_data)

        # obtain vegetables data
        cur.execute("SELECT favouriteFood FROM foods WHERE `index` = %s and food_type = 2;", (people_id[0],))
        vegetables = [item[0] for item in cur.fetchall()]
        vegetables_data = {}
        vegetables_data["vegetables"] = vegetables
        json_data.update(vegetables_data)

        cur.close()
        return json.dumps(json_data)

    # for 2 people query
    elif len(people_id)==2:
        json_data_all={}

        cur = mysql.connection.cursor()

        # obtain first user information
        cur.execute("SELECT name as username, age, address, phone FROM people WHERE `index` = %s;", (people_id[0],))
        row_headers=[x[0] for x in cur.description]
        rows = cur.fetchall()
        json_data={}
        for row in rows:
            json_data.update(dict(zip(row_headers,row)))
        user1 = {}
        user1["user_"+str(people_id[0])] = json_data
        json_data_all.update(user1)
        
        # obtain first user information
        cur.execute("SELECT name as username, age, address, phone FROM people WHERE `index` = %s;", (people_id[1],))
        row_headers=[x[0] for x in cur.description]
        rows = cur.fetchall()
        json_data={}
        for row in rows:
            json_data.update(dict(zip(row_headers,row)))
        user2 = {}
        user2["user_"+str(people_id[1])] = json_data
        json_data_all.update(user2)

        # obtain common friends
        cur.execute("SELECT T1.friend_index as friend_id, T2.name as friend_name FROM friends T1 \
                    LEFT JOIN people T2 ON T1.friend_index = T2.`index` \
                    WHERE T1.`index` = %s AND T1.friend_index <> %s AND T1.friend_index in \
                    (SELECT friend_index FROM friends WHERE `index` = %s AND friend_index <> %s) \
                    AND T2.eyeColor = 'brown' and has_died = 0;", 
                    (people_id[0], people_id[0], people_id[1], people_id[1]))
        row_headers=[x[0] for x in cur.description]
        rows = cur.fetchall()
        json_data=[]
        for row in rows:
            json_data.append(dict(zip(row_headers,row)))
        common_friends = {}
        common_friends["common_friends"] = json_data
        json_data_all.update(common_friends)

        cur.close()
        return json.dumps(json_data_all)
    else: # neither 1 nor 2 people inputted
        return make_response(json.dumps({'error': 'Incorrect people number provided'}), 400)