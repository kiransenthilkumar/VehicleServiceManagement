from flask import Blueprint

bp = Blueprint('vehicle', __name__)

from app.vehicle import routes

