import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, CustomOrder, CartItem, Message
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key = 'divya_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/add-dummy')
def add_dummy():
    products = [
        Product(name='Art Frame', price=499, image_url='static/uploads/art.jpg'),
        Product(name='Blue Rakhis', price=99, image_url='static/uploads/Blue rakhis.jpg'),
        Product(name='Canvas Print', price=399, image_url='static/uploads/canvas.jpg'),
        Product(name='Cartoon Rakhi', price=89, image_url='static/uploads/cartoon rakhi.jpg'),
        Product(name='Cushion', price=299, image_url='static/uploads/cushion.jpg'),
        Product(name='Custom Mug', price=199, image_url='static/uploads/mug.jpg'),
        Product(name='Keychain', price=49, image_url='static/uploads/names keychain.jpg'),
        Product(name='Notebook', price=129, image_url='static/uploads/notebook.jpg'),
        Product(name='Rakhi', price=79, image_url='static/uploads/Rakhi.jpg'),
        Product(name='T-Shirt', price=349, image_url='static/uploads/t-shirt.jpg'),
        Product(name='Vounterr T-Shirt', price=349, image_url='static/uploads/Vounteer T-shirts.jpg'),
        Product(name='Stars Style Children T-Shirt', price=349, image_url='static/uploads/Starts T-shirts.jpg'),
        Product(name='Customarize Cup', price=349, image_url='static/uploads/cup.jpg'),
        Product(name='Brothers T-Shirts', price=349, image_url='static/uploads/Brothers T-shirts.jpg'),
        Product(name='Bhoot logo Style T-Shirt', price=349, image_url='static/uploads/Bhoot T-shirt.jpg'),
        Product(name='Beauty and Beast Mug', price=349, image_url='static/uploads/Beauty and Beast mugs.jpg'),
        Product(name='Beautiful cups', price=349, image_url='static/uploads/beautiful cups.jpg')
    ]
    db.session.add_all(products)
    db.session.commit()
    return "Dummy products added successfully!"

@app.route('/')
def home():
    products = Product.query.all()
    users = User.query.all()
    unread_count = 0
    if 'user_id' in session:
        unread_count = Message.query.filter_by(recipient_id=session['user_id']).filter_by(is_read=False).count()
    return render_template('home.html', products=products, users=users, unread_count=unread_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, address=address, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('home'))


@app.route('/history')
def history():
    orders = CustomOrder.query.all()
    return render_template('history.html', orders=orders)

@app.route('/customize/<int:product_id>', methods=['GET', 'POST'])
def customize(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        text = request.form['custom_text']
        color = request.form['color']
        image = request.files['image']
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        order = CustomOrder(
            product_id=product_id,
            custom_text=text,
            color=color,
            uploaded_image=filepath
        )
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('preview', order_id=order.id))
    return render_template('customize.html', product=product)

@app.route('/preview/<int:order_id>', methods=['GET', 'POST'])
def preview(order_id):
    order = CustomOrder.query.get_or_404(order_id)
    if request.method == 'POST':
        item = CartItem(order_id=order.id, quantity=1)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('cart'))
    return render_template('preview.html', order=order)

@app.route('/cart')
def cart():
    items = CartItem.query.all()
    total = sum(item.custom_order.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout')
def checkout():
    items = CartItem.query.all()
    total = sum(item.custom_order.product.price * item.quantity for item in items)
    user = User.query.get(session.get('user_id'))

    db.session.query(CartItem).delete()
    db.session.commit()

    return render_template('checkout.html', items=items, total=total, user=user)

@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    if request.method == 'POST':
        session['shipping_name'] = request.form['name']
        session['shipping_address'] = request.form['address']
        return redirect(url_for('summary'))
    return render_template('shipping.html')

@app.route('/summary', methods=['GET'])
def summary():
    items = CartItem.query.all()
    shipping_name = session.get('shipping_name')
    shipping_address = session.get('shipping_address')
    return render_template('summary.html', items=items, name=shipping_name, address=shipping_address)

@app.route('/thank-you', methods=['POST'])
def thank_you():
    return render_template('thank_you.html')

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat(user_id):
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    sender_id = session['user_id']
    recipient = User.query.get_or_404(user_id)

    if request.method == 'POST':
        content = request.form['content']
        msg = Message(sender_id=sender_id, recipient_id=user_id, content=content, is_read=False)
        db.session.add(msg)
        db.session.commit()
        flash("Message sent!")

    # Mark unread as read
    unread = Message.query.filter_by(sender_id=user_id, recipient_id=sender_id, is_read=False).all()
    for msg in unread:
        msg.is_read = True
    db.session.commit()

    messages = Message.query.filter(
        or_(
            (Message.sender_id == sender_id) & (Message.recipient_id == user_id),
            (Message.sender_id == user_id) & (Message.recipient_id == sender_id)
        )
    ).order_by(Message.timestamp).all()

    return render_template('chat.html', messages=messages, recipient=recipient)

if __name__ == '__main__':
    app.run(debug=True)
