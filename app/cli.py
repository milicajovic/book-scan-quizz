import click
from flask.cli import with_appcontext
from flask import current_app
from . import db
import os
from sqlalchemy import inspect


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()

    # Print all tables that SQLAlchemy is aware of
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    click.echo(f"Tables created: {', '.join(tables)}")

    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(current_app.instance_path, db_path)
        click.echo(f"SQLite database location: {os.path.abspath(db_path)}")
    else:
        click.echo(f"Database URI: {db_uri}")