# 📊 Olist E-commerce Data Analyzer

An AI-powered agent that analyzes Brazilian e-commerce data using natural language queries. Built with Google ADK (Gemini 2.5 Flash), PostgreSQL, and Model Context Protocol (MCP) for database access.

## 🎯 Features

- **Natural Language Queries** - Ask questions in plain English
- **SQL Execution** - Automatically generates and runs SQL queries via MCP
- **Advanced Visualizations** - Creates charts, heatmaps, histograms, and more
- **Interactive Chat UI** - Streamlit-based interface
- **Real-time Analysis** - Instant insights from 100K+ e-commerce transactions

## 📊 Dataset

**[Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)** - 100K orders from 2016-2018 across 9 tables:

- `olist_orders_dataset` - Order details and status
- `olist_order_items_dataset` - Items, prices, freight
- `olist_products_dataset` - Product catalog
- `olist_customers_dataset` - Customer demographics  
- `olist_sellers_dataset` - Seller information
- `olist_order_payments_dataset` - Payment methods and values
- `olist_order_reviews_dataset` - Customer ratings and reviews
- `olist_geolocation_dataset` - Geographic coordinates
- `product_category_name_translation` - Category translations

**Database Schema:**

![Database Schema](https://i.imgur.com/HRhd2Y0.png)

> **Note:** The `datasets/` folder already contains all CSV files from the dataset. If you want to download fresh data from Kaggle:
> 1. Download the [Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)
> 2. Remove all CSV files from the `datasets/` folder
> 3. Place the downloaded CSV files in the `datasets/` folder
> 4. Run `notebooks/data_exploration.ipynb` to process and clean the data
> 5. Run `python database/database_setup.py` to upload to database

### 📂 Additional Resources

- **`database/database_setup.py`** - Complete database setup script (creates tables, loads data)
- **`database/sql_demonstrations.py`** - SQL query examples demonstrating joins, filtering, and aggregations
- **`notebooks/data_exploration.ipynb`** - Data cleaning and preprocessing pipeline
- **`notebooks/data_visualization.ipynb`** - Exploratory data analysis with visualizations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- `.env` file with Gemini API key and database credentials (included in project)

### Setup

#### Option 1: Run with Pre-loaded Database (Recommended)

The database is already deployed on Heroku with all data loaded. Simply run the application:

1. **Activate virtual environment** (included in project)
```bash
source .venv/bin/activate
```

2. **Start MCP server** (in separate terminal)
```bash
cd postgres_mcp
./toolbox tools
```

3. **Run the agent API server** (in separate terminal)
```bash
adk api_server
```

4. **Run the Streamlit app** (in separate terminal)
```bash
streamlit run app.py
```

#### Option 2: Process Data from Scratch

If you want to see the full data processing pipeline:

1. **Activate virtual environment**
```bash
source .venv/bin/activate
```

2. **Run data processing notebook**
   - Open `notebooks/data_exploration.ipynb`
   - Run all cells to clean and process the raw CSV files
   - This will generate processed CSV files in `datasets/` directory

3. **Continue with steps 2-5 from Option 1**

#### Option 3: Reload Database (Optional)

If you need to reset the database (⚠️ **This will drop all existing tables**):

1. **Activate virtual environment**
```bash
source .venv/bin/activate
```

2. **Run database setup script**
```bash
python database/database_setup.py
```
   - Database credentials are in `.env` file
   - Database is hosted on Heroku
   - Script will drop existing tables, recreate schema, and upload data from processed CSV files

3. **Continue with steps 2-5 from Option 1**

> **Note:** If `.venv` is not working, first run:
> ```bash
> pip install -r requirements.txt
> ```

## 📁 Project Structure

```
AgenticProject/
├── agent/                          # AI agent configuration
│   ├── agent.py                    # Google ADK agent setup
│   ├── visualization_tools.py      # 7 chart generation tools
│   └── prompts/                    # Agent instructions
├── database/                       # Database scripts
│   ├── database_setup.py           # Complete DB setup (creates tables, loads data)
│   └── sql_demonstrations.py       # SQL examples (joins, filtering, aggregations)
├── datasets/                       # CSV files (9 raw + 5 cleaned tables)
├── notebooks/                      # Data analysis notebooks
│   ├── data_exploration.ipynb      # Data cleaning & preprocessing pipeline
│   └── data_visualization.ipynb    # Exploratory data analysis with charts
├── postgres_mcp/                   # MCP server for database access
│   ├── toolbox                     # MCP server executable
│   └── tools.yaml                  # Database connection config
├── viz_outputs/                    # Generated visualizations
├── .env                            # Gemini API key & database credentials
└── app.py                          # Streamlit UI
```

## 📝 Example Queries

```python
# In the Streamlit app, try:
"Show me the top 10 customers by total spending"
"Create a line chart showing monthly order trends for 2017"
"What's the average review score for each product category?"
"Visualize payment method distribution with a pie chart"
```
