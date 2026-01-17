import json
import os

POSTGRES_CONFIG = json.loads(os.getenv('POSTGRES_CONFIG', '''
{
  "host": "localhost",
  "port": 5432,
  "database": "postgres",
  "user": "postgres",
  "password": "postgres"
}
'''))

MYSQL_CONFIG = json.loads(os.getenv('MYSQL_CONFIG', '''
{
  "host": "localhost",
  "port": 3306,
  "database": "sys",
  "user": "root",
  "password": "mysql"
}
'''))

POSTGRES_SCHEMA = os.getenv('POSTGRES_SCHEMA', 's_sql_dds')
MYSQL_SCHEMA = os.getenv('MYSQL_SCHEMA', 's_sql_dm')
