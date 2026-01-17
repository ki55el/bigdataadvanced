import json
import os

POSTGRES_CONFIG = json.loads(os.getenv('POSTGRES_CONFIG', '''
{
  "host": "host.docker.internal",
  "port": 5432,
  "database": "bda",
  "user": "postgres", 
  "password": "postgres"
}
'''))
