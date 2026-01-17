from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent))

from src.get_dataset import get_dataset
from src.load_data_to_db import load_data_to_db
from src.fill_structured_table import fill_structured_table
from src.fill_dm_table import fill_dm_table
from src.run_data_migration import run_data_migration
from src.run_dq_checks import run_dq_checks

class ETLPipeline:
    
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.stats = {
            'generated': 0,
            'loaded_unstructured': 0,
            'loaded_structured': 0,
            'anomalies_fixed': 0,
            'loaded_datamart': 0
        }
    
    def extract(self, rows: int = 1000):
        print("\nSTAGE 1: EXTRACT (Генерация грязных данных)")
        print("-" * 50)
        
        df = get_dataset(rows)
        print(f"Сгенерировано: {len(df)} строк")
        print(f"NULL аномалий: {df.isnull().sum().sum()}")
        print(f"Отрицательных цен: {(df['unit_price'] < 0).sum()}")
        
        self.stats['generated'] = len(df)
        return df
    
    def load_unstructured(self, df):
        print("\nSTAGE 2: LOAD (t_sql_source_unstructured)")
        print("-" * 50)
        
        load_data_to_db(df)
        self.stats['loaded_unstructured'] = len(df)
        print("Грязные данные загружены!")
    
    def transform_load(self):
        print("\nSTAGE 3: TRANSFORM + LOAD (t_sql_source_structured)")
        print("-" * 50)
        
        fill_structured_table()
        self.stats['loaded_structured'] = 1000
        print("Чистые данные готовы!")
    
    def data_mart_load(self, start_date=None, end_date=None):
        print("\nSTAGE 4: DATA MART (ЗВЕЗДА)")
        print("-" * 50)
        
        fill_dm_table(start_date, end_date)
        self.stats['loaded_datamart'] = 1000
        print("Data Mart (звезда) готов!")

    def export_to_mysql(self, start_date=None, end_date=None): 
        print("\nSTAGE 5: EXPORT (MYSQL VITRINE)")
        print("-" * 50)
        run_data_migration(start_date, end_date)
        print("Данные успешно экспортированы в MySQL!")

    def run_quality_checks(self):
        print("\nSTAGE 6: DATA QUALITY CHECKS")
        print("-" * 50)
        run_dq_checks()
        print("Проверки качества данных выполнены!")

    def run_full_pipeline(self, rows: int = 1000) -> dict:
        try:
            df = self.extract(rows)
            
            self.load_unstructured(df)
            
            self.transform_load()
            
            self.data_mart_load()

            self.export_to_mysql()

            self.run_quality_checks()

            self.print_final_stats()
            return self.stats
            
        except Exception as e:
            print(f"ETL ОШИБКА: {e}")
            raise
    
    def print_final_stats(self):
        print("\nDATA QUALITY ОТЧЁТ")
        print("=" * 40)
        print(f"Сгенерировано строк:        {self.stats['generated']}")
        print(f"Загружено грязных:         {self.stats['loaded_unstructured']}")
        print(f"Загружено чистых:          {self.stats['loaded_structured']}")
        print(f"Data Mart (звезда):         {self.stats.get('loaded_datamart', 0)}")

def main():
    etl = ETLPipeline()
    etl.run_full_pipeline(1000)

if __name__ == "__main__":
    main()
