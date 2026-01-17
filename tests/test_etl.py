import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.get_dataset import get_dataset
from src.load_data_to_db import load_data_to_db
from src.fill_structured_table import fill_structured_table
from src.etl import ETLPipeline
import pandas as pd
from unittest.mock import patch, MagicMock

def test_get_dataset():
    df = get_dataset(100)
    assert len(df) == 100
    assert len(df.columns) == 11
    assert df.isnull().sum().sum() > 0
    assert (df['unit_price'] < 0).sum() > 0

@patch('pandas.DataFrame.to_sql')
@patch('src.load_data_to_db.create_engine')
def test_load_data_to_db(mock_engine, mock_to_sql):
    df = get_dataset(10)
    mock_conn = MagicMock()
    mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
    
    load_data_to_db(df)

    mock_conn.execute.assert_called()
    mock_to_sql.assert_called_once()
    args, kwargs = mock_to_sql.call_args
    assert mock_to_sql.call_args.args[0] == "t_sql_source_unstructured"

@patch('src.fill_structured_table.create_engine')
@patch('src.fill_structured_table.run_sql_file')
def test_fill_structured_table(mock_run_sql, mock_engine):
    mock_conn = MagicMock()
    mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
    
    fill_structured_table()
    
    mock_run_sql.assert_any_call(mock_conn, "sql/dds/s_sql_dds/table/t_sql_source_structured.sql")
    mock_run_sql.assert_any_call(mock_conn, "sql/dds/s_sql_dds/function/fn_etl_data_clean.sql")
    found = any("fn_etl_data_clean" in str(call.args[0]) for call in mock_conn.execute.call_args_list)
    assert found, "SQL call for data cleaning not found"

@patch('src.etl.fill_structured_table')
@patch('src.etl.fill_dm_table')
@patch('src.etl.load_data_to_db')
@patch('src.etl.get_dataset') 
def test_etl_pipeline(mock_get_dataset, mock_load_db, mock_fill_dm, mock_fill_structured):
    mock_df = pd.DataFrame({'unit_price': [10, -5], 'other_col': [1, 2]})
    mock_get_dataset.return_value = mock_df
    
    from src.etl import ETLPipeline
    etl = ETLPipeline()
    etl.run_full_pipeline(50)
    
    mock_get_dataset.assert_called_once_with(50)
    mock_load_db.assert_called_once()
    mock_fill_structured.assert_called_once()
    mock_fill_dm.assert_called_once()
