from flask import Flask, request, jsonify, Blueprint, make_response
import requests
from flask_restful import Api


app = Flask(__name__)
api = Api(app)

PRODUCT_SERVICE_URL = 'http://localhost:8003/products'
ORDER_SERVICE_URL = 'http://localhost:8002/orders'
INVENTORY_SERVICE_URL = 'http://localhost:8001/inventory'

def forward(service_url, METHOD = 'GET' , data = None):
    match METHOD:
        case 'GET':
            response = requests.get(service_url, params=data)
        case 'POST':
            response = requests.post(service_url, json=data)

        case default:
            raise ValueError("Unsupported HTTP method")
    return response

USER_CREDENTIALS = { "username" : 'reg', "password": '1234'}

def check_basic_auth():
    username = request.headers.get("username")
    password = request.headers.get("password")
    if not username or not password:
        return False
    if username != USER_CREDENTIALS["username"] or password != USER_CREDENTIALS["password"]:
        return False
    return True




@app.route('/products', methods=['GET', 'POST'])
def service1_gateway():
    if request.method == 'GET':
        response = forward(PRODUCT_SERVICE_URL, METHOD = 'GET', data = request.args)

    if request.method == 'POST':
        response = forward(PRODUCT_SERVICE_URL, METHOD = 'POST', data = request.json)
    return make_response(response.json(), response.status_code)

@app.before_request
def authorization():
    if not check_basic_auth():
        return make_response(jsonify({"error": "Unauthorized"}), 401)



@app.route('/orders', methods=['GET', 'POST'])
def service2_gateway():
    if request.method == 'GET':
        response = forward(ORDER_SERVICE_URL, METHOD = 'GET', data = request.args)

    if request.method == 'POST':
        response = forward(ORDER_SERVICE_URL, METHOD = 'POST', data = request.json)
    return make_response(response.json(), response.status_code)

@app.route('/inventory', methods=['GET', 'POST'])
def service3_gateway():
    if request.method == 'GET':
        response = forward(INVENTORY_SERVICE_URL, METHOD = 'GET', data = request.args)

    if request.method == 'POST':
        response = forward(INVENTORY_SERVICE_URL, METHOD = 'POST', data = request.json)
    return make_response(response.json(), response.status_code)

@app.route('/')
def home():
    return jsonify({"msg" : "gateway API is running"})

if __name__ == "__main__":
    app.run(debug=True, port=8004)

