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
    featured_beans = CoffeeBeans.query.filter_by(is_favorite=True).all()
    return render_template(
        "index.html", featured_coffees=featured_coffees, featured_beans=featured_beans
    )


@main_bp.route("/menu")
def menu():
    # Filter by category if specified
    category = request.args.get("category", "all")
    bean_id = request.args.get("bean_id")

    # Base query
    query = Coffee.query

    if category != "all":
        query = query.filter_by(category=category)

    # If a bean is selected, filter coffees that use this bean
    if bean_id:
        bean = CoffeeBeans.query.get_or_404(int(bean_id))
        query = query.join(Coffee.beans).filter(CoffeeBeans.id == bean.id)

    # Get coffees
    coffees = query.all()

    # Get unique categories
    categories = db.session.query(Coffee.category).distinct().all()
    categories = [c[0] for c in categories]  # Unpack tuples

    # If a bean was selected, pass it to the template
    selected_bean = CoffeeBeans.query.get(bean_id) if bean_id else None

    return render_template(
        "menu.html",
        coffees=coffees,
        categories=categories,
        selected_category=category,
        selected_bean=selected_bean,
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


@main_bp.route("/api/coffeebeans/<int:bean_id>")
def get_bean_api(bean_id):
    bean = CoffeeBeans.query.get_or_404(bean_id)
    return jsonify(bean.to_dict())


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
    # Filter by origin or roast level if specified
    origin = request.args.get("origin", "all")
    roast = request.args.get("roast", "all")

    # Base query
    query = CoffeeBeans.query

    if origin != "all":
        query = query.filter_by(origin=origin)

    if roast != "all":
        query = query.filter_by(roast_level=roast)

    beans = query.all()

    # Get unique origins
    origins = (
        db.session.query(CoffeeBeans.origin)
        .filter(CoffeeBeans.origin != None)
        .distinct()
        .all()
    )
    origins = [o[0] for o in origins if o[0]]  # Unpack tuples and filter None values

    # Get unique roast levels
    roast_levels = (
        db.session.query(CoffeeBeans.roast_level)
        .filter(CoffeeBeans.roast_level != None)
        .distinct()
        .all()
    )
    roast_levels = [
        r[0] for r in roast_levels if r[0]
    ]  # Unpack tuples and filter None values

    return render_template(
        "beans.html",
        beans=beans,
        origins=origins,
        roast_levels=roast_levels,
        selected_origin=origin,
        selected_roast=roast,
    )


@main_bp.route("/bean/<int:bean_id>")
def bean_detail(bean_id):
    """Show details for a specific bean and its recommended brewing methods"""
    bean = CoffeeBeans.query.get_or_404(bean_id)

    # Parse recommended brewing methods
    brewing_methods = []
    if bean.recommended_brew:
        brewing_methods = [
            method.strip() for method in bean.recommended_brew.split(",")
        ]

    # Find coffees that use this bean
    compatible_coffees = (
        Coffee.query.join(Coffee.beans).filter(CoffeeBeans.id == bean.id).all()
    )

    # Find similar beans (same origin or roast level)
    similar_beans = []
    if bean.origin:
        similar_beans = (
            CoffeeBeans.query.filter(
                CoffeeBeans.id != bean.id, CoffeeBeans.origin == bean.origin
            )
            .limit(3)
            .all()
        )

    # If we don't have enough similar beans by origin, add some with same roast level
    if len(similar_beans) < 3 and bean.roast_level:
        more_beans = (
            CoffeeBeans.query.filter(
                CoffeeBeans.id != bean.id,
                CoffeeBeans.roast_level == bean.roast_level,
                ~CoffeeBeans.id.in_([b.id for b in similar_beans]),
            )
            .limit(3 - len(similar_beans))
            .all()
        )
        similar_beans.extend(more_beans)

    return render_template(
        "bean_detail.html",
        bean=bean,
        brewing_methods=brewing_methods,
        compatible_coffees=compatible_coffees,
        similar_beans=similar_beans,
    )


@main_bp.route("/brew-method/<method>")
def brew_method(method):
    """Show coffees available for a specific brewing method"""
    # Find beans that recommend this brewing method
    beans = CoffeeBeans.query.filter(
        CoffeeBeans.recommended_brew.like(f"%{method}%")
    ).all()

    # Find coffees that can be made with these beans
    coffees = []
    if beans:
        for bean in beans:
            for coffee in bean.coffees:
                if coffee not in coffees:
                    coffees.append(coffee)

    return render_template(
        "brew_method.html", method=method, coffees=coffees, beans=beans
    )
