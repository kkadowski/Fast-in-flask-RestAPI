from flask import Flask, jsonify, redirect
import os
from src.auth import auth
from src.bookmarks  import bookmarks
from src.database import Bookmark, db
from flask_jwt_extended import JWTManager
from src.constants import http_status_codes as cds
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config


def create_app(test_config=None):
    app = Flask(__name__, 
                instance_relative_config=True
                )
      
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'),
            SWAGGER = {
                'title': 'Bookmarks API',
                'universion' : 3
                }
        ) 
    else:
        app.config.from_mapping(test_config)
     
    db.app=app   
    db.init_app(app)
    #flask shell
    #from src.database import sb
    #db.create_all()
    #db
    #db.drop_all() - usuwanie
    
    JWTManager(app)
    
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    
    Swagger(app, config = swagger_config, template = template)
    
    # @app.route("/")
    # def index():
    #     return jsonify({"message": "Welcome to RestAPI"})

    # @app.route("/hello")
    # def hello():
    #     return jsonify({"message": "Hello - testing route..."})
    
    @app.get('/<short_url>')
    @swag_from('./docs/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()
            
            return redirect(bookmark.url)
     
    @app.errorhandler(cds.HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), cds.HTTP_404_NOT_FOUND
    
    @app.errorhandler(cds.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_505(e):
        return jsonify({'error': 'Sorry, something went wrong. We are working on it.'}), cds.HTTP_500_INTERNAL_SERVER_ERROR
    
    
    return app

