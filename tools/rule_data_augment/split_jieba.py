import jieba
from tqdm import tqdm
from multiprocessing import Pool
import sys

def split_jieba(line):
    line = line.decode("utf-8", "ignore").rstrip('\n')
    # line = zhconv.convert(line.rstrip('\n'), 'zh-cn')
    words = jieba.lcut(line)
    return " ".join(words) + '\n'


if __name__ == '__main__':
    filename =sys.argv[1]
    out_file = sys.argv[2]
    with open(filename, 'rb') as f_in:
        with open(out_file, 'w', encoding='utf-8') as f_out:
            with Pool(60) as pool:
                for ret in pool.imap(split_jieba, tqdm(f_in), chunksize=1024):
                    if ret:
                        f_out.write(ret)