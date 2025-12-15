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

> **Note:** Data exploration and basic visualizations available in `notebooks/` directory

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker Desktop
- Google Cloud account with Gemini API access

### Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start PostgreSQL database**
```bash
docker run --name olist-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=olist_ecommerce \
  -p 5432:5432 \
  -d postgres:latest

python database/database_setup.py
```

3. **Authenticate with Google Cloud**
```bash
gcloud auth application-default login
```

4. **Start MCP server** (in separate terminal)
```bash
cd postgres_mcp
./toolbox tools
```

5. **Run the agent api server**
```bash
adk api_server
```

6. **Run the Streamlit app**
```bash
streamlit run app.py
```

## 📁 Project Structure

```
AgenticProject/
├── agent/                          # AI agent configuration
│   ├── agent.py                    # Google ADK agent setup
│   ├── visualization_tools.py      # 7 chart generation tools
│   └── prompts/                    # Agent instructions
├── database/                       # Database setup scripts
├── datasets/                       # Raw CSV files (9 tables)
├── notebooks/                      # Data exploration & visualization
├── postgres_mcp/                   # MCP server for database access
│   ├── toolbox                     # MCP server executable
│   └── tools.yaml                  # Database connection config
├── viz_outputs/                    # Generated visualizations
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
