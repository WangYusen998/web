from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin found: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Is Admin: {admin.is_admin}")
        print(f"Is Active: {admin.is_active}")
        print(f"Created At: {admin.created_at}")
        print(f"Is Administrator Check: {admin.is_administrator()}")
    else:
        print("Admin user not found!")
