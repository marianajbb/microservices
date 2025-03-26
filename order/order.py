'''
    order:
        id
        skucode
        price
        quantity
'''

from flask import Blueprint,Flask,jsonify,request
#!pipenv install flask_restful
from flask_restful import Resource,Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,DECIMAL


app = Flask(__name__)

# config the connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# intialize SQLAlchemy
db= SQLAlchemy(app)

api = Api(app)


class Order(db.Model):
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


class OrderResource(Resource):

    def get(self,id=None):
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
                    return  jsonify({"error":"Not found!"})
                return jsonify(order.to_dict())
            except:
                return {"status": "Failed"}


    def post(self):
        try:
            payload = request.json
            skucode = payload['skucode']
            price = payload['price']
            quantity = payload['quantity']
            new_order = Order(skucode=skucode, price=price, quantity=quantity)
            db.session.add(new_order)
            db.session.commit()

            return jsonify({"status": "Success", "order": new_order.to_dict()})

        except Exception as e:
            print(f"Error creating order: {e}")  # Log the error
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
            print(f"Error updating order: {e}")  # Log the error for debugging
            return {"status": "Failed"}, 500  # Return 500 Internal Server Error

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

api.add_resource(OrderResource,'/orders','/orders/<int:id>')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True,port=8000)

