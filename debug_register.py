import traceback
from app import create_app, db
from app.models import User

def run_test():
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.app_context():
        # ensure DB exists
        db.create_all()

        client = app.test_client()

        data = {
            'username': 'testuser_debug',
            'email': 'testuser_debug@example.com',
            'full_name': 'Test User',
            'phone': '+911234567890',
            'password': 'testpass123',
            'password2': 'testpass123',
            'submit': 'Register'
        }

        try:
            resp = client.post('/auth/register', data=data, follow_redirects=True)
            print('STATUS:', resp.status_code)
            print('LENGTH:', len(resp.data))
            # print a snippet of the response for debugging
            print(resp.data.decode('utf-8', errors='replace')[:2000])
        except Exception:
            print('EXCEPTION during test POST:')
            traceback.print_exc()

if __name__ == '__main__':
    run_test()
