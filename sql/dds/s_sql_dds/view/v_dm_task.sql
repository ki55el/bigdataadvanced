create or replace view s_sql_dds.v_dm_task as
select 
    t.order_id,
    t.customer_id, c.customer_name,
    t.product_category_id, pc.category_name as product_category,
    t.product_id, p.product_name,
    t.status_id, st.status_name,
    t.quantity, t.unit_price, t.total_amount,
    t.order_date, t.delivery_date
from s_sql_dds.t_dm_task t
left join s_sql_dds.t_dim_customer c on t.customer_id = c.id
left join s_sql_dds.t_dim_product_category pc on t.product_category_id = pc.id
left join s_sql_dds.t_dim_product p on t.product_id = p.id
left join s_sql_dds.t_dim_status st on t.status_id = st.id;
