from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from src.load_data_to_db import run_sql_file


def run_dq_checks(start_date=None, end_date=None):

    if start_date is None:
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if end_date is None:
        from datetime import datetime
        end_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Запуск проверок качества данных за период: {start_date} → {end_date}")

    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )

    engine = create_engine(connection_string)

    with engine.connect() as conn:
        print("Создание таблицы результатов проверок качества данных...")
        run_sql_file(conn, "sql/dds/s_sql_dds/table/t_dq_check_results.sql")

        print("Создание функции fn_dq_checks_load...")
        run_sql_file(conn, "sql/dds/s_sql_dds/function/fn_dq_checks_load.sql")

        print("Выполнение проверок качества данных через fn_dq_checks_load...")
        conn.execute(
            text("SELECT s_sql_dds.fn_dq_checks_load(:start_dt, :end_dt);"),
            {"start_dt": start_date, "end_dt": end_date}
        )
        conn.commit()
        print("Проверки качества данных успешно запущены.")
