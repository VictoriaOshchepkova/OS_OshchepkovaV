using System;
using System.Diagnostics;

class MatrixThreads
{
    private int[,] matrixA;
    private int[,] matrixB;
    private int[,] result;
    private int size;
    private int threadCount;

    public MatrixThreads(int size, int threadCount)
    {
        this.size = size;
        this.threadCount = threadCount;
        matrixA = new int[size, size];
        matrixB = new int[size, size];
        result = new int[size, size];
    }

    public void GenerateMatrices()
    {
        Random rand = new Random();
        for (int i = 0; i < size; i++)
        {
            for (int j = 0; j < size; j++)
            {
                matrixA[i, j] = rand.Next(1, 101);
                matrixB[i, j] = rand.Next(1, 101);
            }
        }
    }

    private void MultiplyPartial(int startRow, int endRow)
    {
        for (int i = startRow; i < endRow; i++)
        {
            for (int j = 0; j < size; j++)
            {
                int total = 0;
                for (int k = 0; k < size; k++)
                {
                    total += matrixA[i, k] * matrixB[k, j];
                }
                result[i, j] = total;
            }
        }
    }

    public double MultiplyWithThreads()
    {
        var threads = new List<Thread>();
        int rowsPerThread = size / threadCount;
        int extraRows = size % threadCount;

        int startRow = 0;
        
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        for (int i = 0; i < threadCount; i++)
        {
            int endRow = startRow + rowsPerThread;
            if (i < extraRows)
                endRow += 1;

            int localStart = startRow;
            int localEnd = endRow;

            Thread thread = new Thread(() => MultiplyPartial(localStart, localEnd));
            threads.Add(thread);
            thread.Start();

            startRow = endRow;
        }

        foreach (var thread in threads)
        {
            thread.Join();
        }

        stopwatch.Stop();
        return stopwatch.Elapsed.TotalSeconds;
    }

    public void PrintResult(int maxSize = 5)
    {
        Console.WriteLine("\nРезультат перемножения матриц (первые 5x5 элементов):");
        for (int i = 0; i < Math.Min(maxSize, size); i++)
        {
            for (int j = 0; j < Math.Min(maxSize, size); j++)
            {
                Console.Write(result[i, j] + "\t");
            }
            Console.WriteLine();
        }
    }
}

class Program
{
    static void Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.WriteLine("Usage: dotnet run <matrix_size> <thread_count>");
            return;
        }

        int size = int.Parse(args[0]);
        int threadCount = int.Parse(args[1]);

        Console.WriteLine($"Размер матриц: {size}x{size}");
        Console.WriteLine($"Количество потоков: {threadCount}");

        MatrixThreads multiplier = new MatrixThreads(size, threadCount);
        
        Console.WriteLine("Заполнение матриц числами...");
        multiplier.GenerateMatrices();

        Console.WriteLine("Перемножение матриц...");
        double elapsedTime = multiplier.MultiplyWithThreads();

        Console.WriteLine($"Время перемножения: {elapsedTime} секунд");

        multiplier.PrintResult();
    }
}