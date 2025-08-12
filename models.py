from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# ---------- User Model ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ---------- Product Model ----------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)

# ---------- Custom Order Model ----------
class CustomOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    custom_text = db.Column(db.String(100))
    color = db.Column(db.String(50))
    uploaded_image = db.Column(db.String(300))
    product = db.relationship('Product')

# ---------- Cart Item Model ----------
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('custom_order.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    custom_order = db.relationship('CustomOrder')

# ---------- Message Model ----------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
