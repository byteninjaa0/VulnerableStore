import os
import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "insecure_secret_key")  # Intentionally weak fallback

# SQLite Database configuration - intentionally using raw SQL for vulnerability demonstrations
DATABASE = 'vulnerable_ecommerce.db'

# Helper functions for database operations
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def update_db(query, args=()):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------- Routes --------------------

@app.route('/')
def index():
    # Fetch products for homepage
    products = query_db('SELECT * FROM products')
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vulnerable to SQL Injection - intentionally insecure
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = query_db(query, one=True)
        
        if user:
            # Store user info in session - intentionally storing too much information
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Storing password in plaintext - intentionally insecure
        email = request.form['email']
        
        # Check if username already exists
        existing_user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if existing_user:
            return render_template('register.html', error='Username already exists')
        
        # Insert new user - intentionally not using parameter binding to allow SQL injection
        query = f"INSERT INTO users (username, password, email, is_admin) VALUES ('{username}', '{password}', '{email}', 0)"
        update_db(query)
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        flash('Please log in to view your profile')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    
    # Get user's orders
    orders = query_db('SELECT * FROM orders WHERE user_id = ?', [user_id])
    
    return render_template('profile.html', user=user, orders=orders)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        flash('Please log in to update your profile')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    email = request.form['email']
    address = request.form['address']
    
    # Command injection vulnerability - intentionally insecure
    profile_picture = request.form.get('profile_picture', '')
    if profile_picture:
        # The vulnerability: directly using user input in a system command
        os.system(f"echo Processing profile picture: {profile_picture}")
    
    # Update user profile - SQL injection vulnerability
    query = f"UPDATE users SET email = '{email}', address = '{address}' WHERE id = {user_id}"
    update_db(query)
    
    flash('Profile updated successfully')
    return redirect(url_for('profile'))

@app.route('/product/<int:product_id>')
def product(product_id):
    # IDOR vulnerability - no authorization check for private/restricted products
    product = query_db('SELECT * FROM products WHERE id = ?', [product_id], one=True)
    
    if not product:
        flash('Product not found')
        return redirect(url_for('index'))
    
    # Get product reviews - Vulnerable to Stored XSS
    reviews = query_db('SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = ?', [product_id])
    
    return render_template('product.html', product=product, reviews=reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    if not session.get('logged_in'):
        flash('Please log in to add a review')
        return redirect(url_for('login'))
    
    product_id = request.form['product_id']
    rating = request.form['rating']
    content = request.form['content']  # Not sanitized - intentional XSS vulnerability
    user_id = session['user_id']
    
    # Insert review - SQL injection vulnerability
    query = f"INSERT INTO reviews (product_id, user_id, rating, content) VALUES ({product_id}, {user_id}, {rating}, '{content}')"
    update_db(query)
    
    flash('Review added successfully')
    return redirect(url_for('product', product_id=product_id))

@app.route('/search')
def search():
    query_term = request.args.get('q', '')
    
    if not query_term:
        return render_template('search.html', products=[])
    
    # SQL Injection vulnerability - intentionally insecure
    search_query = f"SELECT * FROM products WHERE name LIKE '%{query_term}%' OR description LIKE '%{query_term}%'"
    products = query_db(search_query)
    
    # Reflected XSS vulnerability - intentionally insecure
    return render_template('search.html', products=products, query=query_term)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    product = query_db('SELECT * FROM products WHERE id = ?', [product_id], one=True)
    
    if product:
        cart_item = {
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        }
        
        # Check if product is already in cart
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += 1
                session.modified = True
                flash(f"Added another {product['name']} to your cart")
                return redirect(url_for('cart'))
        
        # Add new item to cart
        session['cart'].append(cart_item)
        session.modified = True
        flash(f"Added {product['name']} to your cart")
    
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
        flash('Item removed from cart')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('logged_in'):
        flash('Please log in to checkout')
        return redirect(url_for('login'))
    
    if not session.get('cart'):
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    user_id = session['user_id']
    cart = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    # Create order
    update_db('INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)', 
              [user_id, total, 'Pending'])
    
    # Get the order ID
    order_id = query_db('SELECT last_insert_rowid()', one=True)[0]
    
    # Add order items
    for item in cart:
        update_db('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                 [order_id, item['id'], item['quantity'], item['price']])
    
    # Clear the cart
    session.pop('cart', None)
    
    flash('Order placed successfully!')
    return redirect(url_for('profile'))

# Admin routes - with IDOR vulnerabilities
@app.route('/admin')
def admin():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    return render_template('admin.html')

@app.route('/admin/users')
def admin_users():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    users = query_db('SELECT * FROM users')
    return render_template('admin_users.html', users=users)

@app.route('/admin/orders')
def admin_orders():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    orders = query_db('''
        SELECT o.*, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.id
    ''')
    return render_template('admin_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
def view_order(order_id):
    # IDOR vulnerability - no check if the order belongs to the logged-in user
    
    order = query_db('SELECT * FROM orders WHERE id = ?', [order_id], one=True)
    
    if not order:
        flash('Order not found')
        return redirect(url_for('profile'))
    
    # Get order items
    items = query_db('''
        SELECT oi.*, p.name 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = ?
    ''', [order_id])
    
    return render_template('order.html', order=order, items=items)

@app.route('/user/<int:user_id>')
def view_user(user_id):
    # IDOR vulnerability - can view any user's profile
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    
    if not user:
        flash('User not found')
        return redirect(url_for('index'))
    
    return render_template('user.html', user=user)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
