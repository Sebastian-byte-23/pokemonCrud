from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
