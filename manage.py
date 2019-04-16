from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from approval_system import create_app
from approval_system.extensions import db

app = create_app()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
