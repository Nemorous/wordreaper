from tqdm import tqdm

# ANSI red for bar only
RED = '\033[91m'
RESET = '\033[0m'

def merge_files(file_list, silent=False):
    all_words = set()

    for filename in tqdm(
        file_list,
        desc="Merging files",
        unit="file",
        ncols=80,
        ascii=(" ", "#"),
        bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]",
        disable=silent
    ):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned:
                        all_words.add(cleaned)
        except FileNotFoundError:
            print(f"[!] File not found: {filename}")

    return sorted(all_words)