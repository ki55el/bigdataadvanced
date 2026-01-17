CREATE TABLE IF NOT EXISTS s_sql_dm.t_dm_stg_task (
    order_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    customer_name_id INT,
    product_category_id INT,
    product_name_id INT,
    status_id INT,
    quantity INT,
    unit_price DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    order_date DATE,
    delivery_date DATE,
    load_ts DATETIME
);
