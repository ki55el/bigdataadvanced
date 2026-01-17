drop table if exists s_sql_dds.t_dim_product cascade;
create table s_sql_dds.t_dim_product (
    id serial primary key,
    product_name varchar(100) not null unique
);
