drop table if exists s_sql_dds.t_sql_source_unstructured;
create table s_sql_dds.t_sql_source_unstructured (
    order_id varchar primary key,
    customer_id varchar,
    customer_name varchar,
    product_category varchar,
    product_name varchar,
    quantity numeric,
    unit_price numeric,
    total_amount numeric,
    order_date timestamp,
    delivery_date timestamp,
    status varchar,
    load_ts timestamp default current_timestamp
);
