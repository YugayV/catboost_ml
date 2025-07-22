from api.app import create_app
from api.config import DevelopmentConfig, ProductionConfig
import os

application = create_app( 
    config_object=ProductionConfig if os.getenv("FLASK_ENV") == 'production' else DevelopmentConfig
)

if __name__ == '__main__': 
    application.run( 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000))
    )