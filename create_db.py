from app import db
from models import Flaskr


# Create DB
db.create_all()


# Commit changes to DB
db.session.commit()
