'''
    inventory:
        id
        skucode
        quantity
'''
import requests
from flask import Blueprint,Flask,jsonify,request
#!pipenv install flask_restful
from flask_restful import Resource,Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,DECIMAL


app = Flask(__name__)

# config the connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# intialize SQLAlchemy
db= SQLAlchemy(app)

api = Api(app)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    skucode = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "skucode": self.skucode,
            "quantity": self.quantity,
        }


class InventoryResource(Resource):

    def get(self,id=None):
        if id is None:
            try:
               inventories = Inventory.query.all()
               return jsonify([inventory.to_dict() for inventory in inventories])
            except:
                return {"status": "Failed"}
        else:
            try:
                inventory = Inventory.query.get(id)
                if inventory is None:
                    return  jsonify({"error":"Not found!"})
                return jsonify(inventory.to_dict())
            except:
                return {"status": "Failed"}

        return {"Method" : "GET"}

    def post(self):
        try:
            payload = request.json
            skucode = payload['skucode']
            quantity = payload['quantity']
            new_inventory = Inventory(skucode=skucode, quantity=quantity)
            db.session.add(new_inventory)
            db.session.commit()

            return jsonify({"status": "Success", "inventory": new_inventory.to_dict()})

        except Exception as e:
            print(f"Error creating inventory: {e}")  # Log the error
            return jsonify({"status": "Failed", "error": str(e)}), 500

    def put(self, id):
        try:
            payload = request.json
            skucode = payload['skucode']
            quantity = payload['quantity']
            inventory = Inventory.query.get(id)
            if inventory is None:
                return jsonify({"error": "inventory not found"}), 404

            if skucode:
                inventory.skucode = skucode
            if quantity:
                inventory.quantity = quantity

            db.session.commit()
            return jsonify({"status": "Success", "inventory": inventory.to_dict()})
        except Exception as e:
            print(f"Error updating inventory: {e}")  # Log the error for debugging
            return {"status": "Failed"}, 500  # Return 500 Internal Server Error

    def delete(self, id):
        try:
            inventory = Inventory.query.get(id)
            if inventory is None:
                return jsonify({"error": "Product not found"}), 404

            db.session.delete(inventory)
            db.session.commit()
            return jsonify({"status": "Success", "message": "inventory deleted"})
        except Exception as e:
            print(f"Error deleting inventory: {e}")
            return {"status": "Failed"}, 500

api.add_resource(InventoryResource,'/inventory','/inventory/<int:id>')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = 8001
    discovery_server_url = "http://localhost:5005/register"
    service_name = "inventory-service"
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

