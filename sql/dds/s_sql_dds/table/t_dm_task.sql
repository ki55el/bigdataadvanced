drop table if exists s_sql_dds.t_dm_task cascade;
create table s_sql_dds.t_dm_task (
    order_id varchar primary key,
    customer_id int references s_sql_dds.t_dim_customer(id),
    product_category_id int references s_sql_dds.t_dim_product_category(id),
    product_id int references s_sql_dds.t_dim_product(id),
    status_id int references s_sql_dds.t_dim_status(id),
    quantity integer check (quantity > 0),
    unit_price numeric check (unit_price > 0),
    total_amount numeric check (total_amount > 0),
    order_date date not null,
    delivery_date date check (delivery_date >= order_date)
);
