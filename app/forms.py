from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TimeField, TextAreaField, IntegerField, DecimalField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from flask_wtf.file import FileAllowed
from app.models import User, Vehicle

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = SelectField('Remember Me', choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data, is_deleted=False).first()
        if user:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data, is_deleted=False).first()
        if user:
            raise ValidationError('Please use a different email address.')

class VehicleForm(FlaskForm):
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(max=20)])
    brand = StringField('Brand', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    manufacturing_year = IntegerField('Manufacturing Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    current_odometer = IntegerField('Current Odometer Reading (km)', validators=[DataRequired(), NumberRange(min=0)], default=0)
    image = FileField('Vehicle Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'bmp', 'svg', 'tiff', 'ico'], 'Images only!')])
    submit = SubmitField('Submit')

class ServiceRequestForm(FlaskForm):
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    service_type = SelectField('Service Type', choices=[
        ('Regular Service', 'Regular Service'),
        ('Repair', 'Repair'),
        ('Custom', 'Custom Service')
    ], validators=[DataRequired()])
    custom_service_description = TextAreaField('Service Description (for Custom)', validators=[Optional(), Length(max=500)])
    preferred_date = DateField('Preferred Date', validators=[DataRequired()], format='%Y-%m-%d')
    preferred_time = TimeField('Preferred Time', validators=[Optional()], format='%H:%M')
    submit = SubmitField('Request Service')

class ServiceRecordForm(FlaskForm):
    service_type = StringField('Service Type', validators=[DataRequired(), Length(max=100)])
    parts_replaced = TextAreaField('Parts Replaced', validators=[Optional()])
    labor_charge = DecimalField('Labor Charge', validators=[DataRequired(), NumberRange(min=0)], places=2)
    additional_cost = DecimalField('Additional Cost', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    service_notes = TextAreaField('Service Notes', validators=[Optional()])
    odometer_reading = IntegerField('Odometer Reading', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Complete Service')

class ServiceStatusUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Status')

class DocumentForm(FlaskForm):
    document_type = SelectField('Document Type', choices=[
        ('Insurance', 'Insurance Certificate'),
        ('RC', 'RC Book'),
        ('Pollution', 'Pollution Certificate'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    file = FileField('Document File', validators=[DataRequired(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'bmp', 'svg', 'tiff', 'ico', 'doc', 'docx'], 'Documents only!')])
    expiry_date = DateField('Expiry Date', validators=[Optional()], format='%Y-%m-%d')
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Upload Document')

class PaymentForm(FlaskForm):
    invoice_id = HiddenField()
    payment_method = SelectField('Payment Method', choices=[
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment (UPI/Net Banking)')
    ], validators=[DataRequired()])
    submit = SubmitField('Process Payment')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

