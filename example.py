import time

def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Функция {func.__name__} выполнена за {end_time - start_time:.4f} секунд.")
        return result
    return wrapper

@log_execution_time
def calculate():
    time.sleep(2)  # имитация длительной операции
    print("Вычисления завершены.")

calculate()
