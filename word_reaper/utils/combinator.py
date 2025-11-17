from tqdm import tqdm

# ANSI red for the bar only
RED = '\033[91m'
RESET = '\033[0m'

def combinatorize(file1_path, file2_path, output_path=None, max_word_length=32, buffer_size=1000, silent=False, massive=False):
    with open(file1_path, "r", encoding="utf-8", errors="ignore") as f1:
        words1 = [line.strip().replace('\r', '') for line in f1 if len(line.strip()) <= max_word_length]

    total_lines = len(words1)
    progress = None
    if not massive:
        progress = tqdm(
            total=total_lines,
            desc="Combining",
            unit="word1",
            ncols=80,
            ascii=(" ", "#"),
            bar_format="{l_bar}" + RED + "{bar}" + RESET + "| {n_fmt}/{total_fmt} [{elapsed}]"
        )

    buffer = []
    out_file = open(output_path, "w", encoding="utf-8") if output_path else None

    try:
        for word1 in words1:
            with open(file2_path, "r", encoding="utf-8", errors="ignore") as f2:
                for line2 in f2:
                    word2 = line2.strip().replace('\r', '')
                    if len(word2) > max_word_length:
                        continue

                    combo = word1 + word2
                    buffer.append(combo)

                    if len(buffer) >= buffer_size:
                        flush_buffer(buffer, out_file)

            if progress:
                progress.update(1)

        flush_buffer(buffer, out_file)

    finally:
        if out_file:
            out_file.close()
        if progress:
            progress.close()

def flush_buffer(buffer, out_file):
    if out_file:
        out_file.write('\n'.join(buffer) + '\n')
    else:
        for line in buffer:
            print(line)
    buffer.clear()