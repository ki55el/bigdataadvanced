import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config import POSTGRES_CONFIG

@st.cache_resource
def get_db_engine():
    """Создает и кэширует SQLAlchemy движок."""
    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    return create_engine(connection_string)

@st.cache_data(ttl=600)
def load_dq_results():
    engine = get_db_engine()
    query = """
    SELECT check_id, check_type, table_name, column_name, execution_date, status, error_message
    FROM s_sql_dds.t_dq_check_results
    ORDER BY execution_date DESC
    LIMIT 100; -- Ограничиваем количество строк для отображения
    """
    df = pd.read_sql_query(query, engine)
    return df

st.title("Мониторинг Качества Данных")

df = load_dq_results()

if df.empty:
    st.info("Результаты проверок качества данных пока отсутствуют.")
else:
    latest_run = df['execution_date'].max()
    st.subheader(f"Последний запуск проверок: {latest_run.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    
    status_counts = df['status'].value_counts()
    st.bar_chart(status_counts)

    st.subheader("Детали проверок")
    st.dataframe(df[['check_type', 'table_name', 'column_name', 'status', 'error_message', 'execution_date']])

    st.subheader("Фильтр по статусу")
    all_available_statuses = df['status'].unique()

    default_statuses_for_filter = [status for status in ['failed', 'error'] if status in all_available_statuses]
    selected_statuses = st.multiselect("Выберите статусы", options=all_available_statuses, default=default_statuses_for_filter)

    filtered_df = df[df['status'].isin(selected_statuses)]
    st.dataframe(filtered_df[['check_type', 'table_name', 'status', 'error_message', 'execution_date']])


    errors_df = df[df['status'] == 'error']
    failures_df = df[df['status'] == 'failed']
    
    if not errors_df.empty:
        st.error(f"Найдено {len(errors_df)} критических ошибок (error)!")
        st.write(errors_df[['check_type', 'table_name', 'error_message']])
        
    if not failures_df.empty:
        st.warning(f"Найдено {len(failures_df)} проваленных проверок (failed)!")
        st.write(failures_df[['check_type', 'table_name', 'error_message']])
