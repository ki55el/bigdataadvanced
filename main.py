from src.etl import ETLPipeline
from datetime import date
from src.fill_dm_table import run_full_pipeline

def main():
    etl = ETLPipeline()
    etl.run_full_pipeline(1000)

    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    run_full_pipeline(start_date, end_date)

if __name__ == "__main__":
    main()
