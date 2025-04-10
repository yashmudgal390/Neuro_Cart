-- Drop tables if they exist
DROP TABLE IF EXISTS customer_sessions;
DROP TABLE IF EXISTS event_logs;
DROP TABLE IF EXISTS customer_segments;
DROP TABLE IF EXISTS product_catalog;
DROP TABLE IF EXISTS product_embeddings;
DROP TABLE IF EXISTS recommendation_results;
DROP TABLE IF EXISTS optimization_summary;
DROP TABLE IF EXISTS reports;

-- Create customer_sessions table
CREATE TABLE IF NOT EXISTS customer_sessions (
    customer_id TEXT PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    location TEXT,
    interests TEXT,  -- JSON array of interests
    registration_date DATE,
    last_active DATE
);

-- Create event_logs table
CREATE TABLE IF NOT EXISTS event_logs (
    interaction_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    event_type TEXT,  -- view, click, add_to_cart, purchase
    timestamp DATETIME,
    dwell_time INTEGER,  -- in seconds
    FOREIGN KEY (customer_id) REFERENCES customer_sessions(customer_id),
    FOREIGN KEY (product_id) REFERENCES product_catalog(product_id)
);

-- Create customer_segments table
CREATE TABLE IF NOT EXISTS customer_segments (
    customer_id TEXT PRIMARY KEY,
    segment_tag TEXT,  -- premium, regular, new_user
    score REAL,  -- segmentation score
    FOREIGN KEY (customer_id) REFERENCES customer_sessions(customer_id)
);

-- Create product_catalog table
CREATE TABLE IF NOT EXISTS product_catalog (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    popularity INTEGER DEFAULT 0,
    stock INTEGER DEFAULT 0
);

-- Create product_embeddings table
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id TEXT PRIMARY KEY,
    vector_blob BLOB,  -- Binary vector data
    FOREIGN KEY (product_id) REFERENCES product_catalog(product_id)
);

-- Create recommendation_results table
CREATE TABLE IF NOT EXISTS recommendation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    recommendations TEXT,  -- JSON array of product IDs
    confidence_scores TEXT,  -- JSON array of scores
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_sessions(customer_id)
);

-- Create optimization_summary table
CREATE TABLE optimization_summary (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metrics_json TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT,
    data_blob TEXT,  -- JSON data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_event_logs_customer ON event_logs(customer_id);
CREATE INDEX idx_event_logs_session ON event_logs(customer_id);
CREATE INDEX idx_event_logs_product ON event_logs(product_id);
CREATE INDEX idx_customer_segments_tag ON customer_segments(segment_tag);
CREATE INDEX idx_product_catalog_category ON product_catalog(category);
CREATE INDEX idx_recommendation_results_customer ON recommendation_results(customer_id);
CREATE INDEX idx_reports_type ON reports(report_type); 