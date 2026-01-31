from app import create_app, db
from app.models import User
from config import Config
import os

app = create_app()

# Initialize on startup (for Render and other platforms)
with app.app_context():
    db.create_all()
    # Only seed if database is empty
    if User.query.count() == 0:
        print("Initializing database with seed data...")
        try:
            from seed_data import seed_database
            seed_database()
        except Exception as e:
            print(f"Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: Create admin user
            admin = User(
                username='admin',
                email='admin@vehicleservice.com',
                full_name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created. Username: admin, Password: admin123")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
