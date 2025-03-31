'''
    order:
        id
        skucode
        price
        quantity
'''
import atexit

import requests
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
# import consul  # Import the consul library
# import socket  # Import socket for getting the host IP
import logging
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)
api = Api(app)

# # Consul setup
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# consul_client = consul.Consul(host='127.0.0.1', port=8500)
#
# service_name = 'order-service'
# service_port = 8002

# def get_primary_ip():
#     """
#     Gets the primary network interface's IP address.
#     This is more robust than socket.gethostbyname() in many cases.
#     """
#     try:
#         for iface in netifaces.interfaces():
#             iface_details = netifaces.ifaddresses(iface)
#             if netifaces.AF_INET in iface_details:
#                 for ip_info in iface_details[netifaces.AF_INET]:
#                     if 'netmask' in ip_info and ip_info['netmask'] != '255.255.255.255':
#                         return ip_info['addr']
#         return '127.0.0.1'  # Fallback
#     except Exception:
#         return '127.0.0.1'


# host_ip = get_primary_ip()  # Get the primary IP address



#
# def register_with_consul():
#     consul_client.agent.service.register(
#         name=service_name,
#         service_id=service_name + '-' + str(service_port),
#         address=host_ip,
#         port=service_port,
#         check=consul.Check.http(f'http://{host_ip}:{service_port}/health', interval='10s')
#     )
#     logging.info(f"Registered service {service_name} with Consul at {host_ip}:{service_port}")
#
#
# def deregister_from_consul():
#     consul_client.agent.service.deregister(service_id=service_name + '-' + str(service_port))
#     logging.info(f"Deregistered service {service_name} from Consul")

#
# @app.route('/health')
# def health_check():
#     return jsonify({"status": "UP"}), 200


class Order(db.Model):  # Your database model
    id = db.Column(db.Integer, primary_key=True)
    skucode = db.Column(db.String(50), nullable=False)
    price = db.Column(db.DECIMAL(precision=10))
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "skucode": self.skucode,
            "price": self.price,
            "quantity": self.quantity
        }


class OrderResource(Resource):  # Your Flask-RESTful resource
    def get(self, id=None):
        if id is None:
            try:
                orders = Order.query.all()
                return jsonify([order.to_dict() for order in orders])
            except:
                return {"status": "Failed"}
        else:
            try:
                order = Order.query.get(id)
                if order is None:
                    return jsonify({"error": "Not found!"})
                return jsonify(order.to_dict())
            except:
                return {"status": "Failed"}

    def post(self):
        try:
            payload = request.json
            skucode = payload['skucode']
            price = payload['price']
            quantity = payload['quantity']

            # Assuming checkInventory is a function you've defined elsewhere
            if checkInventory(skucode, quantity):
                new_order = Order(skucode=skucode, price=price, quantity=quantity)
                db.session.add(new_order)
                db.session.commit()

                return jsonify({"status": "Success", "order": new_order.to_dict()})
            else:
                return jsonify({
                    "status": "Failed",
                    "error": "Inventory check failed for skucode: " + skucode
                }), 400
        except Exception as e:
            print(f"Error creating order: {e}")
            return jsonify({"status": "Failed", "error": str(e)}), 500

    def put(self, id):
        try:
            payload = request.json
            skucode = payload['skucode']
            price = payload['price']
            quantity = payload['quantity']
            order = Order.query.get(id)
            if order is None:
                return jsonify({"error": "order not found"}), 404

            if skucode:
                order.skucode = skucode
            if price:
                order.price = price
            if quantity:
                order.quantity = quantity

            db.session.commit()
            return jsonify({"status": "Success", "order": order.to_dict()})
        except Exception as e:
            print(f"Error updating order: {e}")
            return {"status": "Failed"}, 500

    def delete(self, id):
        try:
            order = Order.query.get(id)
            if order is None:
                return jsonify({"error": "order not found"}), 404

            db.session.delete(order)
            db.session.commit()
            return jsonify({"status": "Success", "message": "order deleted"})
        except Exception as e:
            print(f"Error deleting order: {e}")
            return {"status": "Failed"}, 500


api.add_resource(OrderResource, '/orders', '/orders/<int:id>')


def checkInventory(skucode, quantity):  # Your inventory check function
    try:
        service_inventory_url = "http://127.0.0.1:8001/inventory"
        response = requests.get(service_inventory_url)
        response.raise_for_status()
        inventory = response.json()
        print(type(inventory))
        found = False
        for item in inventory:
            if skucode == item["skucode"] and item["quantity"] - quantity > 1:
                found = True
        return found
    except Exception as e:
        print(f"Error in checkInventory: {e}")  # Add logging here
        return False


# if __name__ == '__main__':
#     # Register with Consul *before* starting the Flask app
#     # register_with_consul()
#     # # Register deregistration to happen automatically on exit
#     # atexit.register(deregister_from_consul)
#     with app.app_context():
#         db.create_all()
#     # Start the Flask app.  This will now run *after* registration.
#     # app.run(debug=True, port=service_port, host=host_ip)
#     app.run(debug=True)

if __name__ == "__main__":
    port = 8002
    discovery_server_url = "http://localhost:5005/register"
    service_name = "order-service"
    service_address = f"http://localhost:{port}"

    registration_data = {
        "name": service_name,
        "address": service_address
    }

    try:
        response = requests.post(discovery_server_url, json=registration_data)
        response.raise_for_status()
        print(f"Service {service_name} registered successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to register service {service_name}: {e}")

    app.run(debug=True, port=port)