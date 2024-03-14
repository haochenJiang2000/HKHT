from numpy.random import choice
from tqdm import tqdm
import json
from collections import defaultdict
import argparse
from multiprocessing import Pool


def split_char(line):
    """
    将中文按照字分开，英文按照词分开
    :param line: 输入句子
    :return: 分词后的句子
    """
    english = "abcdefghijklmnopqrstuvwxyz0123456789"
    output = []
    buffer = ""
    for s in line:
        if s in english or s in english.upper():  # 英文或数字不分
            buffer += s
        else:  # 中文或标点分
            if buffer and buffer != " ":
                output.append(buffer)
            buffer = ""
            if s != " ":
                output.append(s)
    if buffer:
        output.append(buffer)
    return output


def _is_chinese_char(cp):
    """Checks whether CP is the codepoint of a CJK character."""

    if len(cp) > 1:
        return False
    cp = ord(cp)
    if ((0x4E00 <= cp <= 0x9FFF) or  #
            (0x3400 <= cp <= 0x4DBF) or  #
            (0x20000 <= cp <= 0x2A6DF) or  #
            (0x2A700 <= cp <= 0x2B73F) or  #
            (0x2B740 <= cp <= 0x2B81F) or  #
            (0x2B820 <= cp <= 0x2CEAF) or
            (0xF900 <= cp <= 0xFAFF) or  #
            (0x2F800 <= cp <= 0x2FA1F)):  #
        return True
    return False


def load_confusion_set():
    with open("data/confusion-set.txt_threshold0.7_supplement_by_qua.json", "r") as f:
        confusion_dic = json.load(f)
    return confusion_dic


def read_cilin():
    with open("data/jinyi_20", "r") as f:
        jinyi_dic = json.load(f)
    return jinyi_dic


def is_all_chinese(word):
    for ch in word:
        if not _is_chinese_char(ch):
            return False
    return True


def read_error_distribution(filename):
    with open(filename, "r") as f:
        append_dic, replace_dic, delete_dic = json.load(f)
    return append_dic, replace_dic, delete_dic


## 读取用于数据增强的各词表
# 混淆集 和 近义词
confusion_dic = load_confusion_set()
jinyi_dic = read_cilin()

# append,replace,delete 三种错误的分布，对应的词表
word_append_dic, word_replace_dic, word_delete_dic = read_error_distribution("data/error_distribution")

# 同音异形词
homophone_char = json.load(open("data/ChineseHomophones-master/chinese_homophone_char.txt_clean.json", "r"))
homophone_word = json.load(open("data/ChineseHomophones-master/chinese_homophone_word.txt_clean.json", "r"))

common_punct = list("，。！？；：、”“.（）《》…")


def inject(buffer):
    # TODO 标点符号针对性处理
    # 是否加入噪声
    whether_add_noise = choice(a=[0, 1], p=[0.5, 0.5], size=1, replace=False)[0]
    if whether_add_noise:
        return "".join(buffer)
    # 噪声数量
    add_noise_num = choice(a=[1, 2, 3], p=[0.8, 0.15, 0.05], size=1, replace=False)[0]
    for _ in range(add_noise_num):
        if not buffer:
            continue
        type = choice(a=[0, 1, 2, 3], p=[0.38, 0.20, 0.37, 0.05], size=1, replace=False)[0]  # 0-替换, 1-添加, 2-删除，3-词序
        if type == 0:
            level = choice(a=[0, 1], p=[0.0, 1.0], size=1, replace=False)[0]  # 0-词级别，1-字级别
        elif type == 1:
            level = choice(a=[0, 1], p=[0.0, 1.0], size=1, replace=False)[0]  # 0-词级别，1-字级别
        elif type == 2:
            level = choice(a=[0, 1], p=[0.3, 0.7], size=1, replace=False)[0]  # 0-字级别，1-标点级别
        else:
            level = choice(a=[0, 1], p=[0.0, 1.0], size=1, replace=False)[0]  # 0-词级别，1-字级别

        if type == 0:  # 替换
            if level == 0:
                x = choice(a=[0, 1], p=[1.0, 0.0], size=1, replace=False)[0]  # 0-同音词替换，1-近义词替换
                pos = choice(a=range(len(buffer)), size=1, replace=False)[0]
                if len(buffer[pos]) == 1 and buffer[pos] in common_punct:  # 标点错误
                    # new_punct = choice(a=common_punct, size=1, replace=False)[0]
                    # print("S\t" + buffer[pos] + "\t"+ new_punct)
                    # buffer[pos] = new_punct
                    del buffer[pos]
                else:
                    new_word = None
                    if x == 0:
                        if buffer[pos] in homophone_word.keys() and homophone_word[buffer[pos]]:
                            new_word = choice(a=homophone_word[buffer[pos]], size=1, replace=False)[0]
                    elif x == 1:
                        if is_all_chinese(buffer[pos]):  # 近义词替换
                            if buffer[pos] in jinyi_dic.keys():
                                new_word = choice(a=jinyi_dic[buffer[pos]], size=1, replace=False)[0]
                    if new_word and abs(len(new_word) - len(buffer[pos])) <= 1:
                        # print("S\t" + buffer[pos] + "\t"+ new_word)
                        buffer[pos] = new_word
            else:
                buffer = list("".join(buffer))
                pos = choice(a=range(len(buffer)), size=1, replace=False)[0]
                x = choice(a=[0, 1], p=[0.8, 0.2], size=1, replace=False)[0]  # 0-同音字替换，1-混淆集替换
                if len(buffer[pos]) == 1 and buffer[pos] in common_punct:  # 标点错误
                    # new_punct = choice(a=common_punct, size=1, replace=False)[0]
                    # print("S\t" + buffer[pos] + "\t"+ new_punct)
                    # buffer[pos] = new_punct
                    del buffer[pos]
                else:
                    new_char = None
                    if x == 0:
                        if buffer[pos] in homophone_char.keys() and homophone_char[buffer[pos]]:  # 拼写错误
                            new_char = choice(a=homophone_char[buffer[pos]], size=1, replace=False)[0]
                    else:
                        if buffer[pos] in confusion_dic.keys():  # 拼写错误
                            new_char = choice(a=confusion_dic[buffer[pos]], size=1, replace=False)[0]
                    if new_char:
                        # print("S\t" + buffer[pos] + "\t"+ new_char)
                        buffer[pos] = new_char

        elif type == 1:
            if level == 1:
                buffer = list("".join(buffer))
            pos = choice(a=range(len(buffer)), size=1, replace=False)[0]
            x = choice(a=[0, 1, 2], p=[0.2, 0.0, 0.8], size=1, replace=False)[0]  # 0-用分布采样，1-随机添加一个近义词, 2-重复当前token
            if is_all_chinese(buffer[pos]) or buffer[pos] in common_punct:
                new_word = buffer[pos]
                if x == 2:  # 重复当前词
                    new_word = buffer[pos]
                elif x == 0 and buffer[pos] in word_append_dic.keys():  # 从分布采样
                    new_word = \
                        choice(a=word_append_dic[buffer[pos]][0], p=word_append_dic[buffer[pos]][1], size=1,
                               replace=False)[0]
                elif buffer[pos] in jinyi_dic.keys():  # 添加当前词的近义词
                    new_word = choice(a=jinyi_dic[buffer[pos]], size=1, replace=False)[0]
                if new_word:
                    offset = choice(a=[-1, 0, 1, 2], p=[0.1, 0.2, 0.6, 0.1], size=1, replace=False)[0]
                    new_pos = pos + offset
                    if 0 <= new_pos <= len(buffer) and len(new_word) <= 2:
                        # print("R " + new_word)
                        buffer.insert(pos + offset, new_word)
        elif type == 2:
            buffer = list("".join(buffer))
            if level == 1:
                pos = choice(a=range(len(buffer)), size=1, replace=False)[0]
                del_num = choice(a=[1, 2, 3], p=[0.8, 0.2, 0.0], size=1, replace=False)[0]
                for _ in range(del_num):
                    if 0 <= pos < len(buffer) and (is_all_chinese(buffer[pos]) or buffer[pos] in common_punct):
                        # print("M " + buffer[pos])
                        del buffer[pos]
            else:
                for i in range(len(buffer) - 1, -1, -1):
                    if buffer[i] in common_punct:
                        del buffer[i]
        else:
            if level == 1:
                buffer = list("".join(buffer))
            x = choice(a=[0, 1], p=[0.5, 0.5], size=1, replace=False)[0]  # 0-交换，1-先删除再插入
            offset = choice(a=[-3, -2, -1, 1, 2, 3], p=[0.00, 0.1, 0.4, 0.4, 0.1, 0.00], size=1, replace=False)[0]
            pos = choice(a=range(len(buffer)), size=1, replace=False)[0]
            new_pos = pos + offset
            if x == 0 and 0 <= new_pos < len(buffer):
                buffer[new_pos], buffer[pos] = buffer[pos], buffer[new_pos]
            elif x == 1 and 0 <= new_pos <= len(buffer):
                tmp = buffer[pos]
                del buffer[pos]
                buffer.insert(new_pos, tmp)

    return "".join(buffer)


def generate_error(sent):
    words = sent.strip().split()
    iterval = 20
    result = ""
    buffer = []
    for word in words:
        buffer.append(word)
        if len(buffer) == iterval:
            result += inject(buffer)
            buffer = []
    if buffer:
        result += inject(buffer)
    return result + '\n'


def main(args):
    with open(args.src, "r") as f:
        with open(args.output, "w") as out:
            # with open(args.output + "_char", "w") as out_char:
            with Pool(64) as pool:
                for ret in pool.imap(generate_error, tqdm(f), chunksize=1024):
                    if ret:
                        out.write(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose input file to generate error.")
    parser.add_argument("-s", "--src",
                        default="/mnt/nas_alinlp/zuyi.bzy/zhangyue/MuCGEC2.0-data/wudao/WuDao_pretrain/wudao_all.shuf.txt.jieba.1000",
                        type=str, help="Input src file")
    parser.add_argument("-o", "--output",
                        default="/mnt/nas_alinlp/zuyi.bzy/zhangyue/MuCGEC2.0-data/wudao/WuDao_pretrain/wudao_all.shuf.txt.jieba.1000.da.v2",
                        type=str, help="Output file")
    args = parser.parse_args()
    main(args)
