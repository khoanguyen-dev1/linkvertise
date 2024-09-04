import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
port = int(os.getenv('PORT', 8080))

# Configure logging
logger = logging.getLogger('api_usage')
logger.setLevel(logging.INFO)
log_file_path = '/tmp/api_usage.log'  # Adjust this path if needed
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_client_ip():
    """Get the client's IP address, considering possible proxy headers."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/linkbeta', methods=['GET'])
def fluxus():
    link = request.args.get('link')
    client_ip = get_client_ip()
    logger.info(f"Request from IP: {client_ip}")

    if not link:
        return jsonify({'error': 'Link is required'}), 400

    try:
        final_url = f'https://api.bypass.vip/bypass?url={link}'
        logger.info(f"Requesting final URL: {final_url}")
        final_response = requests.get(final_url)
        final_response.raise_for_status()
        final_data = final_response.json()
        key = final_data.get{"result")
        # Remove the "selling" key from the data if present
        final_data.pop('selling', None)
        return jsonify({"key" : key})
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while accessing {final_url}: {http_err}")
        return jsonify({'error': 'HTTP error occurred'}), 500
    except requests.RequestException as req_err:
        logger.error(f"API Request Error while accessing {final_url}: {req_err}")
        return jsonify({'error': 'Request error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error while accessing {final_url}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Ensure debug=False in production
    )
