import sqlite3
import os

# Delete existing database if it exists
if os.path.exists('vulnerable_ecommerce.db'):
    os.remove('vulnerable_ecommerce.db')

# Create a new database
conn = sqlite3.connect('vulnerable_ecommerce.db')
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT,
    is_admin INTEGER DEFAULT 0
)
''')

c.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    image_url TEXT
)
''')

c.execute('''
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    user_id INTEGER,
    rating INTEGER NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

c.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

c.execute('''
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')

# Insert demo data
# Admin user
c.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
          ('admin', 'admin123', 'admin@example.com', 1))

# Regular user
c.execute("INSERT INTO users (username, password, email, address, is_admin) VALUES (?, ?, ?, ?, ?)",
          ('user', 'password123', 'user@example.com', '123 Main St, Anytown', 0))

# Products
products = [
    ('Smartphone', 'Latest model with high-resolution camera', 699.99, 50, '/static/img/smartphone.jpg'),
    ('Laptop', 'Powerful laptop for work and gaming', 1299.99, 30, '/static/img/laptop.jpg'),
    ('Headphones', 'Noise-cancelling wireless headphones', 199.99, 100, '/static/img/headphones.jpg'),
    ('Smartwatch', 'Track your fitness and get notifications', 249.99, 45, '/static/img/smartwatch.jpg'),
    ('Tablet', '10-inch screen with long battery life', 399.99, 60, '/static/img/tablet.jpg'),
    ('Gaming Console', 'Next-gen gaming experience', 499.99, 25, '/static/img/console.jpg'),
    ('Camera', 'DSLR with 24MP sensor', 799.99, 20, '/static/img/camera.jpg'),
    ('Bluetooth Speaker', 'Portable speaker with great sound', 129.99, 80, '/static/img/speaker.jpg')
]

for product in products:
    c.execute("INSERT INTO products (name, description, price, stock, image_url) VALUES (?, ?, ?, ?, ?)", product)

# Add some reviews (one with XSS)
c.execute("INSERT INTO reviews (product_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
          (1, 2, 5, 'Great phone, I love it!'))

c.execute("INSERT INTO reviews (product_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
          (1, 2, 1, '<script>alert("XSS Attack!")</script>This product is terrible.'))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized with sample data!")
