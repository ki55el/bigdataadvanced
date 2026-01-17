CREATE OR REPLACE FUNCTION s_sql_dds.fn_dm_data_load(start_dt DATE, end_dt DATE)
RETURNS VOID AS $$
BEGIN
    DELETE FROM s_sql_dds.t_dm_task
    WHERE order_date BETWEEN start_dt AND end_dt;

    INSERT INTO s_sql_dds.t_dm_task (
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
    )
    SELECT
        src.order_id,
        src.customer_id,
        cn.id AS customer_name_id,
        pc.id AS product_category_id,
        pn.id AS product_name_id,
        st.id AS status_id,
        src.quantity,
        src.unit_price,
        src.total_amount,
        src.order_date,
        src.delivery_date,
        src.load_ts
    FROM s_sql_dds.t_sql_source_structured src
    LEFT JOIN s_sql_dds.d_customer_name cn ON src.customer_name = cn.name
    LEFT JOIN s_sql_dds.d_product_category pc ON src.product_category = pc.name
    LEFT JOIN s_sql_dds.d_product_name pn ON src.product_name = pn.name
    LEFT JOIN s_sql_dds.d_status st ON src.status = st.name
    WHERE src.order_date BETWEEN start_dt AND end_dt;
END;
$$ LANGUAGE plpgsql;
