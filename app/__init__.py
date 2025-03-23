from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.models import db
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(id):
        from app.models import User

        return User.query.get(int(id))

    # Register blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    from app.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.admin import admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Create database tables (in development)
    with app.app_context():
        # Create uploads directory if it doesn't exist
        if not os.path.exists(os.path.join(app.static_folder, "uploads")):
            os.makedirs(os.path.join(app.static_folder, "uploads"))

        db.create_all()

        # Add demo data if no data exists
        from app.models import User, Coffee

        if not User.query.first():
            create_demo_data(db)

    return app


def create_demo_data(db):
    # Create a sample admin user
    from app.models import User, Coffee

    admin = User(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        is_admin=True,
        is_barista=True,
    )
    admin.set_password("adminpass")

    # Create a sample barista
    barista = User(
        username="barista",
        email="barista@example.com",
        first_name="Coffee",
        last_name="Maker",
        is_admin=False,
        is_barista=True,
    )
    barista.set_password("baristapass")

    # Create sample users
    user1 = User(
        username="mom", email="mom@example.com", first_name="Mom", last_name="Family"
    )
    user1.set_password("password")

    user2 = User(
        username="dad", email="dad@example.com", first_name="Dad", last_name="Family"
    )
    user2.set_password("password")

    user3 = User(
        username="sister",
        email="sister@example.com",
        first_name="Sister",
        last_name="Family",
    )
    user3.set_password("password")

    # Add sample coffee items
    coffee1 = Coffee(
        name="Espresso",
        description="Strong, concentrated coffee served in a small cup. Bold and intense flavor.",
        price=2.50,
        image="coffee1.jpg",
        category="espresso",
        is_favorite=True,
        flavors="Strong,Intense,Bold",
    )

    coffee2 = Coffee(
        name="Cappuccino",
        description="Equal parts espresso, steamed milk, and milk foam. Perfect balance of flavor.",
        price=3.75,
        image="coffee2.jpg",
        category="espresso",
        is_favorite=False,
        flavors="Creamy,Balanced",
    )

    coffee3 = Coffee(
        name="Latte",
        description="Espresso with steamed milk and a small layer of foam. Smooth and mild.",
        price=3.50,
        image="coffee3.jpg",
        category="espresso",
        is_favorite=True,
        flavors="Smooth,Creamy,Mild",
    )

    coffee4 = Coffee(
        name="Cold Brew",
        description="Coffee brewed with cold water for 12-24 hours. Smooth with low acidity.",
        price=4.00,
        image="coffee1.jpg",
        category="cold",
        is_favorite=False,
        flavors="Smooth,Rich,Low Acidity",
    )

    coffee5 = Coffee(
        name="Americano",
        description="Espresso diluted with hot water. Similar strength to drip coffee but different flavor.",
        price=2.75,
        image="coffee2.jpg",
        category="espresso",
        is_favorite=False,
        flavors="Mild,Balanced",
    )

    coffee6 = Coffee(
        name="Mocha",
        description="Espresso with chocolate syrup and steamed milk. Rich and indulgent.",
        price=4.25,
        image="coffee3.jpg",
        category="specialty",
        is_favorite=True,
        flavors="Chocolatey,Rich,Sweet",
    )

    # Add all to database
    db.session.add_all(
        [
            admin,
            barista,
            user1,
            user2,
            user3,
            coffee1,
            coffee2,
            coffee3,
            coffee4,
            coffee5,
            coffee6,
        ]
    )
    db.session.commit()
