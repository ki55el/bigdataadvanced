CREATE OR REPLACE VIEW s_sql_dds.v_dm_task AS
SELECT
    order_id,
    customer_id,
    customer_name_id,
    product_category_id,
    product_name_id,
    status_id,
    quantity,
    unit_price,
    total_amount,
    order_date,
    delivery_date,
    load_ts
FROM s_sql_dds.t_dm_task;
