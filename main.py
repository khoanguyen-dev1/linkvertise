import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from bs4 import BeautifulSoup
import os
import requests

app = Flask(__name__)
CORS(app)
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

@app.route('/fluxus', methods=['GET'])
def fluxus():
    link = request.args.get('link')
    client_ip = get_client_ip()
    logger.info(f"Request from IP: {client_ip}")

    if not link:
        return jsonify({'error': 'Link is required'}), 400

    try:
        final_url = f'https://api-bypass.robloxexecutorth.workers.dev/fluxus?url={link}'
        logger.info(f"Requesting final URL: {final_url}")
        final_response = requests.get(final_url)
        final_response.raise_for_status()
        final_data = final_response.json()
        key = final_data.get('key')  
        final_data.pop('selling', None)  
        return jsonify({"result": key})
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while accessing {final_url}: {http_err}")
        return jsonify({'error': 'HTTP error occurred'}), 500
    except requests.RequestException as req_err:
        logger.error(f"API Request Error while accessing {final_url}: {req_err}")
        return jsonify({'error': 'Request error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error while accessing {final_url}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
@app.route('/socialwolvez', methods=['GET'])
def socialwolvez():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'Missing parameter: url'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', {'id': '__NUXT_DATA__'})
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                
                extracted_url = data[5]
                extracted_name = data[6]

                if extracted_url and extracted_name:
                    return jsonify({'result': extracted_url, 'name': extracted_name})
                else:
                    return jsonify({'error': 'Required data not found in the JSON structure.'}), 500

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                return jsonify({'error': 'Failed to parse JSON data.', 'details': str(e)}), 500
        else:
            return jsonify({'error': 'Script tag with JSON data not found.'}), 404

    except requests.RequestException as e:
        return jsonify({'error': 'Failed to make request to the provided URL.', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Ensure debug=False in production
    )
