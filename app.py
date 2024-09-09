from models import Seller,Admin,Buyer, Transaction
from config import app,Resource,api,make_response,request,db
from flask_jwt_extended import create_access_token, get_jwt_identity, current_user, jwt_required, JWTManager
from flask import Flask,jsonify
import uuid

app.config["JWT_SECRET_KEY"] = "b'Y\xf1Xz\x01\xad|eQ\x80t \xca\x1a\x10K'"  
app.config['JWT_TOKEN_LOCATION'] = ['headers']

jwt = JWTManager(app)

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
    else:
        return None
    



class SignUp(Resource):
    def post(self):
        
        data = request.get_json()
        name = data.get("username")
        email = data.get("email")
        password = data.get("password")
        phone_number = data.get("phone_number")
        role = data.get("role")  

        if role == "Admin":
            try:
                user = Admin(
                    username=name,
                    email=email,
                    phone_number=phone_number,
                    
                )
                user.password_hash=password
                db.session.add(user)
                db.session.commit()

                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": e.args}, 422
            
        elif role == "Buyer":
            try:
                user = Buyer(
                    username=name,
                    email=email,
                    phone_number=phone_number,
                    
                )
                user.password_hash=password
                db.session.add(user)
                db.session.commit()

                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": e.args}, 422
            
        elif role == "Seller":
            try:
                user = Seller(
                    username=name,
                    email=email,
                    phone_number=phone_number,
                    
                )
                user.password_hash = password
                db.session.add(user)
                db.session.commit()

                access_token = create_access_token(identity=user)
                return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
            except Exception as e:
                return {"error": e.args}, 422
        else:
            return make_response({"error": "Invalid role"}, 400)

api.add_resource(SignUp, "/signup")



class Login(Resource):
    def post(self):
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
        else:
            return make_response({"error": "Unauthorized"}, 401)

api.add_resource(Login, "/login")



class CheckSession(Resource):
    @jwt_required()
    def get(self):
        return make_response(current_user.to_dict(), 200)

api.add_resource(CheckSession, '/check_session', endpoint="check_session")


class TransactionsById(Resource):
    """ @jwt_required() """
    def get(self,id):
        transaction = Transaction.query.filter_by(id=id).first()
        if transaction:

            return make_response(transaction.to_dict(), 200)
        
        else:
            return make_response({"error":"Transaction not found"}, 404)


    """ @jwt_required() """
    def patch(self,id):
        data = request.get_json()

        transaction = Transaction.query.filter_by(id=id).first()

        if transaction:
            for field in ["message", "product_name", "quantity", "total_price"]:
                if field in data:
                    setattr(transaction, field, data[field])

                db.session.commit()
                return make_response(transaction.to_dict(), 200)
        else:
            return make_response({"error": "Transaction not found"}, 404)

api.add_resource(TransactionsById,"/transaction/<int:id>")


class TransactionClass(Resource):
    """ @jwt_required() """
    def get(self):
        transactions = Transaction.query.all()
        return make_response([transaction.to_dict() for transaction in transactions], 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        token = str(uuid.uuid4())
        

        transaction = Transaction(
            message = data.get("message"),
            product_name = data.get("product_name"),
            quantity = int(data.get("quantity")),
            total_price = int(data.get("total_price")),
            seller_id = current_user.id,
            token = token

        )

        db.session.add(transaction)
        db.session.commit()

        response = make_response(
            {
                "transaction":transaction.to_dict(),
                "transaction_link": f"https://payment-app-backend-lemon.vercel.app/transaction/{token}"
            },
            201
        )
        return response
    
api.add_resource(TransactionClass,"/transactions")


@app.route('/transactionByToken/<token>', methods=['GET'])
def get_transaction_by_token(token):
    transaction = Transaction.query.filter_by(token=token).first()  
    if transaction:
        return make_response(transaction.to_dict(), 200)
    return jsonify({'error': 'Transaction not found'}), 404
        




if __name__ == "__main__":
    app.run(debug=True,port=5555)


