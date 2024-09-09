from models import Seller, Admin, Buyer, Transaction
from config import app, db
from flask_restx import Resource, Api, fields
from flask_jwt_extended import create_access_token, get_jwt_identity, current_user, jwt_required, JWTManager
from flask import Flask, jsonify, make_response, request


app.config["JWT_SECRET_KEY"] = "b'Y\xf1Xz\x01\xad|eQ\x80t \xca\x1a\x10K'"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)
api = Api(app, doc='/swagger', version="1.0", title="Payment App", description="API for payment system app")


@jwt.user_identity_loader
def user_identity_lookup(user):
    return {"id": user.id, "role": user.__class__.__name__} 

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user_id = identity["id"]
    role = identity["role"]
    
    if role == "Admin":
        return Admin.query.filter_by(id=user_id).one_or_none()
    elif role == "Seller":
        return Seller.query.filter_by(id=user_id).one_or_none()
    elif role == "Buyer":
        return Buyer.query.filter_by(id=user_id).one_or_none()
    return None



signup_model = api.model('SignUp', {
    'username': fields.String(required=True, description="User's username"),
    'email': fields.String(required=True, description="User's email"),
    'password': fields.String(required=True, description="User's password"),
    'phone_number': fields.String(required=True, description="User's phone number"),
    'role': fields.String(required=True, enum=['Admin', 'Seller', 'Buyer'], description="User role")
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description="User's email"),
    'password': fields.String(required=True, description="User's password"),
    'role': fields.String(required=True, enum=['Admin', 'Seller', 'Buyer'], description="User role")
})

transaction_model = api.model('Transaction', {
    'message': fields.String(required=True, description="Transaction message"),
    'product_name': fields.String(required=True, description="Product name"),
    'quantity': fields.Integer(required=True, description="Quantity of the product"),
    'total_price': fields.Float(required=True, description="Total price of the product"),
})



@api.route('/signup')
class SignUp(Resource):
    @api.expect(signup_model)
    @api.response(201, 'User created successfully')
    @api.response(422, 'Validation Error')
    def post(self):
        """Sign up a new user (Admin, Seller, Buyer)"""
        data = request.get_json()
        name = data.get("username")
        email = data.get("email")
        password = data.get("password")
        phone_number = data.get("phone_number")
        role = data.get("role")

        if role == "Admin":
            try:
                user = Admin(username=name, email=email, phone_number=phone_number)
                user.password_hash = password
                db.session.add(user)
                db.session.commit()
                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": str(e)}, 422

        elif role == "Buyer":
            try:
                user = Buyer(username=name, email=email, phone_number=phone_number)
                user.password_hash = password
                db.session.add(user)
                db.session.commit()
                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": str(e)}, 422

        elif role == "Seller":
            try:
                user = Seller(username=name, email=email, phone_number=phone_number)
                user.password_hash = password
                db.session.add(user)
                db.session.commit()
                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": str(e)}, 422

        return make_response({"error": "Invalid role"}, 400)


@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(201, 'Login successful')
    @api.response(401, 'Unauthorized')
    @api.response(400, 'Invalid role')
    def post(self):
        """Login for existing users"""
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        user_class = {"Seller": Seller, "Admin": Admin, "Buyer": Buyer}.get(role)
        if not user_class:
            return make_response({"error": "Invalid role"}, 400)

        user = user_class.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            access_token = create_access_token(identity=user)
            return make_response({"user": user.to_dict(), "access_token": access_token}, 201)
        return make_response({"error": "Unauthorized"}, 401)


@api.route('/check_session')
class CheckSession(Resource):
    """ @jwt_required() """
    @api.response(200, 'Session valid')
    def get(self):
        """Check if the user session is valid"""
        return make_response(current_user.to_dict(), 200)


@api.route('/transaction/<int:id>')
class TransactionsById(Resource):
    """ @jwt_required() """
    @api.response(200, 'Transaction found')
    @api.response(404, 'Transaction not found')
    def get(self, id):
        """Get a transaction by ID"""
        transaction = Transaction.query.filter_by(id=id).first()
        if transaction:
            return make_response(transaction.to_dict(), 200)
        return make_response({"error": "Transaction not found"}, 404)

    """ @jwt_required() """
    @api.expect(transaction_model)
    @api.response(200, 'Transaction updated')
    @api.response(404, 'Transaction not found')
    def patch(self, id):
        """Update a transaction by ID"""
        data = request.get_json()
        transaction = Transaction.query.filter_by(id=id).first()
        if transaction:
            for field in ["message", "product_name", "quantity", "total_price"]:
                if field in data:
                    setattr(transaction, field, data[field])
            db.session.commit()
            return make_response(transaction.to_dict(), 200)
        return make_response({"error": "Transaction not found"}, 404)


@api.route('/transactions')
class TransactionClass(Resource):
    """ @jwt_required() """
    @api.response(200, 'Transactions fetched successfully')
    def get(self):
        """Get all transactions"""
        transactions = Transaction.query.all()
        return make_response([transaction.to_dict() for transaction in transactions], 200)

    """ @jwt_required() """
    @api.expect(transaction_model)
    @api.response(201, 'Transaction created')
    def post(self):
        """Create a new transaction"""
        data = request.get_json()
        transaction = Transaction(
            message=data.get("message"),
            product_name=data.get("product_name"),
            quantity=int(data.get("quantity")),
            total_price=int(data.get("total_price")),
            seller_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        return make_response(transaction.to_dict(), 201)


if __name__ == "__main__":
    app.run(debug=True, port=5555)
