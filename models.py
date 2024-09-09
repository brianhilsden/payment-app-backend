from config import db,bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime



class Seller(SerializerMixin,db.Model):
    __tablename__ = "sellers"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    role = db.Column(db.String, default = "Seller")
    phone_number = db.Column(db.String)
    _password_hash = db.Column(db.String)
   

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password is not readable')
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    


class Admin(SerializerMixin,db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    phone_number = db.Column(db.String)
    _password_hash = db.Column(db.String)
    role = db.Column(db.String, default = "Admin")

    transactions = db.relationship("Transaction", back_populates = "seller")

    serialize_rules = ("transactions.seller",)

    


    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password is not readable')
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    

class Buyer(SerializerMixin,db.Model):
    __tablename__ = "buyers"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    phone_number = db.Column(db.String)
    _password_hash = db.Column(db.String)
    role = db.Column(db.String, default = "Buyer")

    transactions = db.relationship("Transaction", back_populates = "buyer")

    serialize_rules = ("transactions.buyer",)


    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password is not readable')
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))



class Transaction(SerializerMixin,db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.String)
    product_name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String)
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyers.id"))
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id"))
    purchase_link = db.Column(db.String)

    customer = db.relationship("Customer", back_populates = "transactions")
    seller = db.relationship("Seller", back_populates ="transactions")

    serialize_rules = ("-customer.transactions","-seller.transactions" )
    
