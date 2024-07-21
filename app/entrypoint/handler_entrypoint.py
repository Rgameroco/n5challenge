# app/entrypoint/handler_entrypoint.py
from app import create_app
from app.domain.infractions import infraction_blueprint
from app.domain.users import officer_blueprint, person_blueprint
from app.domain.vehicles import vehicle_blueprint

app = create_app()
app.register_blueprint(person_blueprint, url_prefix="/persons")
app.register_blueprint(officer_blueprint, url_prefix="/officers")
app.register_blueprint(infraction_blueprint, url_prefix="/infractions")
app.register_blueprint(vehicle_blueprint, url_prefix="/vehicles")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
