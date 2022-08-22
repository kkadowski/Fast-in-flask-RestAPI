from flask import Flask, jsonify

def create_app(test_config=None):
    app = Flask(__name__, 
                instance_relative_config=True
                )
      
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = "dev",
        ) 
    else:
        app.config.from_mapping(test_config)
    
    @app.get("/")
    def index():
        return jsonify({"message": "Welcome to RestAPI"})

    @app.get("/hello")
    def hello():
        return jsonify({"message": "Hello - testing route..."})
    
    return app
