from src.etl import ETLPipeline

def main():
    etl = ETLPipeline()
    etl.run_full_pipeline(1000)

if __name__ == "__main__":
    main()
