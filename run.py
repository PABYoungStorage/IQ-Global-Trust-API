from app import create_app
from flask_cors import CORS

app = create_app()
# cors = CORS(app,resources={r"/*":{"origins":"http://localhost:*"}})
CORS(app, supports_credentials=True, origins='*', allow_headers='*')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
