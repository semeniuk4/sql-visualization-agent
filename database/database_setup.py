# database_setup.py
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import warnings
warnings.filterwarnings('ignore')

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',  # Change if needed
    'password': 'postgres',  # Change to your password
    'database': 'olist_ecommerce'
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_PARAMS['host'],
            port=DB_PARAMS['port'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_PARAMS['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_PARAMS['database'])
            ))
            print(f"✓ Database '{DB_PARAMS['database']}' created successfully")
        else:
            print(f"✓ Database '{DB_PARAMS['database']}' already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        raise

def create_tables():
    """Create all tables with proper relationships"""
    
    # SQL statements for creating tables
    create_table_queries = [
        # 1. Geolocation (independent table)
        """
        CREATE TABLE IF NOT EXISTS geolocation (
            geolocation_zip_code_prefix INTEGER PRIMARY KEY,
            geolocation_lat FLOAT NOT NULL,
            geolocation_lng FLOAT NOT NULL,
            geolocation_city VARCHAR(100),
            geolocation_state VARCHAR(2)
        );
        """,
        
        # 2. Customers (geolocation is optional - not all zip codes are in geolocation table)
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            customer_unique_id VARCHAR(50) NOT NULL,
            customer_zip_code_prefix INTEGER,
            customer_city VARCHAR(100),
            customer_state VARCHAR(2)
        );
        """,
        
        # 3. Sellers (depends on geolocation)
        """
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id VARCHAR(50) PRIMARY KEY,
            seller_zip_code_prefix INTEGER,
            seller_city VARCHAR(100),
            seller_state VARCHAR(2),
            FOREIGN KEY (seller_zip_code_prefix) 
                REFERENCES geolocation(geolocation_zip_code_prefix)
        );
        """,
        
        # 4. Product category translation
        """
        CREATE TABLE IF NOT EXISTS product_category_translation (
            product_category_name VARCHAR(100) PRIMARY KEY,
            product_category_name_english VARCHAR(100) NOT NULL
        );
        """,
        
        # 5. Products (depends on category translation)
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(50) PRIMARY KEY,
            product_category_name VARCHAR(100),
            product_name_lenght FLOAT,
            product_description_lenght FLOAT,
            product_photos_qty FLOAT,
            product_weight_g FLOAT,
            product_length_cm FLOAT,
            product_height_cm FLOAT,
            product_width_cm FLOAT,
            FOREIGN KEY (product_category_name) 
                REFERENCES product_category_translation(product_category_name)
        );
        """,
        
        # 6. Orders (depends on customers)
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            order_status VARCHAR(20) NOT NULL,
            order_purchase_timestamp TIMESTAMP NOT NULL,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            delivery_time_days FLOAT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """,
        
        # 7. Order Items (depends on orders, products, sellers)
        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_id VARCHAR(50),
            order_item_id INTEGER,
            product_id VARCHAR(50) NOT NULL,
            seller_id VARCHAR(50) NOT NULL,
            shipping_limit_date TIMESTAMP,
            price FLOAT NOT NULL,
            freight_value FLOAT NOT NULL,
            PRIMARY KEY (order_id, order_item_id),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
        );
        """,
        
        # 8. Order Payments (depends on orders)
        """
        CREATE TABLE IF NOT EXISTS order_payments (
            order_id VARCHAR(50),
            payment_sequential INTEGER,
            payment_type VARCHAR(20) NOT NULL,
            payment_installments INTEGER NOT NULL,
            payment_value FLOAT NOT NULL,
            PRIMARY KEY (order_id, payment_sequential),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        """,
        
        # 9. Order Reviews (depends on orders)
        """
        CREATE TABLE IF NOT EXISTS order_reviews (
            review_id VARCHAR(50) PRIMARY KEY,
            order_id VARCHAR(50) NOT NULL,
            review_score INTEGER NOT NULL,
            review_comment_title TEXT,
            review_comment_message TEXT,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP,
            has_title BOOLEAN,
            has_message BOOLEAN,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        """
    ]
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("\n📋 Creating tables...")
        for i, query in enumerate(create_table_queries, 1):
            cursor.execute(query)
            table_name = query.split('TABLE IF NOT EXISTS')[1].split('(')[0].strip()
            print(f"  {i}. Table '{table_name}' created/verified")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ All tables created successfully\n")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise

def load_data_to_postgres():
    """Load data from CSV files into PostgreSQL tables"""
    
    # Define the order of loading (respecting foreign key dependencies)
    load_order = [
        ('geolocation', './datasets/geolocation_clean.csv'),
        ('customers', './datasets/olist_customers_dataset.csv'),
        ('sellers', './datasets/olist_sellers_dataset.csv'),
        ('product_category_translation', './datasets/product_category_name_translation.csv'),
        ('products', './datasets/products_clean.csv'),
        ('orders', './datasets/orders_clean.csv'),
        ('order_items', './datasets/olist_order_items_dataset.csv'),
        ('order_payments', './datasets/olist_order_payments_dataset.csv'),
        ('order_reviews', './datasets/reviews_clean.csv')
    ]
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("📊 Loading data into tables...\n")
        
        for table_name, csv_path in load_order:
            print(f"  Loading {table_name}...", end=' ')
            
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Replace NaN with None for proper NULL handling
            df = df.where(pd.notnull(df), None)
            
            # Prepare column names and placeholders
            columns = df.columns.tolist()
            placeholders = ','.join(['%s'] * len(columns))
            columns_str = ','.join(columns)
            
            # Insert data
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            # Convert DataFrame to list of tuples
            data = [tuple(row) for row in df.values]
            
            # Execute batch insert
            cursor.executemany(insert_query, data)
            conn.commit()
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"✓ {count:,} rows")
        
        cursor.close()
        conn.close()
        print("\n✓ All data loaded successfully!")
        
    except Exception as e:
        print(f"\n✗ Error loading data: {e}")
        raise

def verify_database():
    """Verify the database setup"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("DATABASE VERIFICATION")
        print("="*60)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Tables in database: {len(tables)}\n")
        
        # Count rows in each table
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name:35s}: {count:>10,} rows")
        
        # Test some relationships
        print("\n🔗 Testing relationships:")
        
        test_queries = [
            ("Orders with valid customers", 
             "SELECT COUNT(*) FROM orders o JOIN customers c ON o.customer_id = c.customer_id"),
            ("Order items with valid orders", 
             "SELECT COUNT(*) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id"),
            ("Products with category translation", 
             "SELECT COUNT(*) FROM products p LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name"),
            ("Customers with geolocation", 
             "SELECT COUNT(*) FROM customers c JOIN geolocation g ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix")
        ]
        
        for description, query in test_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {description:40s}: {count:>10,}")
        
        print("\n" + "="*60)
        print("✓ Database setup complete and verified!")
        print("="*60 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        raise

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("OLIST E-COMMERCE DATABASE SETUP")
    print("="*60 + "\n")
    
    try:
        # Step 1: Create database
        print("Step 1: Creating database...")
        create_database()
        
        # Step 2: Create tables
        print("\nStep 2: Creating tables...")
        create_tables()
        
        # Step 3: Load data
        print("Step 3: Loading data...")
        load_data_to_postgres()
        
        # Step 4: Verify
        print("\nStep 4: Verifying setup...")
        verify_database()
        
        print("\n🎉 SUCCESS! Your database is ready for the agent analyzer!")
        print(f"\nConnection details:")
        print(f"  Host: {DB_PARAMS['host']}")
        print(f"  Port: {DB_PARAMS['port']}")
        print(f"  Database: {DB_PARAMS['database']}")
        print(f"  User: {DB_PARAMS['user']}")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()