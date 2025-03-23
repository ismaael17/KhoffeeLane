from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    flash,
    session,
    abort,
)
from flask_login import login_required, current_user
from app.models import Coffee, Order, User, db, CoffeeBeans
from datetime import datetime
import json
import uuid

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured_coffees = Coffee.query.filter_by(is_favorite=True).all()
    return render_template("index.html", featured_coffees=featured_coffees)


@main_bp.route("/menu")
def menu():
    # Filter by category if specified
    category = request.args.get("category", "all")

    # Base query
    query = Coffee.query

    if category != "all":
        query = query.filter_by(category=category)

    # Get coffees
    coffees = query.all()

    # Get unique categories
    categories = db.session.query(Coffee.category).distinct().all()
    categories = [c[0] for c in categories]  # Unpack tuples

    return render_template(
        "menu.html", coffees=coffees, categories=categories, selected_category=category
    )


@main_bp.route("/cart")
@login_required
def cart():
    return render_template("cart.html")


@main_bp.route("/order", methods=["GET", "POST"])
@login_required
def order():
    if request.method == "POST":
        # Get cart data from form
        cart_items = json.loads(request.form.get("cart_items"))

        if not cart_items:
            flash("Your cart is empty!", "warning")
            return redirect(url_for("main.cart"))

        # Generate order ID
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in cart_items)

        # Create new order
        new_order = Order(
            order_id=order_id,
            user_id=current_user.id,
            items=json.dumps(cart_items),
            total=total,
            status="pending",
            notes=request.form.get("notes", ""),
        )

        db.session.add(new_order)
        db.session.commit()

        flash("Your order has been placed successfully!", "success")
        return redirect(url_for("main.order_confirmation", order_id=order_id))

    return redirect(url_for("main.cart"))


@main_bp.route("/order-confirmation/<order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(
        order_id=order_id, user_id=current_user.id
    ).first_or_404()
    return render_template("order_confirmation.html", order=order)


@main_bp.route("/order-history")
@login_required
def order_history():
    # Get current user's orders, newest first
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("order_history.html", orders=orders)


# Changed endpoint name from get_coffee to get_coffee_api to avoid conflicts
@main_bp.route("/api/coffee/<int:coffee_id>")
def get_coffee_api(coffee_id):
    coffee = Coffee.query.get_or_404(coffee_id)
    return jsonify(coffee.to_dict())


@main_bp.route("/api/orders")
@login_required
def get_orders():
    if current_user.is_admin or current_user.is_barista:
        # Admins and baristas can see all orders
        orders = Order.query.all()
    else:
        # Regular users can only see their own orders
        orders = Order.query.filter_by(user_id=current_user.id).all()

    return jsonify([order.to_dict() for order in orders])


@main_bp.route("/api/reorder/<order_id>")
@login_required
def reorder(order_id):
    # Find the order
    order = Order.query.filter_by(
        order_id=order_id, user_id=current_user.id
    ).first_or_404()

    # Generate new order ID
    new_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Create new order with same items
    new_order = Order(
        order_id=new_order_id,
        user_id=current_user.id,
        items=order.items,
        total=order.total,
        status="pending",
        notes=f"Reorder of {order_id}",
    )

    db.session.add(new_order)
    db.session.commit()

    flash("Your order has been placed successfully!", "success")
    return redirect(url_for("main.order_confirmation", order_id=new_order_id))


@main_bp.route("/api/cancel-order/<order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    # Find the order
    order = Order.query.filter_by(
        order_id=order_id, user_id=current_user.id
    ).first_or_404()

    # Only pending orders can be cancelled by users
    if order.status != "pending":
        flash("Only pending orders can be cancelled!", "danger")
        return redirect(url_for("main.order_history"))

    # Update status
    order.status = "cancelled"
    db.session.commit()

    flash("Your order has been cancelled!", "success")
    return redirect(url_for("main.order_history"))


@main_bp.route("/beans")
def beans():
    """Display available coffee beans for selection"""
    beans = Coffee.query.filter(Coffee.bean_origin.isnot(None)).all()
    return render_template("beans.html", beans=beans)


@main_bp.route("/bean/")
def bean_detail(coffee_id):
    """Show details for a specific bean and its recommended brewing methods"""
    coffee = Coffee.query.get_or_404(coffee_id)

    # Parse recommended brewing methods
    brewing_methods = []
    if coffee.recommended_brew:
        brewing_methods = [
            method.strip() for method in coffee.recommended_brew.split(",")
        ]

    # Find other coffees that use the same brewing methods
    similar_coffees = []
    if brewing_methods:
        # Create a query to find coffees that have any of these brewing methods
        query = Coffee.query.filter(Coffee.id != coffee_id)
        for method in brewing_methods:
            query = query.filter(Coffee.recommended_brew.like(f"%{method}%"))
        similar_coffees = query.all()

    return render_template(
        "bean_detail.html",
        coffee=coffee,
        brewing_methods=brewing_methods,
        similar_coffees=similar_coffees,
    )


@main_bp.route("/brew-method/")
def brew_method(method):
    """Show coffees available for a specific brewing method"""
    # Find all coffees that can be prepared with this method
    coffees = Coffee.query.filter(Coffee.recommended_brew.like(f"%{method}%")).all()
    return render_template("brew_method.html", method=method, coffees=coffees)
