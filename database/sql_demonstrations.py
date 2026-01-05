"""
SQL Query Demonstrations
Comprehensive examples of joins, filtering, and aggregations
"""

import psycopg2
import pandas as pd
from tabulate import tabulate
import warnings
import os
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

load_dotenv() 

DB_PARAMS = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)), 
    
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def run_query(query, description):
    """Execute SQL query and display results"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        
        print(f"{description}")        
        print(f"\nQuery:\n{query}\n")
        print(f"Results ({len(df)} rows):")
        print(tabulate(df.head(10), headers='keys', tablefmt='psql', showindex=False))
        if len(df) > 10:
            print(f"\n... showing first 10 of {len(df)} rows")
        print()
        
        return df
    except Exception as e:
        print(f"Error: {e}\n")
        return None


def query_joins():
    """Various types of SQL joins"""
    
    
    print("PART 1: SQL JOINS")
   
    
    # 1.1 INNER JOIN - Orders with Customer Information
    query1 = """
    SELECT 
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    ORDER BY o.order_purchase_timestamp DESC
    LIMIT 10;
    """
    run_query(query1, "INNER JOIN: Orders with Customer Details")
    
    # 1.2 MULTIPLE JOINS - Complete Order Information
    query2 = """
    SELECT 
        o.order_id,
        c.customer_state,
        p.product_category_name,
        pct.product_category_name_english,
        oi.price,
        oi.freight_value,
        s.seller_state
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    INNER JOIN sellers s ON oi.seller_id = s.seller_id
    LIMIT 10;
    """
    run_query(query2, "MULTIPLE JOINS: Complete Order Information with Products & Sellers")
    
    # 1.3 LEFT JOIN - All Products with Optional Category Translation
    query3 = """
    SELECT 
        p.product_id,
        p.product_category_name,
        pct.product_category_name_english,
        CASE 
            WHEN pct.product_category_name_english IS NULL THEN 'No Translation'
            ELSE 'Translated'
        END as translation_status
    FROM products p
    LEFT JOIN product_category_translation pct 
        ON p.product_category_name = pct.product_category_name
    LIMIT 10;
    """
    run_query(query3, "LEFT JOIN: Products with Optional Category Translation")


def query_filtering():
    """Advanced filtering examples"""
    
    
    print("PART 2: FILTERING & WHERE CLAUSES")
   
    
    # 2.1 Simple WHERE - High Value Orders
    query1 = """
    SELECT 
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        SUM(oi.price + oi.freight_value) as total_value
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.order_status, o.order_purchase_timestamp
    HAVING SUM(oi.price + oi.freight_value) > 1000
    ORDER BY total_value DESC
    LIMIT 10;
    """
    run_query(query1, "FILTERING: High-Value Orders (>1000)")
    
    # 2.2 Date Range Filtering
    query2 = """
    SELECT 
        DATE_TRUNC('month', order_purchase_timestamp) as month,
        COUNT(*) as total_orders,
        AVG(delivery_time_days) as avg_delivery_days
    FROM orders
    WHERE order_purchase_timestamp >= '2017-01-01' 
        AND order_purchase_timestamp < '2018-01-01'
        AND order_status = 'delivered'
    GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
    ORDER BY month;
    """
    run_query(query2, "DATE FILTERING: Monthly Orders in 2017")
    
    # 2.3 Complex Filtering - Top States by Orders
    query3 = """
    SELECT 
        c.customer_state,
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(DISTINCT c.customer_id) as unique_customers,
        ROUND(AVG(oi.price)::numeric, 2) as avg_order_value
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    HAVING COUNT(DISTINCT o.order_id) > 100
    ORDER BY total_orders DESC
    LIMIT 10;
    """
    run_query(query3, "COMPLEX FILTERING: Top States by Order Volume (>100 orders)")
    
    # 2.4 Pattern Matching - Products with specific characteristics
    query4 = """
    SELECT 
        p.product_category_name,
        pct.product_category_name_english,
        COUNT(*) as product_count,
        ROUND(AVG(p.product_weight_g)::numeric, 2) as avg_weight_g
    FROM products p
    LEFT JOIN product_category_translation pct 
        ON p.product_category_name = pct.product_category_name
    WHERE p.product_weight_g > 5000
        AND p.product_photos_qty >= 3
    GROUP BY p.product_category_name, pct.product_category_name_english
    ORDER BY product_count DESC
    LIMIT 10;
    """
    run_query(query4, "PATTERN FILTERING: Heavy Products (>5kg) with Multiple Photos")


def query_aggregations():
    """Advanced aggregations and analytics"""
    
    
    print("PART 3: AGGREGATIONS & ANALYTICS")
   
    
    # 3.1 Revenue Analysis by Category
    query1 = """
    SELECT 
        COALESCE(pct.product_category_name_english, 'Unknown') as category,
        COUNT(DISTINCT oi.order_id) as total_orders,
        COUNT(DISTINCT oi.product_id) as unique_products,
        ROUND(SUM(oi.price)::numeric, 2) as total_revenue,
        ROUND(AVG(oi.price)::numeric, 2) as avg_price,
        ROUND(MIN(oi.price)::numeric, 2) as min_price,
        ROUND(MAX(oi.price)::numeric, 2) as max_price
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct 
        ON p.product_category_name = pct.product_category_name
    GROUP BY pct.product_category_name_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    run_query(query1, "AGGREGATION: Revenue Analysis by Product Category")
    
    # 3.2 Customer Behavior Analysis
    query2 = """
    SELECT 
        c.customer_state,
        COUNT(DISTINCT c.customer_id) as total_customers,
        COUNT(o.order_id) as total_orders,
        ROUND(COUNT(o.order_id)::numeric / COUNT(DISTINCT c.customer_id), 2) as orders_per_customer,
        ROUND(AVG(oi.price + oi.freight_value)::numeric, 2) as avg_order_value,
        ROUND(SUM(oi.price + oi.freight_value)::numeric, 2) as total_spent
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_state
    ORDER BY total_spent DESC
    LIMIT 10;
    """
    run_query(query2, "AGGREGATION: Customer Behavior by State")
    
    # 3.3 Delivery Performance Analysis
    query3 = """
    SELECT 
        order_status,
        COUNT(*) as order_count,
        ROUND(AVG(delivery_time_days)::numeric, 2) as avg_delivery_days,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delivery_time_days)::numeric, 2) as median_delivery_days,
        ROUND(MIN(delivery_time_days)::numeric, 2) as min_delivery_days,
        ROUND(MAX(delivery_time_days)::numeric, 2) as max_delivery_days
    FROM orders
    WHERE delivery_time_days IS NOT NULL
    GROUP BY order_status
    ORDER BY order_count DESC;
    """
    run_query(query3, "AGGREGATION: Delivery Performance Metrics")
    
    # 3.4 Payment Analysis
    query4 = """
    SELECT 
        op.payment_type,
        COUNT(DISTINCT op.order_id) as total_orders,
        ROUND(AVG(op.payment_installments)::numeric, 2) as avg_installments,
        ROUND(SUM(op.payment_value)::numeric, 2) as total_value,
        ROUND(AVG(op.payment_value)::numeric, 2) as avg_payment_value,
        ROUND(100.0 * COUNT(DISTINCT op.order_id) / SUM(COUNT(DISTINCT op.order_id)) OVER ()::numeric, 2) as percentage_of_orders
    FROM order_payments op
    GROUP BY op.payment_type
    ORDER BY total_value DESC;
    """
    run_query(query4, "AGGREGATION: Payment Method Analysis with Window Functions")


def query_advanced_techniques():
    """Advanced SQL techniques"""
    
    
    print("PART 4: ADVANCED SQL TECHNIQUES")
   
    
    # 4.1 Subquery - Best Selling Products
    query1 = """
    SELECT 
        p.product_id,
        COALESCE(pct.product_category_name_english, p.product_category_name) as category,
        sales.times_sold,
        ROUND(sales.total_revenue::numeric, 2) as total_revenue,
        ROUND(sales.avg_price::numeric, 2) as avg_price
    FROM products p
    LEFT JOIN product_category_translation pct 
        ON p.product_category_name = pct.product_category_name
    INNER JOIN (
        SELECT 
            product_id,
            COUNT(*) as times_sold,
            SUM(price) as total_revenue,
            AVG(price) as avg_price
        FROM order_items
        GROUP BY product_id
    ) sales ON p.product_id = sales.product_id
    ORDER BY sales.times_sold DESC
    LIMIT 10;
    """
    run_query(query1, "SUBQUERY: Top 10 Best-Selling Products")
    
    # 4.2 CTE (Common Table Expression) - Seller Performance
    query2 = """
    WITH seller_stats AS (
        SELECT 
            s.seller_id,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) as total_orders,
            SUM(oi.price) as total_revenue,
            AVG(oi.price) as avg_sale_price
        FROM sellers s
        INNER JOIN order_items oi ON s.seller_id = oi.seller_id
        GROUP BY s.seller_id, s.seller_state
    ),
    state_avg AS (
        SELECT 
            seller_state,
            AVG(total_revenue) as state_avg_revenue
        FROM seller_stats
        GROUP BY seller_state
    )
    SELECT 
        ss.seller_id,
        ss.seller_state,
        ss.total_orders,
        ROUND(ss.total_revenue::numeric, 2) as seller_revenue,
        ROUND(sa.state_avg_revenue::numeric, 2) as state_avg_revenue,
        ROUND(((ss.total_revenue - sa.state_avg_revenue) / sa.state_avg_revenue * 100)::numeric, 2) as performance_vs_state_avg
    FROM seller_stats ss
    INNER JOIN state_avg sa ON ss.seller_state = sa.seller_state
    WHERE ss.total_orders >= 10
    ORDER BY ss.total_revenue DESC
    LIMIT 10;
    """
    run_query(query2, "CTE: Seller Performance vs State Average")
    

def query_business_insights():
    """Business intelligence queries"""
    
    
    print("PART 5: BUSINESS INTELLIGENCE QUERIES")
   
    
    # 5.1 Geographic Analysis - Interstate Commerce
    query1 = """
    SELECT 
        c.customer_state as buyer_state,
        s.seller_state as seller_state,
        COUNT(DISTINCT o.order_id) as transactions,
        ROUND(SUM(oi.price)::numeric, 2) as total_value,
        ROUND(AVG(o.delivery_time_days)::numeric, 2) as avg_delivery_days,
        CASE 
            WHEN c.customer_state = s.seller_state THEN 'Same State'
            ELSE 'Interstate'
        END as transaction_type
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN sellers s ON oi.seller_id = s.seller_id
    WHERE o.order_status = 'delivered'
        AND o.delivery_time_days IS NOT NULL
    GROUP BY c.customer_state, s.seller_state
    HAVING COUNT(DISTINCT o.order_id) >= 10
    ORDER BY total_value DESC
    LIMIT 10;
    """
    run_query(query1, "GEOGRAPHIC ANALYSIS: Interstate vs Same-State Commerce")
    
    # 5.2 Time Series - Monthly Trends
    query2 = """
    SELECT 
        DATE_TRUNC('month', o.order_purchase_timestamp) as month,
        COUNT(DISTINCT o.order_id) as orders,
        COUNT(DISTINCT o.customer_id) as customers,
        ROUND(SUM(oi.price + oi.freight_value)::numeric, 2) as revenue,
        ROUND(AVG(oi.price + oi.freight_value)::numeric, 2) as avg_order_value,
        ROUND(AVG(CASE WHEN or2.review_score IS NOT NULL THEN or2.review_score END)::numeric, 2) as avg_review_score
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN order_reviews or2 ON o.order_id = or2.order_id
    WHERE o.order_purchase_timestamp >= '2017-01-01'
    GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
    ORDER BY month;
    """
    run_query(query2, "TIME SERIES: Monthly Business Metrics")
    
    # 5.3 Product Performance with Reviews
    query3 = """
    SELECT 
        COALESCE(pct.product_category_name_english, 'Unknown') as category,
        COUNT(DISTINCT oi.product_id) as products_sold,
        COUNT(DISTINCT oi.order_id) as total_sales,
        ROUND(AVG(or2.review_score)::numeric, 2) as avg_review_score,
        ROUND(SUM(oi.price)::numeric, 2) as total_revenue,
        ROUND(AVG(oi.price)::numeric, 2) as avg_price,
        SUM(CASE WHEN or2.review_score >= 4 THEN 1 ELSE 0 END) as positive_reviews,
        ROUND(100.0 * SUM(CASE WHEN or2.review_score >= 4 THEN 1 ELSE 0 END) / COUNT(or2.review_score)::numeric, 2) as positive_review_rate
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    LEFT JOIN order_reviews or2 ON oi.order_id = or2.order_id
    GROUP BY pct.product_category_name_english
    HAVING COUNT(DISTINCT oi.order_id) >= 50
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    run_query(query3, "PRODUCT INSIGHTS: Category Performance with Customer Satisfaction")


def main():
    """Run all query demonstrations"""
    
    print("  SQL Query Analysis: Joins, Filtering, and Aggregations")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.close()
        print("Connected to database successfully\n")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running (Docker container)")
        print("  2. Database credentials are correct")
        print("  3. Database 'olist_ecommerce' exists and is populated")
        return
    
    query_joins()
    query_filtering()
    query_aggregations()
    query_advanced_techniques()
    query_business_insights()
    
if __name__ == "__main__":
    main()
