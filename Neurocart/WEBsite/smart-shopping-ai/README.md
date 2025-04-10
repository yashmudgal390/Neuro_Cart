# Smart Shopping AI

A multi-agent AI system for hyper-personalized product recommendations on an e-commerce platform. This system uses local LLMs (Ollama) and SQLite to deliver personalized product recommendations without requiring cloud services.

## Features

- **Multi-agent Architecture**: Specialized agents for data loading, customer segmentation, product catalog management, recommendations, optimization, and reporting
- **Hyper-personalized Recommendations**: Tailored product suggestions based on customer behavior and preferences
- **Customer Segmentation**: RFM and KMeans clustering to identify distinct customer segments
- **Product Embeddings**: Generate and store product embeddings for similarity search
- **Performance Tracking**: Monitor recommendation effectiveness and optimize strategies
- **Insights Dashboard**: Visualize key metrics and performance indicators

## Tech Stack

- **Python 3.10+**: Core programming language
- **Ollama**: Local LLM for embeddings and text processing
- **SQLite**: Local database for data storage
- **Flask**: Lightweight web API
- **Chart.js**: Data visualization
- **Bootstrap**: UI components

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smart-shopping-ai.git
   cd smart-shopping-ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Ollama (Windows):
   - Download from [Ollama's website](https://ollama.ai/download)
   - Follow the installation instructions
   - Pull the tinyllama model:
     ```
     ollama pull tinyllama
     ```

4. Initialize the database:
   ```
   python main.py --steps init_db
   ```

## Usage

### Running the Full Pipeline

To run the entire recommendation pipeline:

```
python main.py
```

This will:
1. Initialize the database
2. Load customer data
3. Segment customers
4. Process the product catalog
5. Generate recommendations
6. Optimize shopping strategies
7. Generate reports

### Running Specific Steps

You can run specific steps of the pipeline:

```
python main.py --steps init_db load_customers segment_customers
```

Available steps:
- `init_db`: Initialize the database
- `load_customers`: Load customer data from CSV
- `segment_customers`: Segment customers using RFM and KMeans
- `process_products`: Process product catalog and generate embeddings
- `generate_recommendations`: Generate personalized recommendations
- `optimize_shopping`: Optimize shopping strategies
- `generate_reports`: Generate insights and reports

### Web Interface

Start the Flask web server:

```
python app.py
```

Then open your browser to `http://localhost:5000` to access the web interface.

## Data Format

### Customer Data (customers.csv)
```
customer_id,age,gender,location,start_time
C001,32,F,New York,2023-01-15 10:30:00
C002,45,M,Los Angeles,2023-01-16 14:20:00
...
```

### Product Data (products.csv)
```
product_id,name,description,price,category,popularity,stock
P001,Wireless Headphones,High-quality wireless headphones,99.99,Electronics,0.85,50
P002,Running Shoes,Lightweight running shoes,79.99,Sports,0.72,30
...
```

### Event Logs (event_logs.csv) - Optional
```
session_id,category,dwell_time,event_type
S001,Electronics,120,view
S001,Electronics,45,click
S002,Sports,90,view
...
```

## Project Structure

```
smart-shopping-ai/
├── agents/
│   ├── customer_loader.py
│   ├── segmenter.py
│   ├── product_catalog.py
│   ├── recommendation_engine.py
│   ├── optimizer.py
│   └── reporter.py
├── database/
│   ├── schema.sql
│   ├── init_db.py
│   └── data.db
├── config/
│   ├── segment_rules.json
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── event_logs.csv
├── embeddings/
│   └── product_vectors.pkl
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── reports.css
│   └── js/
│       ├── main.js
│       ├── upload.js
│       ├── recommendations.js
│       ├── segments.js
│       └── reports.js
├── templates/
│   ├── index.html
│   ├── upload.html
│   ├── recommendations.html
│   ├── segments.html
│   └── reports.html
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## API Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/recommendations/<customer_id>`: Get personalized recommendations for a customer
- `GET /api/products/<product_id>`: Get product details
- `GET /api/segments`: Get customer segment distribution
- `GET /api/reports/latest`: Get the latest insights report
- `POST /api/track_event`: Track customer events (views, clicks, purchases)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 