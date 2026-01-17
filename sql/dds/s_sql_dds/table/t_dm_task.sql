CREATE TABLE IF NOT EXISTS s_sql_dds.t_dm_task (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR NOT NULL,
    customer_name_id INT,
    product_category_id INT,
    product_name_id INT,
    status_id INT,
    quantity INT,
    unit_price NUMERIC,
    total_amount NUMERIC,
    order_date DATE,
    delivery_date DATE,
    load_ts TIMESTAMP
);
