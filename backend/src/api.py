import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
def long_and_short(input_str):
    '''
    Based on long or short we can query the drinks
    '''
    input_str_lower = input_str.lower()
    query_drinks = Drink.query.all()
    drinks_option = ['short','long']
    if input_str_lower == drinks_option[0]:
        drinks_repr = [option.short() for option in query_drinks]
    elif input_str_lower == drinks_option[1]:
         drinks_repr = [option.long() for option in query_drinks]
    else:
        print('Give input string as long or short to get the data representation')
        abort(500)
    return  drinks_repr
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
def get_short_drinks():
    '''
    Get the drinks which is drink.short()
    '''
    get_data = long_and_short('short')
    if len(get_data) == 0:
        abort(404)
    else:
	    response = {
            'success': True,
            'status_code':200,
            'drinks': get_data
        }
	    return jsonify(response)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_the_drinks_detail(data):
    '''
    Get the drinks in detail and includes drink.long()
    representation.
    '''
    get_data = long_and_short('long')
    if len(get_data) == 0:
        abort(404)
    else:
	    response = {
            'success': True,
            'status_code':200,
            'drinks': get_data
        }
	    return jsonify(response)
  

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def add_new_drink(data):
    '''
    Add new drink in the drink table
    '''
    try:
        add_title = request.get_json().get('title', None)
        add_recipe = request.get_json().get('recipe', None)
        drink = Drink(title = add_title,recipe =json.dumps(add_recipe))
        drink.insert()
        response = {
            'success' : True,
            'status_code':200,
            'drinks': drink.long()
        }
        return jsonify(response)
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:/drinks/<id>')
def add_to_existing_one(data, id):

    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} 
        where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    try:
        if request.get_json() is None:
            abort(400)
        else:
            # add the new drink in the row 
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            patch_title = request.get_json().get('title', None)
            patch_recipe = request.get_json().get('recipe', None)
            if patch_title or drink is None:
                abort(404)
            else:
                drink.title = patch_title
                drink.recipe = json.dumps(patch_recipe)
            drink.update()
            response = {
                'success': True,
                'status_code': 200,
                'drinks':[Drink.query.filter_by(id=id).first()]
            }
            return jsonify(response)
    except:
        abort(422)
    
  
@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('patch:/drinks/<id>')
def del_the_drink(data, id):
    '''
    Delete the drink based on given id
    '''
    if id is None:
        print('Provide id to delete the drink from database')
        abort(422)
    else:
            del_drinks = Drink.query.filter(Drink.id == id).one_or_none()
            if del_drinks is None:
                abort(404)
            else:
                del_drinks.delete()
                response = {
                    'success':True,
                    'status_code':200,
                    'delete':id
                }
                return jsonify(response)
## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
    Error handler for Page not found or Server not found
'''

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Page not found or Server not found"
                    }), 404

'''
Error handler for Unauthorized client status
'''
@app.errorhandler(401)
def Unauthorized_client(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized client status"
                    }), 401

'''
Error handler for Bad Request from client to server
'''
@app.errorhandler(400)
def bad_request_to_server(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad Request from client to server"
                    }), 400 

'''
Error handler for Internal Server Error server or Bad Gateway
'''
@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "Internal Server Error server or Bad Gateway"
                    }), 500                   
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error_msg):
    
    return jsonify({
                    "success": False, 
                    "error": error_msg.status_code,
                    "message": error_msg.error['description']
                    }), error_msg.status_code