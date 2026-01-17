DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load;

CREATE PROCEDURE fn_dm_data_stg_to_dm_load(IN start_dt DATE, IN end_dt DATE)
BEGIN
    DELETE FROM s_sql_dm.t_dm_task
    WHERE order_date BETWEEN start_dt AND end_dt;

    INSERT INTO s_sql_dm.t_dm_task
    SELECT * FROM s_sql_dm.t_dm_stg_task
    WHERE order_date BETWEEN start_dt AND end_dt;
END
