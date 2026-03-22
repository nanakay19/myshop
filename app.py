from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'shopkey123'

def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                (id INTEGER PRIMARY KEY, name TEXT, price REAL, image TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, address TEXT, 
                items TEXT, total REAL, time TEXT)''')
    # Add sample products if empty
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO products VALUES (1, 'Product 1', 10.00, 'https://i.postimg.cc/Qty4K0QN/download_(1).jpg', 'Description 1')")
        c.execute("INSERT INTO products VALUES (2, 'Product 2', 20.00, 'https://i.postimg.cc/LXXQsrZW/download_(3).jpg', 'Description 2')")
        c.execute("INSERT INTO products VALUES (3, 'Product 3', 30.00, 'https://i.postimg.cc/V6VG0DqF/download.jpg', 'Description 3')")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('home.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    items = []
    total = 0
    for pid, qty in cart.items():
        c.execute('SELECT * FROM products WHERE id=?', (pid,))
        product = c.fetchone()
        if product:
            subtotal = product[2] * qty
            total += subtotal
            items.append((product, qty, subtotal))
    conn.close()
    return render_template('cart.html', items=items, total=total)

@app.route('/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        cart = session.get('cart', {})
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        items = []
        total = 0
        for pid, qty in cart.items():
            c.execute('SELECT * FROM products WHERE id=?', (pid,))
            product = c.fetchone()
            if product:
                subtotal = product[2] * qty
                total += subtotal
                items.append(f"{product[1]} x{qty}")
        c.execute('INSERT INTO orders (name, phone, address, items, total, time) VALUES (?,?,?,?,?,?)',
                  (name, phone, address, ', '.join(items), total, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        session['cart'] = {}
        return render_template('success.html', name=name)
    cart = session.get('cart', {})
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    total = 0
    for pid, qty in cart.items():
        c.execute('SELECT price FROM products WHERE id=?', (pid,))
        p = c.fetchone()
        if p:
            total += p[0] * qty
    conn.close()
    return render_template('checkout.html', total=total)
@app.route('/admin')
def admin():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = c.fetchall()
    c.execute('SELECT COUNT(*) FROM orders')
    total_orders = c.fetchone()[0]
    c.execute('SELECT SUM(total) FROM orders')
    total_revenue = c.fetchone()[0] or 0
    conn.close()
    return render_template('admin.
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
