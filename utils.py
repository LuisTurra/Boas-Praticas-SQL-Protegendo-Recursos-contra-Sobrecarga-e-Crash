import time
import psutil
import duckdb
import pandas as pd

def measure_query(query: str) -> dict:
    process = psutil.Process()
    start_mem = process.memory_info().rss / (1024 ** 2) 
    start_time = time.perf_counter()

    try:
        result_df = duckdb.sql(query).df()
        error = None
    except Exception as e:
        result_df = pd.DataFrame()
        error = str(e)

    end_time = time.perf_counter()
    end_mem = process.memory_info().rss / (1024 ** 2)
    delta_mem = max(end_mem - start_mem, 0)

    return {
        "result": result_df,
        "tempo": end_time - start_time if error is None else None,
        "memoria_delta_mb": delta_mem if error is None else "CRASH/ERRO",
        "error": error
    }