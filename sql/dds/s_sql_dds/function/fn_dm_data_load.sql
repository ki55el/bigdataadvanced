create or replace function s_sql_dds.fn_dm_data_load(
    start_dt date, 
    end_dt date
)
returns void as $$
begin
    -- 1. Очистка t_dm_task за период
    delete from s_sql_dds.t_dm_task 
    where order_date between start_dt and end_dt;
    
    -- 2. Обновление справочников (on conflict do nothing)
    insert into s_sql_dds.t_dim_product_category (category_name)
    select distinct product_category 
    from s_sql_dds.t_sql_source_structured 
    where product_category is not null 
      and order_date between start_dt and end_dt
    on conflict (category_name) do nothing;
    
    insert into s_sql_dds.t_dim_status (status_name)
    select distinct status 
    from s_sql_dds.t_sql_source_structured 
    where status is not null 
      and order_date between start_dt and end_dt
    on conflict (status_name) do nothing;
    
    insert into s_sql_dds.t_dim_customer (customer_name)
    select distinct customer_name 
    from s_sql_dds.t_sql_source_structured 
    where customer_name is not null 
      and order_date between start_dt and end_dt
    on conflict (customer_name) do nothing;
    
    insert into s_sql_dds.t_dim_product (product_name)
    select distinct product_name 
    from s_sql_dds.t_sql_source_structured 
    where product_name is not null 
      and order_date between start_dt and end_dt
    on conflict (product_name) do nothing;
    
    -- 3. Заполнение t_dm_task
    insert into s_sql_dds.t_dm_task (
        order_id, 
        customer_id,
        product_category_id,
        product_id,
        status_id,
        quantity, unit_price, total_amount, 
        order_date, delivery_date
    )
    select 
        s.order_id,
        c.id as customer_id,
        pc.id as product_category_id,
        p.id as product_id,
        st.id as status_id,
        s.quantity, s.unit_price, s.total_amount,
        s.order_date, s.delivery_date
    from s_sql_dds.t_sql_source_structured s
    left join s_sql_dds.t_dim_customer c on s.customer_name = c.customer_name
    left join s_sql_dds.t_dim_product_category pc on s.product_category = pc.category_name
    left join s_sql_dds.t_dim_product p on s.product_name = p.product_name
    left join s_sql_dds.t_dim_status st on s.status = st.status_name
    where s.order_date between start_dt and end_dt;
end;
$$ language plpgsql;
