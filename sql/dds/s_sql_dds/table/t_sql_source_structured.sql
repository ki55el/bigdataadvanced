drop table if exists s_sql_dds.t_sql_source_structured;
create table s_sql_dds.t_sql_source_structured (
    order_id varchar primary key,
    customer_id varchar not null,
    customer_name varchar not null,
    product_category varchar not null,
    product_name varchar not null,
    quantity integer check (quantity > 0),
    unit_price numeric check (unit_price > 0),
    total_amount numeric check (total_amount > 0),
    order_date date not null,
    delivery_date date check (delivery_date >= order_date),
    status varchar check (status in ('new', 'processed', 'shipped', 'cancelled')),
    load_ts timestamp default current_timestamp
);
