from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS, PATCH"
    )
    return response

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(jwt):
    drink_list = Drink.query.order_by(Drink.id).all()
    drinks = [drink.short() for drink in drink_list]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail/<int:drink_id>', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt, drink_id):
    try:
        drinks = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if drinks is None:
            abort(404)
        else:
            return jsonify({
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            })
    
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
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
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_None()

        if drink is None:
            abort(404)

        else:
            drink.delete()

            return jsonify({
                "success": True,
                "deleted": drink_id
            })
    except:
        abort(422)

# Error Handling
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
@app.errorhandler(400)
def bad_request(error):
    return (jsonify({
        "success": False,
        "error": 400,
        "message": "your request is not acceptable"
    }), 400)
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return (jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404)

@app.errorhandler(401)
def unauthorized_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "You are not authorised for this request"
    }), 401

@app.errorhandler(403)
def forbidden_request(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "You are forbidden to perform this request"
    }), 403


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return 
