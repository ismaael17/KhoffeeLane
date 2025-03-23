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
        from app.models import User, Coffee, CoffeeBeans

        if not User.query.first():
            create_demo_data(db)

    return app


def create_demo_data(db):
    # Create a sample admin user
    from app.models import User, Coffee, CoffeeBeans

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

    # Add sample coffee beans
    bean1 = CoffeeBeans(
        name="Ethiopian Yirgacheffe",
        description="A bright, fruity coffee with floral notes and a tea-like body.",
        price=14.99,
        image="bean1.jpg",
        is_favorite=True,
        origin="Ethiopia",
        bean_type="arabica",
        roast_level="light",
        processing_method="washed",
        flavor_notes="Citrus, bergamot, floral with a clean, bright finish",
        acidity="high",
        body="light",
        sweetness="medium_high",
        recommended_brew="Pour Over, Aeropress, Drip",
        harvest_date="March-June",
    )

    bean2 = CoffeeBeans(
        name="Colombian Supremo",
        description="A well-balanced coffee with caramel sweetness and nutty undertones.",
        price=12.99,
        image="bean2.jpg",
        is_favorite=False,
        origin="Colombia",
        bean_type="arabica",
        roast_level="medium",
        processing_method="washed",
        flavor_notes="Caramel, almond, light citrus acidity with a smooth finish",
        acidity="medium",
        body="medium",
        sweetness="medium",
        recommended_brew="French Press, Espresso, Drip",
        harvest_date="October-January",
    )

    bean3 = CoffeeBeans(
        name="Sumatra Mandheling",
        description="Earthy and full-bodied with low acidity and notes of dark chocolate.",
        price=13.99,
        image="bean3.jpg",
        is_favorite=True,
        origin="Indonesia",
        bean_type="arabica",
        roast_level="dark",
        processing_method="wet_hulled",
        flavor_notes="Earthy, herbal, dark chocolate, spice",
        acidity="low",
        body="full",
        sweetness="medium_low",
        recommended_brew="French Press, Espresso, Cold Brew",
        harvest_date="June-December",
    )

    bean4 = CoffeeBeans(
        name="Brazilian Santos",
        description="Smooth and mild with nutty flavors and a mild acidity.",
        price=11.99,
        image="bean2.jpg",
        is_favorite=False,
        origin="Brazil",
        bean_type="arabica",
        roast_level="medium",
        processing_method="natural",
        flavor_notes="Chocolate, nuts, mild fruit with a smooth finish",
        acidity="low",
        body="medium",
        sweetness="medium",
        recommended_brew="Espresso, Moka Pot, French Press",
        harvest_date="May-September",
    )

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

    # Set up relationships between coffees and beans
    coffee1.beans.append(bean1)
    coffee1.beans.append(bean3)
    coffee1.default_bean = bean3

    coffee2.beans.append(bean1)
    coffee2.beans.append(bean2)
    coffee2.default_bean = bean2

    coffee3.beans.append(bean2)
    coffee3.beans.append(bean4)
    coffee3.default_bean = bean2

    coffee4.beans.append(bean3)
    coffee4.beans.append(bean4)
    coffee4.default_bean = bean3

    coffee5.beans.append(bean1)
    coffee5.beans.append(bean2)
    coffee5.beans.append(bean4)
    coffee5.default_bean = bean2

    coffee6.beans.append(bean2)
    coffee6.beans.append(bean3)
    coffee6.default_bean = bean3

    # Add all to database
    db.session.add_all(
        [
            admin,
            barista,
            user1,
            user2,
            user3,
            bean1,
            bean2,
            bean3,
            bean4,
            coffee1,
            coffee2,
            coffee3,
            coffee4,
            coffee5,
            coffee6,
        ]
    )
    db.session.commit()
