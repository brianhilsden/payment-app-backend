from models import Seller, Admin, Buyer, Transaction
from config import db, app
from datetime import datetime

def seed_data():
    with app.app_context():
        # Clear the tables
        db.session.query(Transaction).delete()
        db.session.query(Seller).delete()
        db.session.query(Buyer).delete()
        db.session.query(Admin).delete()
        
        db.session.commit()

        # Seed Admins
        admin1 = Admin(
            username="admin1",
            email="admin1@example.com",
            phone_number="0700000001",
            role="Admin"
        )
        admin1.password_hash = "adminpassword1"

        admin2 = Admin(
            username="admin2",
            email="admin2@example.com",
            phone_number="0700000002",
            role="Admin"
        )
        admin2.password_hash = "adminpassword2"

        # Seed Sellers
        seller1 = Seller(
            username="seller1",
            email="seller1@example.com",
            phone_number="0700000011",
            role="Seller"
        )
        seller1.password_hash = "sellerpassword1"

        seller2 = Seller(
            username="seller2",
            email="seller2@example.com",
            phone_number="0700000012",
            role="Seller"
        )
        seller2.password_hash = "sellerpassword2"

        # Seed Buyers
        buyer1 = Buyer(
            username="buyer1",
            email="buyer1@example.com",
            phone_number="0700000021",
            role="Buyer"
        )
        buyer1.password_hash = "buyerpassword1"

        buyer2 = Buyer(
            username="buyer2",
            email="buyer2@example.com",
            phone_number="0700000022",
            role="Buyer"
        )
        buyer2.password_hash = "buyerpassword2"

        db.session.add_all([admin1, admin2, seller1, seller2, buyer1, buyer2])
        db.session.commit()


        # Seed Transactions
        transaction1 = Transaction(
            message="First transaction",
            product_name="Product A",
            quantity=2,
            total_price=2000,
            status="Pending",
            buyer_id=buyer1.id,  # Assuming buyer1 is saved with ID 1
            seller_id=seller1.id,  # Assuming seller1 is saved with ID 1
            purchase_link="http://example.com/product-a",
            date=datetime.now()
        )

        transaction2 = Transaction(
            message="Second transaction",
            product_name="Product B",
            quantity=1,
            total_price=1000,
            status="Completed",
            buyer_id=buyer2.id,  # Assuming buyer2 is saved with ID 2
            seller_id=seller2.id,  # Assuming seller2 is saved with ID 2
            purchase_link="http://example.com/product-b",
            date=datetime.now()
        )

        # Add data to the session
        db.session.add_all([transaction1, transaction2])

        # Commit to the database
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
