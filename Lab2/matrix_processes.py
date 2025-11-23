import argparse
import time
import random
import os
import sys

def generate_matrix(n):
    return [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]

def multiply_partial(start_row, end_row, matrix_a, matrix_b, n, result_pipe):
    partial_result = []
    
    for i in range(start_row, end_row):
        row = []
        for j in range(n):
            total = 0
            for k in range(n):
                total += matrix_a[i][k] * matrix_b[k][j]
            row.append(total)
        partial_result.append((i, row))
    
    os.write(result_pipe, str(partial_result).encode() + b'\n')
    os.close(result_pipe)
    sys.exit(0)

def multiply_with_process(n, matrix_a, matrix_b, processes_count):
    processes = []
    pipes = [] 
    
    rows_per_process = n // processes_count
    extra_rows = n % processes_count
    
    start_row = 0
    for i in range(processes_count):
        end_row = start_row + rows_per_process
        if i < extra_rows:
            end_row += 1
        
        parent_pipe, child_pipe = os.pipe()
        
        pid = os.fork()
        
        if pid == 0:
            os.close(parent_pipe)  
            multiply_partial(start_row, end_row, matrix_a, matrix_b, n, child_pipe)
        else:
            os.close(child_pipe) 
            processes.append(pid)
            pipes.append(parent_pipe)
        
        start_row = end_row
    
    result_matrix = [[0] * n for _ in range(n)]
    
    for pipe in pipes:
        data = b''
        while True:
            chunk = os.read(pipe, 4096)
            if not chunk:
                break
            data += chunk
        
        partial_result = eval(data.decode().strip())
        for row_idx, row_data in partial_result:
            result_matrix[row_idx] = row_data
        
        os.close(pipe)
    
    for pid in processes:
        os.waitpid(pid, 0)
    
    return result_matrix

def interface():
    parser = argparse.ArgumentParser()
    parser.add_argument('size', type=int)
    parser.add_argument('processes', type=int)
    
    args = parser.parse_args()
    
    print(f"Размер матриц: {args.size}x{args.size}")
    print(f"Количество процессов: {args.processes}")
    
    print("Заполнение матриц числами...")
    matrix_a = generate_matrix(args.size)
    matrix_b = generate_matrix(args.size)
    
    print("Перемножение матриц...")
    start_time = time.time()
    result = multiply_with_process(args.size, matrix_a, matrix_b, args.processes)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"Время перемножения: {execution_time} секунд")
    
    print("\nРезультат перемножения матриц (первые 5x5 элементов):")
    for i in range(min(5, args.size)):
        row = []
        for j in range(min(5, args.size)):
            row.append(str(result[i][j]))
        print(" ".join(row))

interface()