drop table if exists s_sql_dds.t_dim_customer cascade;
create table s_sql_dds.t_dim_customer (
    id serial primary key,
    customer_name varchar(100) not null unique
);
