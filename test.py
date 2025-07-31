import requests
import json
from typing import Dict, Any

# API endpoint
API_URL = "http://localhost:8000/generate-sql"

# Complex e-commerce database schema
COMPLEX_SCHEMA = """
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    phone VARCHAR(20),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    account_status ENUM('active', 'suspended', 'deleted') DEFAULT 'active',
    loyalty_points INT DEFAULT 0
);

CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT,
    brand VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    weight DECIMAL(8,2),
    dimensions VARCHAR(50),
    description TEXT,
    sku VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ship_date TIMESTAMP,
    delivery_date TIMESTAMP,
    order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned') DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(8,2),
    discount_amount DECIMAL(10,2) DEFAULT 0,
    payment_method ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash_on_delivery'),
    shipping_address_id INT,
    billing_address_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE addresses (
    address_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    address_type ENUM('shipping', 'billing', 'both') DEFAULT 'both',
    street_address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE reviews (
    review_id INT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_votes INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE inventory_movements (
    movement_id INT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type ENUM('purchase', 'sale', 'adjustment', 'return') NOT NULL,
    quantity_change INT NOT NULL,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference_order_id INT,
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (reference_order_id) REFERENCES orders(order_id)
);

CREATE TABLE coupons (
    coupon_id INT PRIMARY KEY,
    coupon_code VARCHAR(50) UNIQUE NOT NULL,
    discount_type ENUM('percentage', 'fixed_amount') NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    minimum_order_amount DECIMAL(10,2),
    maximum_discount DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    usage_limit INT,
    used_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_coupon_usage (
    usage_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    order_id INT NOT NULL,
    usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discount_applied DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
"""

# Complex test queries
COMPLEX_QUERIES = [
    {
        "name": "Monthly Revenue Analysis with Growth",
        "question": "Calculate monthly revenue for the last 12 months, including month-over-month growth percentage, average order value, and total number of orders, only for completed orders (delivered status)"
    },
    {
        "name": "Customer Lifetime Value Analysis",
        "question": "Find the top 10 customers by lifetime value, showing their total spent, number of orders, average order value, first order date, last order date, and loyalty points. Include only active customers who have made at least 3 orders."
    },
    {
        "name": "Product Performance with Inventory",
        "question": "Show products with their total revenue, units sold, average rating, review count, current stock, and profit margin (price - cost). Include category name and brand. Filter for products that have been sold at least 10 times and have a rating above 3.5."
    },
    {
        "name": "Advanced Customer Segmentation",
        "question": "Segment customers into 'High Value' (>$1000 total spent), 'Medium Value' ($200-$1000), and 'Low Value' (<$200). For each segment, show count of customers, average order frequency, most popular category, and average time between orders."
    },
    {
        "name": "Inventory Turnover Analysis",
        "question": "Calculate inventory turnover ratio for each product category in the last 6 months. Show category name, total units sold, average inventory level, turnover ratio, and identify slow-moving products (turnover < 2)."
    },
    {
        "name": "Coupon Effectiveness Analysis",
        "question": "Analyze coupon performance by showing coupon code, total usage, total discount given, average order value with and without coupon, conversion rate, and ROI. Include only coupons used at least 10 times in the last year."
    },
    {
        "name": "Geographic Sales Analysis",
        "question": "Show sales performance by state/region including total revenue, number of orders, number of unique customers, average order value, and top-selling product category for each state. Rank states by total revenue."
    },
    {
        "name": "Seasonal Trends Analysis",
        "question": "Analyze seasonal buying patterns by showing monthly sales trends for each product category over the last 2 years. Include percentage change from previous year for the same month and identify the peak season for each category."
    },
    {
        "name": "Customer Churn Prediction Data",
        "question": "Identify customers at risk of churning by finding active customers who haven't placed an order in the last 90 days but were previously active (had at least 2 orders). Show their last order date, total lifetime value, average days between orders, and preferred categories."
    },
    {
        "name": "Advanced Profitability Analysis",
        "question": "Create a comprehensive profitability report showing revenue, COGS (cost of goods sold), gross profit, shipping costs, discount amounts, and net profit by month and product category. Include profit margins and identify the most and least profitable categories."
    }
]

def test_sql_generation(schema: str, question: str, query_name: str) -> Dict[str, Any]:
    """Test the SQL generation endpoint with a complex query."""
    
    payload = {
        "schema": schema,
        "question": question
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "query_name": query_name,
                "question": question,
                "generated_sql": result.get("sql_query", ""),
                "response_time": response.elapsed.total_seconds()
            }
        else:
            return {
                "success": False,
                "query_name": query_name,
                "question": question,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": response.elapsed.total_seconds()
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "query_name": query_name,
            "question": question,
            "error": f"Request failed: {str(e)}",
            "response_time": None
        }

def run_comprehensive_test():
    """Run all complex query tests."""
    
    print("🚀 Starting Complex SQL Generator API Tests")
    print("=" * 80)
    print(f"Testing endpoint: {API_URL}")
    print(f"Schema complexity: {len(COMPLEX_SCHEMA.split('CREATE TABLE'))-1} tables")
    print(f"Number of test queries: {len(COMPLEX_QUERIES)}")
    print("=" * 80)
    
    results = []
    
    for i, query_test in enumerate(COMPLEX_QUERIES, 1):
        print(f"\n📊 Test {i}/{len(COMPLEX_QUERIES)}: {query_test['name']}")
        print("-" * 50)
        print(f"Question: {query_test['question'][:100]}...")
        
        result = test_sql_generation(
            COMPLEX_SCHEMA, 
            query_test['question'], 
            query_test['name']
        )
        
        results.append(result)
        
        if result['success']:
            print(f"✅ SUCCESS - Response time: {result['response_time']:.2f}s")
            print(f"Generated SQL (first 200 chars): {result['generated_sql'][:200]}...")
        else:
            print(f"❌ FAILED - {result['error']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average response time: {avg_response_time:.2f}s")
        
        print(f"🚀 Fastest query: {min(successful_tests, key=lambda x: x['response_time'])['query_name']} "
              f"({min(r['response_time'] for r in successful_tests):.2f}s)")
        print(f"🐌 Slowest query: {max(successful_tests, key=lambda x: x['response_time'])['query_name']} "
              f"({max(r['response_time'] for r in successful_tests):.2f}s)")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failed in failed_tests:
            print(f"   - {failed['query_name']}: {failed['error']}")
    
    # Save detailed results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to 'test_results.json'")
    
    return results

if __name__ == "__main__":
    # Check if API is running
    try:
        health_check = requests.get("http://localhost:8000/docs", timeout=5)
        if health_check.status_code == 200:
            print("🟢 API is running and accessible")
        else:
            print("🟡 API responded but may have issues")
    except requests.exceptions.RequestException:
        print("🔴 WARNING: Cannot connect to API. Make sure it's running on localhost:8000")
        print("Start your API with: python app.py")
        exit(1)
    
    # Run the tests
    results = run_comprehensive_test()