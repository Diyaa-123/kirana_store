from flask import Blueprint, session, jsonify, request
from src.database.product_catelog import category
import secrets

api_bp = Blueprint('api_bp', __name__, static_folder='static', template_folder='templates')

# Discount codes configuration
DISCOUNT_CODES = {
    'SAVE10': 10,
    'SAVE20': 20,
    'FIRST50': 50
}

DELIVERY_FEE = 40

@api_bp.route('/api/cart', methods=['GET'])
def get_cart():
    """Get current cart from session"""
    cart = session.get('cart', [])
    return jsonify({
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    })

@api_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.json
    
    if not all(k in data for k in ['name', 'price', 'weight', 'image_url']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    cart = session.get('cart', [])
    
    # Check if item already exists
    existing_item = next((item for item in cart if item['name'] == data['name']), None)
    
    if existing_item:
        existing_item['quantity'] = existing_item.get('quantity', 1) + 1
    else:
        cart.append({
            'name': data['name'],
            'price': data['price'],
            'weight': data['weight'],
            'image_url': data['image_url'],
            'quantity': 1
        })
    
    session['cart'] = cart
    session.permanent = True
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    })

@api_bp.route('/api/cart/update', methods=['POST'])
def update_cart_item():
    """Update item quantity in cart"""
    data = request.json
    
    if 'name' not in data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Missing name or quantity'}), 400
    
    cart = session.get('cart', [])
    item = next((item for item in cart if item['name'] == data['name']), None)
    
    if not item:
        return jsonify({'success': False, 'error': 'Item not found in cart'}), 404
    
    if data['quantity'] <= 0:
        cart.remove(item)
    else:
        item['quantity'] = data['quantity']
    
    session['cart'] = cart
    session.permanent = True
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    })

@api_bp.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    data = request.json
    
    if 'name' not in data:
        return jsonify({'success': False, 'error': 'Missing item name'}), 400
    
    cart = session.get('cart', [])
    cart = [item for item in cart if item['name'] != data['name']]
    
    session['cart'] = cart
    session.permanent = True
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    })

@api_bp.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """Clear entire cart"""
    session['cart'] = []
    session.permanent = True
    
    return jsonify({
        'success': True,
        'cart': [],
        'total_items': 0
    })

@api_bp.route('/api/discount/validate', methods=['POST'])
def validate_discount():
    """Validate discount code"""
    data = request.json
    
    if 'code' not in data:
        return jsonify({'success': False, 'error': 'Missing discount code'}), 400
    
    code = data['code'].upper()
    
    if code in DISCOUNT_CODES:
        return jsonify({
            'success': True,
            'valid': True,
            'discount_percent': DISCOUNT_CODES[code],
            'message': f'{DISCOUNT_CODES[code]}% discount applied!'
        })
    else:
        return jsonify({
            'success': True,
            'valid': False,
            'discount_percent': 0,
            'message': 'Invalid discount code'
        })

@api_bp.route('/api/cart/calculate', methods=['POST'])
def calculate_cart_total():
    """Calculate cart totals with discount and delivery"""
    data = request.json
    cart = data.get('cart', [])
    discount_percent = data.get('discount_percent', 0)
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount_amount = round(subtotal * discount_percent / 100)
    total = subtotal - discount_amount + DELIVERY_FEE
    
    return jsonify({
        'success': True,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'delivery_fee': DELIVERY_FEE,
        'total': total
    })

@api_bp.route('/api/checkout', methods=['POST'])
def checkout():
    """Process checkout and create order"""
    data = request.json
    
    required_fields = ['cart', 'payment_method']
    if not all(k in data for k in required_fields):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    cart = data['cart']
    payment_method = data['payment_method']
    discount_percent = data.get('discount_percent', 0)
    
    if not cart:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount_amount = round(subtotal * discount_percent / 100)
    total = subtotal - discount_amount + DELIVERY_FEE
    
    # Create order object (in a real app, this would be saved to database)
    order = {
        'order_id': secrets.token_hex(8).upper(),
        'items': cart,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'delivery_fee': DELIVERY_FEE,
        'total': total,
        'payment_method': payment_method,
        'status': 'pending'
    }
    
    # Clear cart after successful order
    session['cart'] = []
    session.permanent = True
    
    # In a real application, you would:
    # 1. Save order to database
    # 2. Send WhatsApp notification
    # 3. Process payment
    # 4. Send confirmation email/SMS
    
    return jsonify({
        'success': True,
        'message': 'Order placed successfully!',
        'order': order
    })

@api_bp.route('/api/products', methods=['GET'])
def get_all_products():
    """Get all products as JSON"""
    all_products = []
    for cat_name, products in category.items():
        for product in products:
            all_products.append({
                **product,
                'category': cat_name
            })
    
    return jsonify({
        'success': True,
        'products': all_products,
        'total': len(all_products)
    })

@api_bp.route('/api/products/<cat_name>', methods=['GET'])
def get_products_by_category(cat_name):
    """Get products by category as JSON"""
    if cat_name == 'all':
        return get_all_products()
    
    if cat_name in category:
        return jsonify({
            'success': True,
            'category': cat_name,
            'products': category[cat_name],
            'total': len(category[cat_name])
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Category not found'
        }), 404