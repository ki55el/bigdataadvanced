import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from config import POSTGRES_CONFIG, MYSQL_CONFIG, POSTGRES_SCHEMA, MYSQL_SCHEMA
from src.load_data_to_db import run_sql_file

BASE_DIR = Path(__file__).resolve().parent.parent

def setup_postgres_dwh():
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': POSTGRES_CONFIG['database'],
        'user': POSTGRES_CONFIG['user'],
        'password': POSTGRES_CONFIG['password']
    }

    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_string)

    print("Создание схемы s_sql_dds...")
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {POSTGRES_SCHEMA};"))
        conn.commit()

    print("Создание таблиц, функций и витрин в PostgreSQL...")
    with engine.connect() as conn:
        run_sql_file(conn, "sql/dds/s_sql_dds/table/t_dm_task.sql")
        run_sql_file(conn, "sql/dds/s_sql_dds/function/fn_dm_data_load.sql")
        run_sql_file(conn, "sql/dds/s_sql_dds/view/v_dm_task.sql")
    print("DWH в PostgreSQL настроена.")

def setup_mysql_dwh():
    import pymysql
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )
    cur = conn.cursor()

    cur.execute("CREATE SCHEMA IF NOT EXISTS s_sql_dm;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS s_sql_dm.t_dm_stg_task (
        order_id VARCHAR(255) PRIMARY KEY,
        customer_id VARCHAR(255) NOT NULL,
        customer_name_id INT,
        product_category_id INT,
        product_name_id INT,
        status_id INT,
        quantity INT,
        unit_price DECIMAL(15,2),
        total_amount DECIMAL(15,2),
        order_date DATE,
        delivery_date DATE,
        load_ts DATETIME
    );
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS s_sql_dm.t_dm_task LIKE s_sql_dm.t_dm_stg_task;")

    # Процедура
    cur.execute("DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load;")
    cur.execute("""
    CREATE PROCEDURE fn_dm_data_stg_to_dm_load(IN start_dt DATE, IN end_dt DATE)
    BEGIN
        DELETE FROM s_sql_dm.t_dm_task
        WHERE order_date BETWEEN start_dt AND end_dt;

        INSERT INTO s_sql_dm.t_dm_task
        SELECT * FROM s_sql_dm.t_dm_stg_task
        WHERE order_date BETWEEN start_dt AND end_dt;
    END
    """)

    conn.commit()
    cur.close()
    conn.close()

def create_dim_tables():
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': POSTGRES_CONFIG['database'],
        'user': POSTGRES_CONFIG['user'],
        'password': POSTGRES_CONFIG['password']
    }

    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_string)

    print("Создание справочников...")
    with engine.connect() as conn:
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {POSTGRES_SCHEMA}.d_customer_name (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );
        """))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {POSTGRES_SCHEMA}.d_product_category (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );
        """))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {POSTGRES_SCHEMA}.d_product_name (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );
        """))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {POSTGRES_SCHEMA}.d_status (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );
        """))

        conn.execute(text(f"""
        INSERT INTO {POSTGRES_SCHEMA}.d_customer_name (name)
        SELECT DISTINCT customer_name FROM {POSTGRES_SCHEMA}.t_sql_source_structured
        ON CONFLICT (name) DO NOTHING;
        """))
        conn.execute(text(f"""
        INSERT INTO {POSTGRES_SCHEMA}.d_product_category (name)
        SELECT DISTINCT product_category FROM {POSTGRES_SCHEMA}.t_sql_source_structured
        ON CONFLICT (name) DO NOTHING;
        """))
        conn.execute(text(f"""
        INSERT INTO {POSTGRES_SCHEMA}.d_product_name (name)
        SELECT DISTINCT product_name FROM {POSTGRES_SCHEMA}.t_sql_source_structured
        ON CONFLICT (name) DO NOTHING;
        """))
        conn.execute(text(f"""
        INSERT INTO {POSTGRES_SCHEMA}.d_status (name)
        SELECT DISTINCT status FROM {POSTGRES_SCHEMA}.t_sql_source_structured
        ON CONFLICT (name) DO NOTHING;
        """))
        conn.commit()
    print("Справочники созданы и заполнены.")

def fill_dm_table(start_dt, end_dt):
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': POSTGRES_CONFIG['database'],
        'user': POSTGRES_CONFIG['user'],
        'password': POSTGRES_CONFIG['password']
    }

    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_string)

    print(f"Загрузка данных в DM-таблицу за период {start_dt} - {end_dt}...")
    with engine.connect() as conn:
        conn.execute(
            text(f"SELECT {POSTGRES_SCHEMA}.fn_dm_data_load(:start_dt, :end_dt);"),
            {"start_dt": start_dt, "end_dt": end_dt}
        )
        conn.commit()
    print("Загрузка завершена.")

def transfer_to_mysql():
    pg_config = {
        'host': 'localhost',
        'port': 5432,
        'database': POSTGRES_CONFIG['database'],
        'user': POSTGRES_CONFIG['user'],
        'password': POSTGRES_CONFIG['password']
    }

    pg_conn_str = (
        f"postgresql://{pg_config['user']}:{pg_config['password']}"
        f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    )
    pg_engine = create_engine(pg_conn_str)

    df = pd.read_sql(f"SELECT * FROM {POSTGRES_SCHEMA}.v_dm_task", pg_engine)

    mysql_conn_str = (
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}"
        f"@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
    )
    mysql_engine = create_engine(mysql_conn_str)

    df.to_sql('t_dm_stg_task', con=mysql_engine, if_exists='replace', index=False)
    print("Данные переданы в MySQL staging.")

def load_to_mysql_dm(start_dt, end_dt):
    import pymysql
    transfer_to_mysql()

    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )
    with conn.cursor() as cur:
        cur.callproc('fn_dm_data_stg_to_dm_load', [start_dt, end_dt])
        conn.commit()
    conn.close()
    print("Данные загружены в MySQL DM.")

def run_full_pipeline(start_dt, end_dt):
    print("=== Запуск DWH ETL процесса ===")
    setup_postgres_dwh()
    setup_mysql_dwh()
    create_dim_tables()
    fill_dm_table(start_dt, end_dt)
    load_to_mysql_dm(start_dt, end_dt)
    print("=== DWH ETL процесс завершён ===")
