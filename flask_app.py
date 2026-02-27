from flask import Flask
from scraper_blueprint import scraper_bp

app = Flask(__name__)

app.register_blueprint(scraper_bp)

if __name__ == '__main__':
    app.run(debug=True)