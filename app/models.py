from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_barista = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship("Order", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_barista": self.is_barista,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat(),
        }

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username


# Many-to-many relationship between Coffee and CoffeeBeans
coffee_beans_association = db.Table(
    "coffee_beans_association",
    db.Column("coffee_id", db.Integer, db.ForeignKey("coffee.id")),
    db.Column("bean_id", db.Integer, db.ForeignKey("coffee_beans.id")),
)


class CoffeeBeans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False, default="beans_default.jpg")
    is_favorite = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Coffee bean specific details
    origin = db.Column(db.String(100), nullable=True)
    bean_type = db.Column(
        db.String(100), nullable=True
    )  # Arabica, Robusta, Blend, etc.
    roast_level = db.Column(db.String(50), nullable=True)  # Light, Medium, Dark, etc.
    processing_method = db.Column(
        db.String(100), nullable=True
    )  # Washed, Natural, Honey, etc.
    flavor_notes = db.Column(
        db.Text, nullable=True
    )  # Detailed flavor profile description
    acidity = db.Column(db.String(50), nullable=True)  # Low, Medium, High
    body = db.Column(db.String(50), nullable=True)  # Light, Medium, Full
    sweetness = db.Column(db.String(50), nullable=True)  # Low, Medium, High
    recommended_brew = db.Column(
        db.String(255), nullable=True
    )  # Recommended brewing methods
    harvest_date = db.Column(
        db.String(50), nullable=True
    )  # When the beans were harvested

    # Coffees that use this bean
    coffees = db.relationship(
        "Coffee", secondary=coffee_beans_association, back_populates="beans"
    )

    def __repr__(self):
        return f"<CoffeeBeans {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "is_favorite": self.is_favorite,
            "price": self.price,
            "origin": self.origin,
            "bean_type": self.bean_type,
            "roast_level": self.roast_level,
            "processing_method": self.processing_method,
            "flavor_notes": self.flavor_notes,
            "acidity": self.acidity,
            "body": self.body,
            "sweetness": self.sweetness,
            "recommended_brew": self.recommended_brew,
            "harvest_date": self.harvest_date,
        }


class Coffee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False, default="coffee_default.jpg")
    category = db.Column(db.String(50), nullable=False, default="coffee")
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flavors = db.Column(
        db.String(255), nullable=True
    )  # Stored as comma-separated string

    # Relationship with beans - a coffee can be made with multiple bean types
    beans = db.relationship(
        "CoffeeBeans", secondary=coffee_beans_association, back_populates="coffees"
    )

    # Default bean recommendation for this coffee
    default_bean_id = db.Column(
        db.Integer, db.ForeignKey("coffee_beans.id"), nullable=True
    )
    default_bean = db.relationship("CoffeeBeans", foreign_keys=[default_bean_id])

    def __repr__(self):
        return f"<Coffee {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "category": self.category,
            "is_favorite": self.is_favorite,
            "flavors": self.flavors.split(",") if self.flavors else [],
            "beans": [bean.to_dict() for bean in self.beans] if self.beans else [],
            "default_bean_id": self.default_bean_id,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string of items
    total = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, preparing, ready, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Order {self.order_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "user_name": self.user.full_name,
            "items": json.loads(self.items),
            "total": self.total,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class FavoriteCoffee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    coffee_id = db.Column(db.Integer, db.ForeignKey("coffee.id"), nullable=False)
    options = db.Column(db.Text, nullable=True)  # JSON string of preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="favorite_coffees")
    coffee = db.relationship("Coffee", backref="favorited_by")

    def __repr__(self):
        return f"<FavoriteCoffee {self.user.username} - {self.coffee.name}>"
