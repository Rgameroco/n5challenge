# app/domain/users/models.py
from app.extensions import db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    vehicles = db.relationship(
        "Vehicle", backref=db.backref("owner", uselist=False), lazy=True
    )

    def __repr__(self):
        return f"<Person {self.name}>"
