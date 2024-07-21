from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Officer(db.Model):
    """Represents a police officer who can log traffic violations."""

    __tablename__ = "officers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unique_identifier = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Officer {self.name}>"
