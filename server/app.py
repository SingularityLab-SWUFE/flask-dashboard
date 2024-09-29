from flask_migrate import Migrate

from api import create_app
from api.models import db
from config import config

app = create_app(config['production'])
db.init_app(app)

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
