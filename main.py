# Utilities.py
from flask import Flask, request, render_template_string
import requests
import json

app = Flask(__name__)

# HTML template with updated styles and structure
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Document Search and Analysis</title>
    <style>
        body, html {
            height: 100%;
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f2f2f2;
            color: #333;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
        .form {
            margin: 20px;
            padding: 25px;
            width: 90%;
            max-width: 640px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 10px rgba(0,0,0,0.12);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #d9d9d9;
            border-radius: 8px;
            box-sizing: border-box;
        }
        input[type="text"] {
            background-color: #eaf0f6;
        }
        input[type="submit"] {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        input[type="submit"]:hover {
            background-color: #2980b9;
        }
        .results {
            width: 90%;
            max-width: 640px;
            margin-top: 30px;
            background-color: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .results section {
            padding: 15px;
            margin-top: 10px;
            background-color: #ecf0f1;
            border-radius: 8px;
            border-left: 5px solid #3498db;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form">
            <h1>Advanced Document Search and Analysis</h1>
            <form method="post">
               
                <input type="submit" value="Crawl">
            </form>
            <form method="post">
                <input type="text" id="query" name="query" placeholder="Type your search query...">
                <input type="submit" value="Search">
            </form>
        </div>
        {% if response_content %}
            <div class="results">
                {% if response_content.get('error') %}
                    <section class="error">{{ response_content['error'] }}</section>
                {% else %}
                    <section>
                        <strong>Corrected Query:</strong> {{ response_content.get('corrected_query', '') }}
                    </section>
                    <section>
                        <strong>Distances:</strong> {{ response_content.get('distances', [])|tojson }}
                    </section>
                    <section>
                        <strong>Expanded Query:</strong> {{ response_content.get('expanded_query', '') }}
                    </section>
                    <section>
                        <strong>Indices:</strong> {{ response_content.get('indices', [])|tojson }}
                    </section>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>

'''

@app.route('/', methods=['GET', 'POST'])
def home():
    response_content = {}
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            response_content = send_request(query)
    return render_template_string(HTML_TEMPLATE, response_content=response_content)

def send_request(query):
    url = 'http://127.0.0.1:5000/query'
    json_data = {'query': query, 'top_k': 5}
    try:
        response = requests.post(url, json=json_data)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Attempt to parse JSON
    except requests.exceptions.HTTPError as err:
        return {'error': f'HTTP error: {err}'}
    except requests.exceptions.RequestException as err:
        return {'error': f'Request error: {err}'}
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON received'}
    except Exception as err:
        return {'error': f'An unexpected error occurred: {err}'}

if __name__ == '__main__':
    app.run(debug=True, port=5001)