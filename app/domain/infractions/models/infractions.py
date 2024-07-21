# app/domain/infractions/models.py
import datetime

from app.extensions import db


class Infraction(db.Model):
    __tablename__ = "infractions"

    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(
        db.String(255), db.ForeignKey("vehicles.license_plate"), nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.Column(db.Text)
    officer_id = db.Column(
        db.Integer, db.ForeignKey("officers.id")
    )  # Usar el ID del oficial como FK

    vehicle = db.relationship(
        "Vehicle", backref=db.backref("infractions", lazy="dynamic")
    )
    officer = db.relationship(
        "Officer", backref=db.backref("infractions", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Infraction {self.id} - {self.timestamp}>"
