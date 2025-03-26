'''
    Product:
        id
        name
        description
        price

'''

from flask import Blueprint,Flask,jsonify,request
#!pipenv install flask_restful
from flask_restful import Resource,Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,DECIMAL


app = Flask(__name__)

# config the connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# intialize SQLAlchemy
db= SQLAlchemy(app)

api = Api(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), nullable = False)
    price = db.Column(db.DECIMAL(precision=10))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price
        }


class ProductResource(Resource):

    def get(self,id=None):
        if id is None:
            try:
               products = Product.query.all()
               return jsonify([product.to_dict() for product in products])
            except:
                return {"status": "Failed"}
        else:
            try:
                product = Product.query.get(id)
                if product is None:
                    return  jsonify({"error":"Not found!"})
                return jsonify(product.to_dict())
            except:
                return {"status": "Failed"}

        return {"Method" : "GET"}

    def post(self):
        try:
            payload = request.json
            name = payload["name"]
            description = payload["description"]
            price = payload["price"]
            new_product = Product(name=name, description=description, price=price)
            db.session.add(new_product)
            db.session.commit()

            return jsonify({"status": "Success", "product": new_product.to_dict()})

        except Exception as e:
            print(f"Error creating product: {e}")  # Log the error
            return jsonify({"status": "Failed", "error": str(e)}), 500

    def put(self, id):
        try:
            payload = request.json
            name = payload.get("name")
            description = payload.get("description")
            price = payload.get("price")

            product = Product.query.get(id)
            if product is None:
                return jsonify({"error": "Product not found"}), 404

            if name:
                product.name = name
            if description:
                product.description = description
            if price:
                product.price = price

            db.session.commit()
            return jsonify({"status": "Success", "product": product.to_dict()})
        except Exception as e:
            print(f"Error updating product: {e}")  # Log the error for debugging
            return {"status": "Failed"}, 500  # Return 500 Internal Server Error

    def delete(self, id):
        try:
            product = Product.query.get(id)
            if product is None:
                return jsonify({"error": "Product not found"}), 404

            db.session.delete(product)
            db.session.commit()
            return jsonify({"status": "Success", "message": "Product deleted"})
        except Exception as e:
            print(f"Error deleting product: {e}")
            return {"status": "Failed"}, 500

api.add_resource(ProductResource,'/products','/products/<int:id>')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True,port=8000)

