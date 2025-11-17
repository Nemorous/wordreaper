import subprocess
import os
import platform
import sys
import time
import threading
from pathlib import Path
from tqdm import tqdm
import pkg_resources

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def count_lines(file_path):
    """Count the number of lines in a file efficiently"""
    line_count = 0
    with open(file_path, 'rb') as f:
        buf_size = 1024 * 1024
        buf = f.read(buf_size)
        while buf:
            line_count += buf.count(b'\n')
            buf = f.read(buf_size)
    return line_count


def progress_tracker(output_path, total_combinations, stop_event):
    """
    Track progress with tqdm, based on file growth.
    """
    try:
        start_time = time.time()
        last_size = 0
        pbar = tqdm(total=total_combinations, unit=" combos", colour="green")

        while not os.path.exists(output_path) and not stop_event.is_set():
            time.sleep(0.1)

        while not stop_event.is_set():
            if os.path.exists(output_path):
                current_size = os.path.getsize(output_path)
                # crude estimate: avg word length ~10 bytes + newline
                approx_combos = current_size // 11
                delta = approx_combos - last_size
                if delta > 0:
                    pbar.update(delta)
                last_size = approx_combos

                elapsed = time.time() - start_time
                pbar.set_description(f"{RED}{current_size / (1024 * 1024):.2f} MB{RESET}")
                pbar.set_postfix_str(f"Elapsed: {int(elapsed)}s")

            time.sleep(0.5)

        pbar.close()
    except Exception as e:
        print(f"\n{RED}Progress display error: {e}{RESET}")


def combinatorize(file1_path, file2_path, output_path=None, max_word_length=32, buffer_size=1000, silent=False):
    if not silent:
        print(f"Combining words from {file1_path} and {file2_path} using combinator...\n")

    binary_path = get_combinator_binary()
    if not binary_path:
        raise RuntimeError("Could not find combinator binary")

    if platform.system() != "Windows":
        try:
            os.chmod(binary_path, 0o755)
        except Exception as e:
            print(f"{RED}Warning:{RESET} Could not set executable permissions: {e}")

    if output_path:
        try:
            indicator_thread = None
            stop_event = threading.Event()

            if not silent:
                try:
                    with open(output_path, 'w', encoding='utf-8') as _:
                        pass

                    print("Calculating file sizes...\n")
                    file1_lines = count_lines(file1_path)
                    file2_lines = count_lines(file2_path)
                    total_combinations = file1_lines * file2_lines
                    print(f"Found {RED}{file1_lines:,}{RESET} words in first file and {RED}{file2_lines:,}{RESET} words in second file")
                    print(f"Expected combinations: {RED}{total_combinations:,}{RESET}")

                    indicator_thread = threading.Thread(
                        target=progress_tracker,
                        args=(output_path, total_combinations, stop_event)
                    )
                    indicator_thread.daemon = True
                    indicator_thread.start()
                except Exception as e:
                    print(f"{RED}Could not initialize progress tracking: {e}{RESET}")

            with open(output_path, 'w', encoding='utf-8') as outfile:
                process = subprocess.Popen(
                    [binary_path, file1_path, file2_path],
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True
                )
                _, stderr = process.communicate()

                if indicator_thread:
                    stop_event.set()
                    indicator_thread.join(timeout=1.0)

                if process.returncode != 0:
                    error_msg = stderr if stderr else "Unknown error"
                    raise RuntimeError(f"Combinator failed: {error_msg}")

            if not silent:
                print(f"\nCombinator completed successfully!")
        except Exception as e:
            if 'stop_event' in locals() and 'indicator_thread' in locals() and indicator_thread:
                stop_event.set()
                indicator_thread.join(timeout=1.0)
            print(f"{RED}Error running combinator: {str(e)}{RESET}")
            raise
    else:
        process = subprocess.Popen(
            [binary_path, file1_path, file2_path],
            stdout=sys.stdout,
            stderr=subprocess.PIPE,
            text=True
        )
        _, stderr = process.communicate()
        if process.returncode != 0:
            error_msg = stderr if stderr else "Unknown error"
            raise RuntimeError(f"Combinator failed: {error_msg}")


def get_combinator_binary():
    """Locate combinator binary packaged with word_reaper."""
    system = platform.system().lower()

    if system == 'windows':
        binary_name = 'combinator.exe'
    elif system in ['linux', 'darwin']:
        binary_name = 'combinator.bin' if system == 'linux' else 'combinator_macos'
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    try:
        bin_dir = pkg_resources.resource_filename("word_reaper", "bin")
        binary_path = os.path.join(bin_dir, binary_name)
        if os.path.exists(binary_path):
            return binary_path
    except Exception as e:
        print(f"{RED}Error locating combinator binary: {e}{RESET}")

    return None

