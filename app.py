from fastapi import FastAPI, Request, Response, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional, Dict
import secrets
from pathlib import Path

# Import database
from src.database.product_catelog import category

# Create FastAPI app
app = FastAPI(title="Kirana Store API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="kirana_session",
    max_age=7 * 24 * 60 * 60  # 7 days in seconds
)

# Discount codes configuration
DISCOUNT_CODES = {
    'SAVE10': 10,
    'SAVE20': 20,
    'FIRST50': 50
}

DELIVERY_FEE = 40

# Pydantic models
class CartItem(BaseModel):
    name: str
    price: float
    weight: str
    image_url: str
    quantity: Optional[int] = 1

class CartUpdate(BaseModel):
    name: str
    quantity: int

class CartRemove(BaseModel):
    name: str

# Helper functions
def get_cart(request: Request) -> List[dict]:
    return request.session.get('cart', [])

def save_cart(request: Request, cart: List[dict]):
    request.session['cart'] = cart

# Page Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage route"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/category/{name}", response_class=HTMLResponse)
async def category_details(request: Request, name: str):
    """Get products by category"""
    if name == 'all':
        # Return all products from all categories
        all_products = []
        for cat_products in category.values():
            all_products.extend(cat_products)
        return templates.TemplateResponse("card.html", {"request": request, "category": all_products})
    
    if name in category:
        category_products = category[name]
        return templates.TemplateResponse("card.html", {"request": request, "category": category_products})
    else:
        return templates.TemplateResponse("card.html", {"request": request, "category": []})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """Profile route"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/order_place", response_class=HTMLResponse)
async def order_place(request: Request):
    """Order place route"""
    return templates.TemplateResponse("order_place.html", {"request": request})

@app.get("/order_status", response_class=HTMLResponse)
async def order_status(request: Request):
    """Order status route"""
    return templates.TemplateResponse("order_status.html", {"request": request})

@app.get("/placed_orders", response_class=HTMLResponse)
async def placed_orders(request: Request):
    """Placed orders route"""
    return templates.TemplateResponse("placed_orders.html", {"request": request})

@app.get("/deals", response_class=HTMLResponse)
async def deals(request: Request):
    """Deals route"""
    return templates.TemplateResponse("deals.html", {"request": request})

@app.get("/new_arrivals", response_class=HTMLResponse)
async def new_arrivals(request: Request):
    """New Arrivals route"""
    return templates.TemplateResponse("new_arrivals.html", {"request": request})

# API Routes
@app.get("/api/cart")
async def get_cart_api(request: Request):
    """Get current cart from session"""
    cart = get_cart(request)
    return {
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    }

@app.post("/api/cart/add")
async def add_to_cart(request: Request, item: CartItem):
    """Add item to cart"""
    cart = get_cart(request)
    
    # Check if item already exists
    existing_item = next((i for i in cart if i['name'] == item.name), None)
    
    if existing_item:
        existing_item['quantity'] = existing_item.get('quantity', 1) + 1
    else:
        cart.append(item.dict())
    
    save_cart(request, cart)
    
    return {
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    }

@app.post("/api/cart/update")
async def update_cart_item(request: Request, update: CartUpdate):
    """Update item quantity in cart"""
    cart = get_cart(request)
    item = next((item for item in cart if item['name'] == update.name), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    if update.quantity <= 0:
        cart.remove(item)
    else:
        item['quantity'] = update.quantity
    
    save_cart(request, cart)
    
    return {
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    }

@app.post("/api/cart/remove")
async def remove_from_cart(request: Request, remove: CartRemove):
    """Remove item from cart"""
    cart = get_cart(request)
    cart = [item for item in cart if item['name'] != remove.name]
    
    save_cart(request, cart)
    
    return {
        'success': True,
        'cart': cart,
        'total_items': sum(item['quantity'] for item in cart)
    }

@app.post("/api/cart/apply-discount")
async def apply_discount(request: Request, code: str):
    """Apply discount code to cart"""
    if code not in DISCOUNT_CODES:
        raise HTTPException(status_code=400, detail="Invalid discount code")
    
    cart = get_cart(request)
    discount = DISCOUNT_CODES[code]
    
    return {
        'success': True,
        'discount': discount,
        'cart': cart
    }

@app.get("/api/cart/delivery-fee")
async def get_delivery_fee():
    """Get delivery fee"""
    return {
        'success': True,
        'delivery_fee': DELIVERY_FEE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
