from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin, customer, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_staff(self):
        return self.role == 'staff'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)  # Petrol, Diesel, Electric, Hybrid
    manufacturing_year = db.Column(db.Integer, nullable=False)
    current_odometer = db.Column(db.Integer, default=0, nullable=False)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='vehicle', lazy='dynamic', cascade='all, delete-orphan')
    service_records = db.relationship('ServiceRecord', backref='vehicle', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='vehicle', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('ServiceReminder', backref='vehicle', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vehicle {self.registration_number}>'


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    service_type = db.Column(db.String(100), nullable=False)  # Regular Service, Repair, Custom
    custom_service_description = db.Column(db.Text)
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.Time)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, in_progress, completed, cancelled, rejected
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    service_record = db.relationship('ServiceRecord', backref='service_request', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ServiceRequest {self.id} - {self.status}>'


class ServiceRecord(db.Model):
    __tablename__ = 'service_records'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), unique=True, nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    parts_replaced = db.Column(db.Text)  # JSON or text description
    labor_charge = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    additional_cost = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    service_notes = db.Column(db.Text)
    odometer_reading = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='service_record', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ServiceRecord {self.id} - {self.vehicle_id}>'


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'), unique=True, nullable=False, index=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, paid, cancelled
    payment_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False)  # Insurance, RC, Pollution, Other
    file_path = db.Column(db.String(255), nullable=False)
    expiry_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    def is_expired(self):
        if self.expiry_date:
            return datetime.now().date() > self.expiry_date
        return False
    
    def is_expiring_soon(self, days=30):
        if self.expiry_date:
            today = datetime.now().date()
            days_until_expiry = (self.expiry_date - today).days
            return 0 <= days_until_expiry <= days
        return False
    
    def __repr__(self):
        return f'<Document {self.document_type} - {self.vehicle_id}>'


class ServiceReminder(db.Model):
    __tablename__ = 'service_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    last_service_date = db.Column(db.Date)
    last_service_odometer = db.Column(db.Integer)
    next_service_date = db.Column(db.Date)
    next_service_odometer = db.Column(db.Integer)
    reminder_type = db.Column(db.String(20), default='date', nullable=False)  # date, km, both
    is_notified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    def is_due(self):
        if self.reminder_type in ['date', 'both']:
            if self.next_service_date and datetime.now().date() >= self.next_service_date:
                return True
        if self.reminder_type in ['km', 'both']:
            vehicle = Vehicle.query.get(self.vehicle_id)
            if vehicle and self.next_service_odometer and vehicle.current_odometer >= self.next_service_odometer:
                return True
        return False
    
    def is_due_soon(self, days=30):
        if self.reminder_type in ['date', 'both']:
            if self.next_service_date:
                today = datetime.now().date()
                days_until = (self.next_service_date - today).days
                return 0 <= days_until <= days
        return False
    
    def __repr__(self):
        return f'<ServiceReminder {self.id} - {self.vehicle_id}>'

