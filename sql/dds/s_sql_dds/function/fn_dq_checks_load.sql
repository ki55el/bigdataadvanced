CREATE OR REPLACE FUNCTION s_sql_dds.fn_dq_checks_load(p_start_dt DATE DEFAULT CURRENT_DATE, p_end_dt DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    error_msg TEXT := '';
    source_sum NUMERIC;
    target_sum NUMERIC;
    source_count BIGINT;
    target_count BIGINT;
BEGIN

    RAISE NOTICE '=== Запуск проверок качества данных для % - % ===', p_start_dt, p_end_dt;

    -- Проверка 1: Полнота 
    INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, column_name, actual_value, execution_date, status, error_message)
    SELECT 
        'completeness',
        'v_dm_task',
        'order_id',
        COUNT(*)::TEXT,
        CURRENT_TIMESTAMP,
        CASE WHEN COUNT(*) = 0 THEN 'passed' ELSE 'failed' END,
        CASE WHEN COUNT(*) > 0 THEN 'Найдено ' || COUNT(*) || ' NULL значений в order_id' ELSE '' END
    FROM s_sql_dds.v_dm_task
    WHERE order_id IS NULL AND order_date BETWEEN p_start_dt AND p_end_dt;

    -- Проверка 2: Уникальность 
    INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, column_name, actual_value, execution_date, status, error_message)
    SELECT 
        'uniqueness',
        'v_dm_task',
        'order_id',
        COALESCE(dup_summary.total_duplicate_occurrences, '0'),
        CURRENT_TIMESTAMP,
        dup_summary.check_status,
        dup_summary.error_message
    FROM (
        SELECT 
            SUM(cnt) as total_duplicate_occurrences,
            CASE WHEN SUM(cnt) > 0 THEN 'failed' ELSE 'passed' END as check_status,
            CASE WHEN SUM(cnt) > 0 THEN 'Найдено ' || SUM(cnt) || ' дубликатов по order_id' ELSE '' END as error_message
        FROM (
            SELECT COUNT(*) as cnt
            FROM s_sql_dds.v_dm_task
            WHERE order_date BETWEEN p_start_dt AND p_end_dt
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) subquery_duplicates
    ) dup_summary; 

    -- Проверка 3: Валидность 
    INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, column_name, expected_value, actual_value, execution_date, status, error_message)
    SELECT 
        'validity',
        'v_dm_task',
        'status_name',
        '''new'', ''processed'', ''shipped'', ''cancelled''',
        string_agg(DISTINCT status_name, ', '),
        CURRENT_TIMESTAMP,
        CASE WHEN COUNT(*) = 0 THEN 'passed' ELSE 'failed' END,
        CASE WHEN COUNT(*) > 0 THEN 'Найдены недопустимые значения: ' || string_agg(DISTINCT status_name, ', ') ELSE '' END
    FROM s_sql_dds.v_dm_task
    WHERE status_name NOT IN ('new', 'processed', 'shipped', 'cancelled')
      AND order_date BETWEEN p_start_dt AND p_end_dt;

    -- Проверка 4: Правильность
    SELECT SUM(total_amount), COUNT(*) INTO source_sum, source_count
    FROM s_sql_dds.t_sql_source_structured
    WHERE order_date BETWEEN p_start_dt AND p_end_dt;

    SELECT SUM(total_amount), COUNT(*) INTO target_sum, target_count
    FROM s_sql_dds.v_dm_task
    WHERE order_date BETWEEN p_start_dt AND p_end_dt;

    INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, expected_value, actual_value, execution_date, status, error_message)
    VALUES (
        'correctness',
        't_sql_source_structured_vs_v_dm_task',
        'sum_total_amount=' || COALESCE(source_sum::TEXT, 'NULL') || ', count=' || COALESCE(source_count::TEXT, 'NULL'),
        'sum_total_amount=' || COALESCE(target_sum::TEXT, 'NULL') || ', count=' || COALESCE(target_count::TEXT, 'NULL'),
        CURRENT_TIMESTAMP,
        CASE WHEN source_sum = target_sum AND source_count = target_count THEN 'passed' ELSE 'failed' END,
        CASE 
            WHEN source_sum != target_sum THEN 'Суммы total_amount не совпадают: источник=' || COALESCE(source_sum::TEXT, 'NULL') || ', витрина=' || COALESCE(target_sum::TEXT, 'NULL')
            WHEN source_count != target_count THEN 'Количество записей не совпадает: источник=' || COALESCE(source_count::TEXT, 'NULL') || ', витрина=' || COALESCE(target_count::TEXT, 'NULL')
            ELSE ''
        END
    );

    -- Проверка 5: Непротиворечивость 
    INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, column_name, actual_value, execution_date, status, error_message)
    SELECT 
        'consistency',
        'v_dm_task',
        'unit_price',
        COUNT(*)::TEXT,
        CURRENT_TIMESTAMP,
        CASE WHEN COUNT(*) = 0 THEN 'passed' ELSE 'failed' END,
        CASE WHEN COUNT(*) > 0 THEN 'Нарушено бизнес-правило: найдено ' || COUNT(*) || ' записей с отрицательной unit_price' ELSE '' END
    FROM s_sql_dds.v_dm_task
    WHERE unit_price < 0 AND order_date BETWEEN p_start_dt AND p_end_dt;


    RAISE NOTICE '=== Проверки качества данных завершены ===';

EXCEPTION
    WHEN OTHERS THEN
        error_msg := SQLERRM;
        INSERT INTO s_sql_dds.t_dq_check_results (check_type, table_name, execution_date, status, error_message)
        VALUES ('general_error', 'ALL_CHECKED_TABLES', CURRENT_TIMESTAMP, 'error', error_msg);
        RAISE;
END;
$$ LANGUAGE plpgsql;
