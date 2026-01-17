drop table if exists s_sql_dds.t_dim_status cascade;
create table s_sql_dds.t_dim_status (
    id serial primary key,
    status_name varchar(20) not null unique
);
