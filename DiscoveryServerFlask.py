from flask import Flask, request, jsonify

app = Flask(__name__)

services = {}  # In-memory dictionary to store registered services

@app.route('/register', methods=['POST'])
def register_service():
    data = request.get_json()
    service_name = data.get('name')
    service_address = data.get('address')
    if service_name and service_address:
        services[service_name] = service_address
        return jsonify({'message': 'Service registered successfully'}), 201
    else:
        return jsonify({'error': 'Missing service name or address'}), 400

@app.route('/services', methods=['GET'])
def get_all_services():
    try:
        if not services:  # Check if services dictionary is empty
            return jsonify({"error": "No services registered!"}), 404
        return jsonify(services)  # Return the services dictionary as JSON
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500  # Return error message and 500 status

@app.route('/discover/<service_name>', methods=['GET'])
def discover_service(service_name):
    if service_name in services:
        return jsonify({'address': services[service_name]}), 200
    else:
        return jsonify({'error': 'Service not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5005)