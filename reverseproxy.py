from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

discovery_server_url = "http://localhost:5005/discover/"

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    service_name = get_service_name(path)
    if not service_name:
        return jsonify({"error": "Service not found for path"}), 404

    try:
        discovery_response = requests.get(discovery_server_url + service_name)
        discovery_response.raise_for_status()
        service_address = discovery_response.json()['address']

        target_url = f"{service_address}/{path}"

        # Forward the request to the target service
        target_response = requests.request(
            method=request.method,
            url=target_url,
            headers=request.headers,
            json=request.get_json(),
            params=request.args,
            stream=True,
        )

        # Return the response from the target service
        return Response(
            target_response.content,
            target_response.status_code,
            headers=target_response.headers.items(),
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Proxy error: {e}"}), 500

def get_service_name(path):
    if path.startswith('products'):
        return 'product-service'
    elif path.startswith('inventory'):
        return 'inventory-service'
    elif path.startswith('orders'):
        return 'orders-service'
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True, port=8004)