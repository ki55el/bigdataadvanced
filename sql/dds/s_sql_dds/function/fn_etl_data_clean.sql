CREATE OR REPLACE FUNCTION s_sql_dds.fn_etl_data_clean()
RETURNS void AS $$
BEGIN
    TRUNCATE s_sql_dds.t_sql_source_structured;
    
    INSERT INTO s_sql_dds.t_sql_source_structured
    SELECT 
        order_id,
        
        COALESCE(NULLIF(trim(customer_id),''), 'UNKNOWN_'||order_id) as customer_id,
        COALESCE(NULLIF(trim(customer_name),''), 'Неизвестный клиент') as customer_name,
        COALESCE(NULLIF(trim(product_category),''), 'Unknown') as product_category,
        COALESCE(NULLIF(trim(product_name),''), 'Неизвестный товар') as product_name,
        
        GREATEST(1, ABS(quantity::int)) as quantity,
        
        GREATEST(0.01, ABS(unit_price)) as unit_price,
        
        GREATEST(0.01, ABS(quantity::int) * ABS(unit_price)) as total_amount,
        
        COALESCE(order_date, NOW())::date as order_date,
        GREATEST(
            COALESCE(delivery_date::date, NOW()::date),
            COALESCE(order_date::date, NOW()::date) + INTERVAL '1 day'
        ) as delivery_date,
        
        CASE 
            WHEN LOWER(trim(status)) IN ('new','processed','shipped') 
            THEN LOWER(trim(status))
            ELSE 'new'
        END as status,
        
        NOW() as load_ts
        
    FROM s_sql_dds.t_sql_source_unstructured;
    
    RAISE NOTICE 'ETL завершён: % грязных → % чистых строк', 
        (SELECT COUNT(*) FROM s_sql_dds.t_sql_source_unstructured),
        (SELECT COUNT(*) FROM s_sql_dds.t_sql_source_structured);
END;
$$ LANGUAGE plpgsql;
