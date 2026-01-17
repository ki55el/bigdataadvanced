import json
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_CONFIG = {
  "host":     os.getenv('POSTGRES_HOST', 'big-data-postgres'),
  "port":     int(os.getenv('POSTGRES_PORT', 5432)),
  "database": os.getenv('POSTGRES_DB', 'bda'),
  "user":     os.getenv('POSTGRES_USER', 'postgres'),
  "password": os.getenv('POSTGRES_PASSWORD', 'postgres')
}

MYSQL_CONFIG = {
  "host":     os.getenv('MYSQL_HOST', 'big-data-mysql'),
  "port":     int(os.getenv('MYSQL_PORT', 3306)),
  "database": os.getenv('MYSQL_DB', 'bda'),
  "user":     os.getenv('MYSQL_USER', 'root'),
  "password": os.getenv('MYSQL_PASSWORD', 'root')
}
