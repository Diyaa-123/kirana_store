from flask import Blueprint, render_template
from src.database.product_catelog import category

page_bp = Blueprint('page_bp', __name__, static_folder='static', template_folder='templates')

@page_bp.route('/')
def home():
    """Homepage route"""
    return render_template('index.html')

@page_bp.route('/category/<name>')
def category_details(name):
    """Get products by category - returns HTML for dynamic loading"""
    if name == 'all':
        # Return all products from all categories
        all_products = []
        for cat_products in category.values():
            all_products.extend(cat_products)
        return render_template('card.html', category=all_products)
    
    if name in category:
        category_name = category[name]
        return render_template('card.html', category=category_name)
    else:
        return render_template('card.html', category=[])
    
@page_bp.route('/profile')
def profile():
    """Profile route"""
    return render_template('profile.html')

@page_bp.route('/order_place')
def order_place():
    """order_place route"""
    return render_template('order_place.html')


@page_bp.route('/order_status')
def order_status():
    """order_status route"""
    return render_template('order_status.html')

@page_bp.route('/placed_orders')
def placed_orders():
    """placed_orders route"""
    return render_template('placed_orders.html')

@page_bp.route('/deals')
def deals():
    """deals route"""
    return render_template('deals.html')

@page_bp.route('/new_arrivals')
def new_arrivals():
    """New Arrivalsroute"""
    return render_template('new_arrivals.html')