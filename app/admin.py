from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
)
from flask_login import login_required, current_user
from app.models import User, Coffee, Order, db
from app.forms import CoffeeForm, UserEditForm
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import uuid

admin_bp = Blueprint("admin", __name__)


def admin_required(func):
    """Decorator to require admin privileges"""

    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin and not current_user.is_barista:
            abort(403)  # Forbidden
        return func(*args, **kwargs)

    decorated_view.__name__ = func.__name__
    return decorated_view


def admin_only(func):
    """Decorator to require admin privileges (not just barista)"""

    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)

    decorated_view.__name__ = func.__name__
    return decorated_view


@admin_bp.route("/")
@admin_required
def dashboard():
    # Get order statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status="pending").count()
    preparing_orders = Order.query.filter_by(status="preparing").count()
    ready_orders = Order.query.filter_by(status="ready").count()
    completed_orders = Order.query.filter_by(status="completed").count()

    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # Get top selling coffees (would need additional data tracking)
    top_coffees = Coffee.query.filter_by(is_favorite=True).all()

    return render_template(
        "admin/dashboard.html",
        title="Admin Dashboard",
        total_orders=total_orders,
        pending_orders=pending_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        completed_orders=completed_orders,
        recent_orders=recent_orders,
        top_coffees=top_coffees,
    )


@admin_bp.route("/orders")
@admin_required
def orders():
    # Filter by status if specified
    status_filter = request.args.get("status", "all")

    # Base query
    query = Order.query

    if status_filter != "all":
        query = query.filter_by(status=status_filter)

    # Get orders, newest first
    orders = query.order_by(Order.created_at.desc()).all()

    return render_template(
        "admin/orders.html",
        title="Manage Orders",
        orders=orders,
        status_filter=status_filter,
    )


@admin_bp.route("/update-order-status/<order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    new_status = request.form.get("status")

    if new_status not in ["pending", "preparing", "ready", "completed", "cancelled"]:
        flash("Invalid status", "danger")
        return redirect(url_for("admin.orders"))

    order.status = new_status

    if new_status == "completed":
        order.completed_at = datetime.utcnow()

    db.session.commit()

    flash(f"Order status updated to {new_status}", "success")
    return redirect(url_for("admin.orders", status=request.args.get("status", "all")))


@admin_bp.route("/menu")
@admin_required
def menu():
    coffees = Coffee.query.all()
    return render_template("admin/menu.html", title="Manage Menu", coffees=coffees)


@admin_bp.route("/coffee/new", methods=["GET", "POST"])
@admin_only
def new_coffee():
    form = CoffeeForm()

    if form.validate_on_submit():
        # Handle image upload
        image_file = "coffee_default.jpg"

        if form.image.data:
            f = form.image.data
            filename = secure_filename(f.filename)
            # Add random string to filename to prevent duplicates
            random_hex = uuid.uuid4().hex
            _, file_extension = os.path.splitext(filename)
            image_file = random_hex + file_extension

            # Save the file
            file_path = os.path.join(current_app.static_folder, "uploads", image_file)
            f.save(file_path)

            # Image path for database is relative to static folder
            image_file = f"uploads/{image_file}"

        # Create new coffee item with enhanced details
        coffee = Coffee(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=image_file,
            category=form.category.data,
            is_favorite=form.is_favorite.data,
            flavors=form.flavors.data,
            # Coffee enthusiast details
            bean_origin=form.bean_origin.data,
            bean_type=form.bean_type.data,
            roast_level=form.roast_level.data,
            processing_method=form.processing_method.data,
            flavor_notes=form.flavor_notes.data,
            acidity=form.acidity.data,
            body=form.body.data,
            sweetness=form.sweetness.data,
            recommended_brew=form.recommended_brew.data,
        )

        db.session.add(coffee)
        db.session.commit()

        flash("New coffee added successfully!", "success")
        return redirect(url_for("admin.menu"))

    return render_template("admin/coffee_form.html", title="Add New Coffee", form=form)


@admin_bp.route("/coffee/edit/<int:id>", methods=["GET", "POST"])
@admin_only
def edit_coffee(id):
    coffee = Coffee.query.get_or_404(id)
    form = CoffeeForm()

    if form.validate_on_submit():
        # Update coffee details
        coffee.name = form.name.data
        coffee.description = form.description.data
        coffee.price = form.price.data
        coffee.category = form.category.data
        coffee.is_favorite = form.is_favorite.data
        coffee.flavors = form.flavors.data

        # Update coffee enthusiast details
        coffee.bean_origin = form.bean_origin.data
        coffee.bean_type = form.bean_type.data
        coffee.roast_level = form.roast_level.data
        coffee.processing_method = form.processing_method.data
        coffee.flavor_notes = form.flavor_notes.data
        coffee.acidity = form.acidity.data
        coffee.body = form.body.data
        coffee.sweetness = form.sweetness.data
        coffee.recommended_brew = form.recommended_brew.data

        # Handle image upload
        if form.image.data:
            f = form.image.data
            filename = secure_filename(f.filename)
            # Add random string to filename to prevent duplicates
            random_hex = uuid.uuid4().hex
            _, file_extension = os.path.splitext(filename)
            image_file = random_hex + file_extension

            # Save the file
            file_path = os.path.join(current_app.static_folder, "uploads", image_file)
            f.save(file_path)

            # Image path for database is relative to static folder
            coffee.image = f"uploads/{image_file}"

        db.session.commit()

        flash("Coffee updated successfully!", "success")
        return redirect(url_for("admin.menu"))

    # Pre-populate form with existing data
    if request.method == "GET":
        form.name.data = coffee.name
        form.description.data = coffee.description
        form.price.data = coffee.price
        form.category.data = coffee.category
        form.is_favorite.data = coffee.is_favorite
        form.flavors.data = coffee.flavors

        # Pre-populate coffee enthusiast details
        form.bean_origin.data = coffee.bean_origin
        form.bean_type.data = coffee.bean_type
        form.roast_level.data = coffee.roast_level
        form.processing_method.data = coffee.processing_method
        form.flavor_notes.data = coffee.flavor_notes
        form.acidity.data = coffee.acidity
        form.body.data = coffee.body
        form.sweetness.data = coffee.sweetness
        form.recommended_brew.data = coffee.recommended_brew

    return render_template(
        "admin/coffee_form.html", title="Edit Coffee", form=form, coffee=coffee
    )


@admin_bp.route("/coffee/delete/<int:id>", methods=["POST"])
@admin_only
def delete_coffee(id):
    coffee = Coffee.query.get_or_404(id)

    db.session.delete(coffee)
    db.session.commit()

    flash("Coffee deleted successfully!", "success")
    return redirect(url_for("admin.menu"))


@admin_bp.route("/users")
@admin_only
def users():
    users = User.query.all()
    return render_template("admin/users.html", title="Manage Users", users=users)


@admin_bp.route("/user/edit/<int:id>", methods=["GET", "POST"])
@admin_only
def edit_user(id):
    user = User.query.get_or_404(id)

    # Admin cannot edit themselves this way (to prevent losing admin access)
    if user.id == current_user.id:
        flash(
            "You cannot edit your own account this way. Use the profile page instead.",
            "warning",
        )
        return redirect(url_for("admin.users"))

    form = UserEditForm(original_username=user.username, original_email=user.email)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_barista = form.is_barista.data
        user.is_admin = form.is_admin.data

        db.session.commit()

        flash("User updated successfully!", "success")
        return redirect(url_for("admin.users"))

    # Pre-populate form with existing data
    if request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.is_barista.data = user.is_barista
        form.is_admin.data = user.is_admin

    return render_template(
        "admin/user_form.html", title="Edit User", form=form, user=user
    )


@admin_bp.route("/user/delete/<int:id>", methods=["POST"])
@admin_only
def delete_user(id):
    user = User.query.get_or_404(id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash("You cannot delete your own account!", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/user/toggle-barista/<int:id>", methods=["POST"])
@admin_only
def toggle_barista(id):
    user = User.query.get_or_404(id)

    # Prevent admin from removing their own privileges
    if user.id == current_user.id:
        flash("You cannot change your own permissions!", "danger")
        return redirect(url_for("admin.users"))

    user.is_barista = not user.is_barista
    db.session.commit()

    status = "granted" if user.is_barista else "revoked"
    flash(f"Barista access {status} for {user.username}", "success")

    return redirect(url_for("admin.users"))


@admin_bp.route("/user/toggle-admin/<int:id>", methods=["POST"])
@admin_only
def toggle_admin(id):
    user = User.query.get_or_404(id)

    # Prevent admin from removing their own privileges
    if user.id == current_user.id:
        flash("You cannot change your own permissions!", "danger")
        return redirect(url_for("admin.users"))

    user.is_admin = not user.is_admin

    # If making someone admin, they should also have barista privileges
    if user.is_admin:
        user.is_barista = True

    db.session.commit()

    status = "granted" if user.is_admin else "revoked"
    flash(f"Admin access {status} for {user.username}", "success")

    return redirect(url_for("admin.users"))
