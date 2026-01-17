drop table if exists t_dm_task;
create table t_dm_task (
    order_id varchar(255) primary key,
    customer_id int,
    customer_name varchar(100),
    product_category_id int,
    product_category varchar(50),
    product_id int,
    product_name varchar(100),
    status_id int,
    status_name varchar(20),
    quantity int,
    unit_price decimal(18,2),
    total_amount decimal(18,2),
    order_date date not null,
    delivery_date date,
    load_ts timestamp default current_timestamp
) engine=innodb default charset=utf8mb4 collate=utf8mb4_unicode_ci;

drop table if exists t_dm_stg_task;
create table t_dm_stg_task (
    order_id varchar(255),
    customer_id int,
    customer_name varchar(100),
    product_category_id int,
    product_category varchar(50),
    product_id int,
    product_name varchar(100),
    status_id int,
    status_name varchar(20),
    quantity int,
    unit_price decimal(18,2),
    total_amount decimal(18,2),
    order_date date,
    delivery_date date,
    load_ts timestamp default current_timestamp
) engine=innodb default charset=utf8mb4 collate=utf8mb4_unicode_ci;
