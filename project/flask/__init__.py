import os
import dotenv
from flask import Flask

from project.middleware.dbConnect import DBConnect
from project.middleware.authService import AuthService

from project.flask.docker import DockerController
from project.flask.service import DockerServiceController

dotenv.load_dotenv()
debug_mode = True if os.getenv('DEBUG_MODE') == '1' else False

def create_app(config_filename=None, instance_relative_config=True):
    app = Flask(__name__)
    
    if config_filename is not None:
        app.config.from_pyfile(config_filename)
    
    app.wsgi_app = AuthService(app.wsgi_app)
    app.wsgi_app = DBConnect(app.wsgi_app)

    app.add_url_rule('/info', view_func=DockerController.getInfo, endpoint='get_info', methods=['GET'])
    app.add_url_rule('/service/<service_id>/update', view_func=DockerServiceController.update, endpoint='get_service_update_post', methods=['POST'])

    return app