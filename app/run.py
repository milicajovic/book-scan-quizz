import os
import os
from app import create_app, db
from flask_migrate import Migrate, stamp

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)