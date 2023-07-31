import os
import argparse
import signal
import time
from multiprocessing import Pool, cpu_count

def get_total_folder_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return start_path, total_size

def print_size(result):
    path, total_size = result
    human_readable = ""

    # total_size is in bytes, convert it to human readable format
    if total_size < 1024:
        human_readable = "{} bytes".format(total_size)
    elif total_size < 1024**2:
        human_readable = "{:.2f} KB".format(total_size/1024)
    elif total_size < 1024**3:
        human_readable = "{:.2f} MB".format(total_size/1024**2)
    else:
        human_readable = "{:.2f} GB".format(total_size/1024**3)

    print("Total size of '{}': {} | {} bytes".format(path, human_readable, total_size))


def main():
    parser = argparse.ArgumentParser(description="Calculate size of all folders inside a folder.")
    parser.add_argument('folder_path', type=str, help="The root folder path")
    args = parser.parse_args()

    folder_path = args.folder_path
    subfolders = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(processes=cpu_count())
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        for subfolder in subfolders:
            pool.apply_async(get_total_folder_size, (subfolder,), callback=print_size)
        pool.close()
        while len(pool._cache) > 0:  # while there are tasks not finished
            time.sleep(0.1)  # wait for 100ms
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        print("Closing pool")
        pool.join()

if __name__ == "__main__":
    main()
