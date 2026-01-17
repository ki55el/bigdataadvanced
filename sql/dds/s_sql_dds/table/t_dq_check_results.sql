DROP TABLE IF EXISTS s_sql_dds.t_dq_check_results CASCADE;

CREATE TABLE s_sql_dds.t_dq_check_results (
  check_id SERIAL PRIMARY KEY,
  check_type VARCHAR(255),
  table_name VARCHAR(255),
  column_name VARCHAR(255), 
  expected_value TEXT,
  actual_value TEXT,
  execution_date TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50),
  error_message TEXT
);

CREATE INDEX idx_dq_results_table_exec ON s_sql_dds.t_dq_check_results(table_name, execution_date DESC);
