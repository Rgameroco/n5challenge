# app/domain/vehicles/models.py
from app.extensions import db


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(255), unique=True, nullable=False)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey("persons.id"))

    def __repr__(self):
        return f"<Vehicle {self.license_plate} - {self.make} {self.model}>"
