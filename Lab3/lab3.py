import os
import tempfile
import mmap
import time
import signal
import random

FILE_SIZE = 100 * 1024 * 1024 
NUM_RUNS = 5

def get_page_faults():
    try:
        with open('/proc/self/stat', 'r') as f:
            data = f.read()

        parts = data.split()
        
        return int(parts[11]), int(parts[9])
    except:
        return -1, -1

def load_pages(mm, size, page_size):
    sum = 0
    for byte in range(0, size, page_size):
        sum += mm[byte]
    return sum

def measure(mm, offset, half_size, page_size):
    maj_bef, min_bef = get_page_faults()
    t0 = time.perf_counter()
    s = load_pages(mm[offset:offset+half_size], half_size, page_size)
    t1 = time.perf_counter()
    maj_aft, min_aft = get_page_faults()
    return (t1 - t0), (maj_aft - maj_bef), (min_aft - min_bef), s

def fill_file(fd, size, page_size):
    os.lseek(fd, 0, os.SEEK_SET)
    chunk = bytearray(page_size)
    for i in range(page_size):
        chunk[i] = (random.getrandbits(8) or 1)

    written = 0
    while written < size:
        to_write = min(page_size, size - written)
        n = os.write(fd, chunk[:to_write])
        written += n
    os.fsync(fd)

def run(full, num_run):
    page_size = os.sysconf('SC_PAGE_SIZE')
    half_size = FILE_SIZE // 2

    fd, path = tempfile.mkstemp()
    try:
        os.ftruncate(fd, FILE_SIZE)

        fill_file(fd, FILE_SIZE, page_size)

        os.posix_fadvise(fd, 0, FILE_SIZE, 4)

        pid = os.fork()
        if pid == 0:
            sig_received = False

            def _handler(signum, frame):
                nonlocal sig_received
                sig_received = True

            signal.signal(signal.SIGUSR1, _handler)

            mm = mmap.mmap(fd, FILE_SIZE, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ)
            while not sig_received:
                signal.pause()

            t1, maj1, min1, s1 = measure(mm, 0, half_size, page_size)
            t2, maj2, min2, s2 = measure(mm, half_size, half_size, page_size)

            print(f"#{num_run}: первое обращение = {t1:.4f} сек (maj = {maj1}, min = {min1}), второе обращение = {t2:.4f} сек (maj = {maj2}, min = {min2})")

            mm.close()
            os._exit(0)
        else:
            mm = mmap.mmap(fd, FILE_SIZE, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ)

            if full:
                page_sum = load_pages(mm, FILE_SIZE, page_size)
            else:
                page_sum = load_pages(mm, half_size, page_size)

            os.kill(pid, signal.SIGUSR1)

            page_sum, status = os.waitpid(pid, 0)
            
            mm.close()

    finally:
        os.close(fd)
        os.unlink(path)

def main():
    print("Эксперимент №1")
    for i in range(NUM_RUNS):
        run(full=False, num_run=i+1)

    print("\nЭксперимент №2")
    for i in range(NUM_RUNS):
        run(full=True, num_run=i+1)

main()

