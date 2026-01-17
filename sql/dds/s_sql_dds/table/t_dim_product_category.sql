drop table if exists s_sql_dds.t_dim_product_category cascade;
create table s_sql_dds.t_dim_product_category (
    id serial primary key,
    category_name varchar(50) not null unique
);
