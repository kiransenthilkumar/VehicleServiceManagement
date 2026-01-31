"""
Seed script to populate database with Tamil Nadu users, vehicles, service records, invoices, and reminders.
Creates 5 users (Tamil Nadu names/places), each with 2 vehicles and 2 service records per vehicle.
Run with: venv\Scripts\python.exe seed_data.py
"""
from app import create_app, db
from app.models import User, Vehicle, ServiceRequest, ServiceRecord, Invoice, ServiceReminder
from datetime import datetime, timedelta
from decimal import Decimal
import random


def seed_database():
    app = create_app()
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        # Admin
        admin = User(username='admin', email='admin@vehiclecare.local', full_name='Administrator', phone='+91-9000000000', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        # Tamil Nadu users (5)
        users_info = [
            {'username': 'sundar', 'email': 'sundar@example.com', 'full_name': 'Sundar R', 'phone': '+91-9840010001', 'city': 'Chennai'},
            {'username': 'meena', 'email': 'meena@example.com', 'full_name': 'Meena K', 'phone': '+91-9840020002', 'city': 'Coimbatore'},
            {'username': 'arun', 'email': 'arun@example.com', 'full_name': 'Arun V', 'phone': '+91-9840030003', 'city': 'Madurai'},
            {'username': 'lakshmi', 'email': 'lakshmi@example.com', 'full_name': 'Lakshmi S', 'phone': '+91-9840040004', 'city': 'Tiruchirappalli'},
            {'username': 'karthik', 'email': 'karthik@example.com', 'full_name': 'Karthik P', 'phone': '+91-9840050005', 'city': 'Salem'},
            # Additional requested users
            {'username': 'sachin', 'email': 'sachin@example.com', 'full_name': 'Sachin', 'phone': '+91-9840060006', 'city': 'Chennai'},
            {'username': 'nishanth', 'email': 'nishanth@example.com', 'full_name': 'Nishanth R', 'phone': '+91-9840070007', 'city': 'Coimbatore'},
            {'username': 'mouli', 'email': 'mouli@example.com', 'full_name': 'Mouli K', 'phone': '+91-9840080008', 'city': 'Madurai'},
        ]

        users = []
        for u in users_info:
            user = User(username=u['username'], email=u['email'], full_name=u['full_name'], phone=u['phone'], role='customer')
            user.address = f"{u['city']}, Tamil Nadu, India"
            user.set_password('password123')
            db.session.add(user)
            users.append({'obj': user, 'city': u['city']})

        db.session.commit()

        # Vehicles per user (2 each)
        print('Creating vehicles and service data...')
        vehicles = []
        reg_counter = 1
        for u in users:
            user_obj = u['obj']
            city_code = {
                'Chennai': 'TN-01',
                'Coimbatore': 'TN-38',
                'Madurai': 'TN-58',
                'Tiruchirappalli': 'TN-81',
                'Salem': 'TN-54'
            }.get(u['city'], 'TN-99')

            for vnum in range(2):
                reg = f"{city_code}-AA-{reg_counter:04d}"
                reg_counter += 1
                brands = ['Maruti Suzuki', 'Hyundai', 'Honda', 'Toyota', 'Tata']
                models = ['Swift', 'i20', 'City', 'Innova', 'Nexon']
                brand = random.choice(brands)
                model = random.choice(models)
                manufacture = random.randint(2016, 2023)
                odo = random.randint(5000, 60000)

                vehicle = Vehicle(user_id=user_obj.id, registration_number=reg, brand=brand, model=model, fuel_type=random.choice(['Petrol', 'Diesel', 'CNG']), manufacturing_year=manufacture, current_odometer=odo)
                db.session.add(vehicle)
                db.session.flush()
                vehicles.append(vehicle)

                # Create 2 service records per vehicle (older and recent)
                for months_ago in (10, 3):
                    service_date = (datetime.now() - timedelta(days=30*months_ago)).date()
                    labor = Decimal(random.randint(800, 4500))
                    extra = Decimal(random.randint(200, 2000))
                    total = labor + extra
                    stype = random.choice(['Regular Service', 'Repair', 'AC Service'])

                    # ServiceRequest
                    sr_req = ServiceRequest(vehicle_id=vehicle.id, user_id=user_obj.id, service_type=stype, preferred_date=service_date, status='completed', created_at=datetime.combine(service_date, datetime.min.time()) - timedelta(days=5))
                    db.session.add(sr_req)
                    db.session.flush()

                    # ServiceRecord (include service_type to satisfy NOT NULL constraint)
                    sr = ServiceRecord(service_request_id=sr_req.id, vehicle_id=vehicle.id, service_date=service_date, service_type=stype, total_amount=total, service_notes=f"Service on {service_date} for {vehicle.registration_number}", parts_replaced='Oil Filter, Brake Pads', labor_charge=labor, additional_cost=extra, odometer_reading=odo - random.randint(500, 3000))
                    db.session.add(sr)
                    db.session.flush()

                    # Invoice
                    inv_num = f"INV-{service_date.strftime('%Y%m%d')}-{sr.id:05d}"
                    invoice = Invoice(service_record_id=sr.id, invoice_number=inv_num, amount=total, payment_status='paid', payment_date=datetime.combine(service_date, datetime.min.time()) + timedelta(days=1))
                    db.session.add(invoice)

                # Add a service reminder based on last service
                last_service = datetime.now().date() - timedelta(days=30*3)
                reminder = ServiceReminder(vehicle_id=vehicle.id, last_service_date=last_service, last_service_odometer=vehicle.current_odometer, next_service_date=last_service + timedelta(days=180), next_service_odometer=vehicle.current_odometer + 10000, reminder_type='both')
                db.session.add(reminder)

        db.session.commit()

        print('\n' + '='*50)
        print('Seeding complete:')
        print(f'  Admin: admin / admin123')
        for u in users:
            print(f"  User: {u['obj'].username} — password: password123 — city: {u['city']}")
        print('  Each user has 2 vehicles (with TN registration) and each vehicle has 2 service records + invoice + reminder')
        print('='*50 + '\n')


if __name__ == '__main__':
    seed_database()

