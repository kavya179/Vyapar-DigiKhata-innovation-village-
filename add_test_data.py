"""
Complete Test Data Insertion Script
Adds users, customers, inventory, transactions, and suppliers

Usage:
    python add_test_data.py
"""

import sqlite3
from datetime import datetime, timedelta
import random
from database import (
    insert_user, get_users, chek_pass,
    add_customer, add_inventory_item, add_transaction,
    add_supplier, update_supplier_due, update_supplier_payment
)

def add_test_users():
    """Add test users to the database"""
    
    test_users = [
        {
            'name': 'Kavya Patel',
            'email': 'kavya@gmail.com',
            'shop_name': 'Kavya General Store',
            'password': '123456'
        },
        {
            'name': 'Nirav Shah',
            'email': 'nirav@gmail.com',
            'shop_name': 'Nirav Electronics',
            'password': '147258'
        },
        {
            'name': 'Asha Desai',
            'email': 'asha@gmail.com',
            'shop_name': 'Asha Textiles',
            'password': '963258'
        }
    ]
    
    print("=" * 60)
    print("STEP 1: Adding Test Users")
    print("=" * 60)
    
    created_users = []
    
    for user in test_users:
        print(f"\n📧 Processing: {user['email']}")
        
        existing_user = get_users(user['email'])
        
        if existing_user:
            print(f"  ⚠️  User already exists")
            user_id = existing_user[0][0]
        else:
            password_exists = chek_pass(user['password'])
            final_password = user['password']
            
            if password_exists:
                final_password = user['password'] + "1"
                print(f"  ⚠️  Password modified to: {final_password}")
            
            insert_user(
                name=user['name'],
                email=user['email'],
                shop_name=user['shop_name'],
                password=final_password
            )
            
            user_data = get_users(user['email'])
            user_id = user_data[0][0]
            print(f"  ✅ User created successfully")
        
        created_users.append({
            'id': user_id,
            'email': user['email'],
            'name': user['name'],
            'shop': user['shop_name']
        })
    
    return created_users

def add_customers_data(users):
    """Add customers for each user"""
    
    print("\n" + "=" * 60)
    print("STEP 2: Adding Customers")
    print("=" * 60)
    
    customers_data = {
        'kavya@gmail.com': [
            {'name': 'Ramesh Kumar', 'contact': '9876543210', 'address': '123 MG Road, Ahmedabad'},
            {'name': 'Priya Sharma', 'contact': '9876543211', 'address': '45 CG Road, Ahmedabad'},
            {'name': 'Vijay Patel', 'contact': '9876543212', 'address': '78 SG Highway, Ahmedabad'},
            {'name': 'Anjali Mehta', 'contact': '9876543213', 'address': '90 Ashram Road, Ahmedabad'},
            {'name': 'Suresh Desai', 'contact': '9876543214', 'address': '12 Satellite, Ahmedabad'},
        ],
        'nirav@gmail.com': [
            {'name': 'Kiran Shah', 'contact': '9876543215', 'address': '34 Navrangpura, Ahmedabad'},
            {'name': 'Meera Joshi', 'contact': '9876543216', 'address': '56 Bodakdev, Ahmedabad'},
            {'name': 'Rajesh Rao', 'contact': '9876543217', 'address': '23 Vastrapur, Ahmedabad'},
            {'name': 'Pooja Nair', 'contact': '9876543218', 'address': '67 Maninagar, Ahmedabad'},
        ],
        'asha@gmail.com': [
            {'name': 'Deepak Singh', 'contact': '9876543219', 'address': '89 Paldi, Ahmedabad'},
            {'name': 'Sneha Reddy', 'contact': '9876543220', 'address': '11 Ambawadi, Ahmedabad'},
            {'name': 'Amit Gupta', 'contact': '9876543221', 'address': '33 Thaltej, Ahmedabad'},
            {'name': 'Nisha Kapoor', 'contact': '9876543222', 'address': '55 Bopal, Ahmedabad'},
            {'name': 'Rahul Verma', 'contact': '9876543223', 'address': '77 Gota, Ahmedabad'},
        ]
    }
    
    customer_ids = {}
    
    for user in users:
        print(f"\n👤 {user['name']} ({user['email']}):")
        customer_ids[user['email']] = []
        
        for customer in customers_data.get(user['email'], []):
            success, message = add_customer(
                user['id'],
                customer['name'],
                customer['contact'],
                customer['address']
            )
            
            if success:
                print(f"  ✅ Added: {customer['name']}")
                # Get customer ID
                conn = sqlite3.connect("Vyapar_Digikhata.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM customers WHERE contact = ?", (customer['contact'],))
                cust_id = cursor.fetchone()[0]
                conn.close()
                customer_ids[user['email']].append(cust_id)
            else:
                print(f"  ⚠️  {customer['name']}: {message}")
    
    return customer_ids

def add_inventory_data(users):
    """Add inventory items for each user"""
    
    print("\n" + "=" * 60)
    print("STEP 3: Adding Inventory Items")
    print("=" * 60)
    
    inventory_data = {
        'kavya@gmail.com': [
            {'item': 'Rice (1kg)', 'quantity': 50, 'price': 60.00},
            {'item': 'Wheat Flour (1kg)', 'quantity': 40, 'price': 45.00},
            {'item': 'Sugar (1kg)', 'quantity': 8, 'price': 50.00},
            {'item': 'Cooking Oil (1L)', 'quantity': 25, 'price': 180.00},
            {'item': 'Tea Powder (250g)', 'quantity': 15, 'price': 120.00},
            {'item': 'Coffee (200g)', 'quantity': 4, 'price': 250.00},
            {'item': 'Salt (1kg)', 'quantity': 60, 'price': 20.00},
            {'item': 'Masala Mix', 'quantity': 9, 'price': 80.00},
        ],
        'nirav@gmail.com': [
            {'item': 'LED TV 32"', 'quantity': 12, 'price': 15000.00},
            {'item': 'Washing Machine', 'quantity': 3, 'price': 18000.00},
            {'item': 'Refrigerator', 'quantity': 5, 'price': 25000.00},
            {'item': 'Microwave Oven', 'quantity': 8, 'price': 8000.00},
            {'item': 'Ceiling Fan', 'quantity': 20, 'price': 1500.00},
            {'item': 'Mixer Grinder', 'quantity': 15, 'price': 3500.00},
        ],
        'asha@gmail.com': [
            {'item': 'Cotton Saree', 'quantity': 25, 'price': 1200.00},
            {'item': 'Silk Saree', 'quantity': 6, 'price': 3500.00},
            {'item': 'Cotton Shirt', 'quantity': 30, 'price': 450.00},
            {'item': 'Jeans Pant', 'quantity': 9, 'price': 800.00},
            {'item': 'Bedsheet Set', 'quantity': 18, 'price': 600.00},
            {'item': 'Towel Set', 'quantity': 40, 'price': 250.00},
            {'item': 'Kurta Set', 'quantity': 3, 'price': 950.00},
        ]
    }
    
    inventory_ids = {}
    
    for user in users:
        print(f"\n📦 {user['name']} ({user['email']}):")
        inventory_ids[user['email']] = []
        
        for item in inventory_data.get(user['email'], []):
            add_inventory_item(
                user['id'],
                item['item'],
                item['quantity'],
                item['price']
            )
            print(f"  ✅ Added: {item['item']} (Qty: {item['quantity']}, Price: ₹{item['price']})")
            
            # Get inventory ID
            conn = sqlite3.connect("Vyapar_Digikhata.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", 
                          (user['id'], item['item']))
            inv_id = cursor.fetchone()[0]
            conn.close()
            inventory_ids[user['email']].append(inv_id)
    
    return inventory_ids

def add_transactions_data(users, customer_ids):
    """Add transactions for each user"""
    
    print("\n" + "=" * 60)
    print("STEP 4: Adding Transactions")
    print("=" * 60)
    
    for user in users:
        print(f"\n💳 {user['name']} ({user['email']}):")
        
        cust_ids = customer_ids.get(user['email'], [])
        if not cust_ids:
            print("  ⚠️  No customers found")
            continue
        
        # Add various transactions over the past 60 days
        transaction_count = 0
        
        for days_ago in range(60, 0, -5):
            for _ in range(random.randint(1, 3)):
                customer_id = random.choice(cust_ids)
                trans_type = random.choice(['Credit', 'Credit', 'Debit'])  # More credits
                amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000])
                
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                if trans_type == 'Credit':
                    description = f"Sale of goods - Invoice #{random.randint(1000, 9999)}"
                else:
                    description = f"Payment received - Receipt #{random.randint(1000, 9999)}"
                
                success, message = add_transaction(
                    user['id'],
                    customer_id,
                    trans_type,
                    amount,
                    date,
                    description
                )
                
                if success:
                    transaction_count += 1
        
        print(f"  ✅ Added {transaction_count} transactions")

def add_suppliers_data(users):
    """Add suppliers for each user"""
    
    print("\n" + "=" * 60)
    print("STEP 5: Adding Suppliers")
    print("=" * 60)
    
    suppliers_data = {
        'kavya@gmail.com': [
            {'name': 'Wholesale Grain Traders', 'contact': '9123456780', 'due': 50000, 'paid': 30000},
            {'name': 'Spice Suppliers Ltd', 'contact': '9123456781', 'due': 25000, 'paid': 25000},
            {'name': 'Oil Distributors', 'contact': '9123456782', 'due': 35000, 'paid': 20000},
        ],
        'nirav@gmail.com': [
            {'name': 'Electronics Wholesale Hub', 'contact': '9123456783', 'due': 500000, 'paid': 350000},
            {'name': 'Appliance Distributors', 'contact': '9123456784', 'due': 300000, 'paid': 300000},
        ],
        'asha@gmail.com': [
            {'name': 'Textile Mills', 'contact': '9123456785', 'due': 150000, 'paid': 100000},
            {'name': 'Cotton Suppliers', 'contact': '9123456786', 'due': 80000, 'paid': 60000},
            {'name': 'Garment Manufacturers', 'contact': '9123456787', 'due': 120000, 'paid': 120000},
        ]
    }
    
    for user in users:
        print(f"\n🏭 {user['name']} ({user['email']}):")
        
        for supplier in suppliers_data.get(user['email'], []):
            add_supplier(
                user['id'],
                supplier['name'],
                supplier['contact'],
                supplier['due'],
                supplier['paid']
            )
            balance = supplier['due'] - supplier['paid']
            print(f"  ✅ Added: {supplier['name']} (Due: ₹{supplier['due']}, Paid: ₹{supplier['paid']}, Balance: ₹{balance})")

def main():
    """Main function to add all test data"""
    
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  VYAPAR DIGIKHATA - TEST DATA INSERTION SCRIPT  ".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    try:
        # Step 1: Add users
        users = add_test_users()
        
        # Step 2: Add customers
        customer_ids = add_customers_data(users)
        
        # Step 3: Add inventory
        inventory_ids = add_inventory_data(users)
        
        # Step 4: Add transactions
        add_transactions_data(users, customer_ids)
        
        # Step 5: Add suppliers
        add_suppliers_data(users)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY - Test Data Added Successfully!")
        print("=" * 60)
        
        for user in users:
            print(f"\n📧 {user['email']}")
            print(f"   Owner: {user['name']}")
            print(f"   Shop: {user['shop']}")
            print(f"   Password: Check output above for final password")
        
        print("\n" + "=" * 60)
        print("LOGIN CREDENTIALS:")
        print("=" * 60)
        print("1. kavya@gmail.com / 123456")
        print("2. nirav@gmail.com / 147258")
        print("3. asha@gmail.com / 963258")
        print("\n⚠️  Note: If passwords were modified, check the output above.")
        
        print("\n" + "=" * 60)
        print("DATA ADDED:")
        print("=" * 60)
        print("✅ Users: 3")
        print("✅ Customers: ~14 total (4-5 per user)")
        print("✅ Inventory Items: ~21 total (6-8 per user)")
        print("✅ Transactions: ~100+ total (distributed across 60 days)")
        print("✅ Suppliers: ~8 total (2-3 per user)")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Run: streamlit run app.py")
        print("2. Login with any test account")
        print("3. Explore all features:")
        print("   • View customers and transactions")
        print("   • Check inventory (some items have low stock!)")
        print("   • See business analytics graphs")
        print("   • Check notifications for alerts")
        print("   • Export data to CSV")
        print("\n✅ All test data added successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure database.py is in the same directory!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()