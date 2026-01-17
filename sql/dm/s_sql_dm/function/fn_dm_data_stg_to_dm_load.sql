create procedure fn_dm_data_stg_to_dm_load(
    p_start_dt date, 
    p_end_dt date
)
begin
    delete from t_dm_task 
    where order_date between p_start_dt and p_end_dt;
    
    insert into t_dm_task (
        order_id, 
        customer_id, customer_name,
        product_category_id, product_category,
        product_id, product_name,
        status_id, status_name,
        quantity, unit_price, total_amount, 
        order_date, delivery_date
    )
    select 
        order_id, 
        customer_id, customer_name,
        product_category_id, product_category,
        product_id, product_name,
        status_id, status_name,
        quantity, unit_price, total_amount, 
        order_date, delivery_date
    from t_dm_stg_task
    where order_date between p_start_dt and p_end_dt;
    
    truncate table t_dm_stg_task;
end
