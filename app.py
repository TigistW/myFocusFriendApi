from config import create_app
from flask_cors import CORS
app = create_app()
# Allow requests from a specific domain (replace with your front-end's domain)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

# Your API routes go here
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
