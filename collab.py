from app import create_app, db
from flask_migrate import Migrate, upgrade
from app.models import Role

app = create_app()

migrate = Migrate(app, db)

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    upgrade()
    Role.insert_roles()

if __name__=='__main__':
    app.run(debug=True)

