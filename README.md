# Vehicle Maintenance and Service Management System

A comprehensive, professional web-based solution for managing vehicle servicing operations efficiently for both service centers and vehicle owners. Built with Flask and featuring a modern, responsive design with beautiful gradient theme.

![Vehicle Service Management](https://img.shields.io/badge/Flask-3.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.12+-green) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0-purple) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Key Features

### 🔐 Authentication & Authorization
- Secure user registration and login with password hashing
- Role-based access control (Admin, Customer)
- Session management with Flask-Login
- Secure password storage with Werkzeug

### 🚗 Vehicle Management
- Register and manage multiple vehicles per account
- Comprehensive vehicle details (registration, brand, model, fuel type, year, odometer)
- Upload and manage vehicle images with automatic sizing
- Vehicle-wise service history and maintenance tracking
- TN registration format support (Tamil Nadu: TN-XX-AA-XXXX)

### 📅 Service Booking & Management
- Request vehicle servicing with multiple service types
- Choose preferred date and time slots
- Real-time status tracking (pending → approved → in_progress → completed)
- Admin approval, rescheduling, and rejection options
- Service completion with detailed service records

### 📋 Service Records & Maintenance History
- Detailed service records with parts, labor, and costs
- Complete maintenance timeline per vehicle
- Immutable service history for accurate auditing
- Service type tracking and documentation

### 🔔 Service Reminders
- Automated reminder system for upcoming services
- Next service calculation based on:
  - Time intervals (6 months default)
  - Mileage intervals (10,000 km default)
- Dashboard notifications for upcoming/overdue services
- Customizable reminder types (date-based, mileage-based, or both)

### 💰 Billing & Invoice Management
- Automatic invoice generation upon service completion
- Detailed invoices with service breakdown
- Dual payment processing:
  - **Customer Payment**: Online payment simulation (Credit Card, UPI, Net Banking)
  - **Admin Cash Payment**: One-click cash payment marking from admin panel
- Payment status tracking (pending, paid)
- Payment date recording and history
- Download and view invoices

### 📄 Document Management
- Upload and store vehicle documents (Insurance, RC, Pollution Certificate, etc.)
- Track document expiry dates with status indicators
- Document expiry reminders (30 days before expiry)
- Download documents with version tracking
- Expiry status badges:
  - 🔴 Expired (red badge)
  - 🟡 Expiring Soon (yellow badge - within 30 days)
  - 🟢 Valid (green badge)

### 📊 Dashboard & Analytics

#### Customer Dashboard
- Overview of registered vehicles
- Upcoming and recent service schedules
- Service history with expense tracking
- Expiring documents alerts
- Quick access to payment pages
- Service request status tracking

#### Admin Dashboard
- Real-time statistics (vehicles, customers, service requests)
- Daily service requests tracking
- Pending jobs and in-progress services
- Monthly revenue summaries with charts
- Payment tracking and pending invoices
- Yearly maintenance cost reports
- Vehicle-wise expense summaries with risk analysis

#### Reports & Analytics
- **Monthly Maintenance Cost Chart**: Visual representation of maintenance expenses by month
- **Top Vehicles by Maintenance Expense Table** with:
  - Vehicle registration and details
  - Service count per vehicle
  - Total maintenance expense
  - **Maintenance Risk Level** (new feature):
    - 🔴 **High Risk**: Cost per service > 130% of average
    - 🟡 **Medium Risk**: Cost per service > 80% of average
    - 🟢 **Low Risk**: Cost per service within normal range
  - Helps identify vehicles needing attention

## 🎨 UI/UX Features

- **Premium Design**: Professional blue-to-coral gradient theme (#0b3d91 → #ff7a59)
- **Hero Section**: Eye-catching landing page with compelling copy
- **Bootstrap 5**: Modern, responsive UI components
- **Custom CSS**: Enhanced styling with gradients and shadows
- **Icons**: Bootstrap Icons throughout the interface
- **Responsive Layout**: Mobile, tablet, and desktop friendly
- **Smooth Animations**: Transitions and hover effects
- **Status Badges**: Color-coded status indicators throughout the app

## 🚀 Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VehicleServiceManagementWebiste
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database with seed data**
   ```bash
   python seed_data.py
   ```
   This will create:
   - Admin user (admin / admin123)
   - 8 Tamil Nadu users with realistic names
   - 16 vehicles (2 per user) with TN registration numbers
   - 64 service records (2 per vehicle)
   - Invoices, reminders, and service requests

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Open your browser: `http://localhost:5000`
   - Admin panel: `http://localhost:5000/admin`

### Deploy to Render

1. **Fork/Clone this repository**

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt && python seed_data.py`
   - Start Command: `gunicorn run:app`

3. **Add Environment Variables**
   - `SECRET_KEY`: Generate a strong secret key
   - `FLASK_ENV`: Set to `production`

4. **Deploy**
   - Render will automatically build and deploy
   - Database will be created and seeded on first run

## 🔑 Default Credentials

After running `python seed_data.py`:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`

### Tamil Nadu Sample Customers

Each user has **2 vehicles** (with TN registration format) and **4 service records** pre-populated:

| Username | Full Name | City | Registration Format | Password |
|----------|-----------|------|-------------------|----------|
| `sundar` | Sundar R | Chennai | TN-01-AA-XXXX | `password123` |
| `meena` | Meena K | Coimbatore | TN-38-AA-XXXX | `password123` |
| `arun` | Arun V | Madurai | TN-58-AA-XXXX | `password123` |
| `lakshmi` | Lakshmi S | Tiruchirappalli | TN-81-AA-XXXX | `password123` |
| `karthik` | Karthik P | Salem | TN-54-AA-XXXX | `password123` |
| `sachin` | Sachin | Chennai | TN-01-AA-XXXX | `password123` |
| `nishanth` | Nishanth R | Coimbatore | TN-38-AA-XXXX | `password123` |
| `mouli` | Mouli K | Madurai | TN-58-AA-XXXX | `password123` |

**⚠️ Important**: Change default passwords in production!

## 📁 Project Structure

```
VehicleServiceManagementWebiste/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models (7 models)
│   ├── forms.py                 # WTForms definitions
│   ├── utils.py                 # Utility functions
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # Login, register, logout
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py            # Dashboard, profile, index
│   ├── vehicle/
│   │   ├── __init__.py
│   │   └── routes.py            # Register, view, edit vehicles
│   ├── service/
│   │   ├── __init__.py
│   │   └── routes.py            # Service requests, booking, payments
│   ├── admin/
│   │   ├── __init__.py
│   │   └── routes.py            # Admin panel, analytics, reports
│   └── document/
│       ├── __init__.py
│       └── routes.py            # Document upload, management
├── templates/
│   ├── base.html                # Base template with navigation
│   ├── index.html               # Landing page (redesigned with gradient)
│   ├── admin/
│   │   ├── dashboard.html       # Admin statistics dashboard
│   │   ├── reports.html         # Analytics with charts and risk levels
│   │   ├── invoices.html        # Invoice management with cash paid button
│   │   ├── requests.html        # Service request management
│   │   ├── vehicles.html        # All vehicles view
│   │   ├── customers.html       # All customers view
│   │   └── vehicle_view.html    # Single vehicle with documents section
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── main/
│   │   ├── dashboard.html       # Customer dashboard
│   │   └── profile.html
│   ├── service/
│   │   ├── request.html         # Service request form
│   │   ├── list.html            # Service requests list
│   │   ├── view_request.html    # Service request detail with cash paid button
│   │   ├── complete.html        # Complete service form
│   │   ├── history.html         # Service history
│   │   ├── invoice.html         # Invoice view
│   │   ├── pay.html             # Payment processing page
│   │   └── update_status.html   # Status update form
│   ├── vehicle/
│   │   ├── register.html        # Vehicle registration
│   │   ├── list.html            # Vehicle list
│   │   ├── edit.html            # Edit vehicle details
│   │   └── view.html            # Vehicle detail view
│   └── document/
│       ├── upload.html          # Document upload form
│       └── expiring.html        # Expiring documents list
├── static/
│   └── css/
│       └── style.css            # Custom CSS (gradients, animations)
├── uploads/
│   ├── documents/               # Uploaded documents
│   └── vehicles/                # Vehicle images
├── config.py                    # Configuration settings
├── seed_data.py                 # Database seeding (8 users, 16 vehicles)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
├── runtime.txt                  # Python version
└── README.md                    # This file
```

## 🗄️ Database Models (7 Models)

- **User**: Users with roles (admin, customer) with authentication
- **Vehicle**: Vehicle information with ownership and registration
- **ServiceRequest**: Service booking requests with status tracking
- **ServiceRecord**: Completed service records with cost breakdown
- **Invoice**: Service invoices with payment tracking
- **Document**: Vehicle documents with expiry date management
- **ServiceReminder**: Automated maintenance reminders (date/mileage based)

## 🎯 Payment System

### Customer Payment Flow
1. Service completed → Invoice generated (status: pending)
2. Customer navigates to "Pay Invoice" button
3. Selects payment method:
   - Credit/Debit Card
   - Online Payment (UPI/Net Banking)
4. Clicks "Process Payment" → **Instant payment processing**
5. Invoice marked as paid
6. Success message with payment details
7. Redirects to invoice view showing ✓ Paid status

### Admin Cash Payment Flow
1. Admin views completed service request
2. **Cash Paid** button visible when status is completed
3. One-click mark as paid for cash payments
4. Invoice status changes to paid
5. Success message with payment details

### Payment Status Indicators
- 🔴 **Pending**: Payment awaiting
- ✓ **Paid**: Payment received (shows payment date)

## 🔧 Configuration

Edit `config.py` to customize:
- Database URI and connection settings
- Upload folder paths (documents, vehicles)
- File size limits (documents: 5MB, images: 2MB)
- Service reminder intervals:
  - Time-based: 6 months (182 days)
  - Mileage-based: 10,000 km
- Document expiry reminder: 30 days before expiry
- Session configuration

## 🔒 Security Features

- **Password Security**: Werkzeug password hashing and verification
- **Input Validation**: WTForms validation on all forms
- **File Upload Security**: Allowed extensions validation, size limits
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **XSS Protection**: Jinja2 auto-escaping on all templates
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Role-based Access Control**: Admin-only routes protected
- **Secure File Paths**: Uploads stored outside web root

## 📝 Key Routes

### Public Routes
- `/` - Landing page
- `/auth/register` - User registration
- `/auth/login` - User login

### Customer Routes
- `/dashboard` - Customer dashboard
- `/vehicle/register` - Register vehicle
- `/vehicle/list` - View all vehicles
- `/service/request` - Request service
- `/service/list` - View service requests
- `/service/history/<vehicle_id>` - Service history
- `/service/invoice/<invoice_id>` - View invoice
- `/service/pay/<invoice_id>` - Payment page
- `/document/upload` - Upload documents
- `/document/expiring` - Expiring documents

### Admin Routes
- `/admin/dashboard` - Admin dashboard
- `/admin/reports` - Analytics and reports (with Maintenance Risk Level)
- `/admin/vehicles` - All vehicles
- `/admin/customers` - All customers
- `/admin/invoices` - Invoice management (with cash paid button)
- `/admin/requests` - Service request management
- `/admin/vehicle/<vehicle_id>` - Vehicle details with documents

## 📊 Technologies Used

- **Backend**: Flask 3.0.0 with Flask-SQLAlchemy ORM
- **Database**: SQLite (local and production)
- **Authentication**: Flask-Login with Werkzeug security
- **Forms**: WTForms with Flask-WTF CSRF protection
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js for analytics visualization
- **Server**: Gunicorn (production)
- **Deployment**: Render

## 🌟 Recent Enhancements (Latest Session)

✅ **Professional Homepage Redesign**
- Premium blue-to-coral gradient theme
- Compelling hero section with updated copy
- Fixed invoicing icon (inline SVG)
- Professional feature showcase

✅ **Cash Payment for Admin**
- One-click "Cash Paid" button on completed service requests
- Instant payment recording without customer interaction
- Visible only when service status is "completed"

✅ **Maintenance Risk Level Feature**
- Replaced progress bar with actionable risk indicators
- Risk calculation based on cost per service vs. average
- 🔴 High Risk | 🟡 Medium Risk | 🟢 Low Risk
- Helps identify maintenance issues early

✅ **Payment System Optimization**
- Instant payment processing (0ms delay)
- Removed modals and loading screens
- Direct form submission
- Real-time success feedback

✅ **Database Seeding**
- 8 Tamil Nadu users with realistic names
- Authentic TN registration numbers (TN-XX-AA-XXXX)
- 16 vehicles with service history
- Complete invoice and reminder setup

## 📈 Statistics (Seeded Data)

- **8 Users** (1 admin + 7 customers)
- **16 Vehicles** (2 per customer with TN registration)
- **64 Service Records** (2 per vehicle)
- **16 Invoices** (1 per service record)
- **16 Service Reminders** (1 per vehicle)
- **8 Cities** (Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, etc.)

## 🛠️ Development & Testing

### Seed Database
```bash
python seed_data.py
```

### Run Development Server
```bash
python run.py
```

### Test Workflow (Fully Functional)
1. Login as admin (admin / admin123)
2. Create and approve service requests
3. Complete services and generate invoices
4. Test payment as customer or admin cash payment
5. View reports with vehicle analytics

## 📋 Features Checklist

- ✅ User authentication (register, login, logout)
- ✅ Vehicle management (register, view, edit)
- ✅ Service booking system
- ✅ Admin service management
- ✅ Service records and history
- ✅ Invoice generation and payment tracking
- ✅ Dual payment system (customer online + admin cash)
- ✅ Document management with expiry tracking
- ✅ Service reminders (date and mileage based)
- ✅ Admin dashboard with analytics
- ✅ Reports with charts
- ✅ Maintenance Risk Level analysis
- ✅ Responsive design
- ✅ Database seeding with realistic data
- ✅ Professional UI with gradient theme
- ✅ Security features (auth, validation, sanitization)

## 📄 License

This project is developed for educational and demonstration purposes.

## 🤝 Support & Issues

For issues or questions, please check the application logs or contact the development team.

---

**Ready to Use**: The system is fully functional and ready for deployment. All features are tested and working.

**Server**: `http://localhost:5000`

**Admin Panel**: `http://localhost:5000/admin`
#   V e h i c l e C a r e  
 