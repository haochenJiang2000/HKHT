# -*- coding: utf-8 -*-

from tqdm import tqdm
import re

from supar.structs.fn import levenshtein

def split_sentence(document: str, flag: str = "all", limit: int = 510):
    """
    Args:
        document:
        flag: Type:str, "all" 中英文标点分句，"zh" 中文标点分句，"en" 英文标点分句
        limit: 默认单句最大长度为510个字符
    Returns: Type:list
    """
    sent_list = []
    try:
        if flag == "zh":
            document = re.sub('(?P<quotation_mark>([。？！](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 单字符断句符
            document = re.sub('(?P<quotation_mark>([。？！])[”’"\'])', r'\g<quotation_mark>\n', document)  # 特殊引号
        elif flag == "en":
            document = re.sub('(?P<quotation_mark>([.?!](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 英文单字符断句符
            document = re.sub('(?P<quotation_mark>([?!.]["\']))', r'\g<quotation_mark>\n', document)  # 特殊引号
        else:
            document = re.sub('(?P<quotation_mark>([。？！….?!](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 单字符断句符
            document = re.sub('(?P<quotation_mark>(([。？！.!?]|…{1,2})[”’"\']))', r'\g<quotation_mark>\n',
                              document)  # 特殊引号

        sent_list_ori = document.splitlines()
        for sent in sent_list_ori:
            sent = sent.strip()
            if not sent:
                continue
            else:
                while len(sent) > limit:
                    temp = sent[0:limit]
                    sent_list.append(temp)
                    sent = sent[limit:]
                sent_list.append(sent)
    except:
        sent_list.clear()
        sent_list.append(document)
    return sent_list


def align(src, tgt):
    _, alignments = levenshtein(src, tgt, (1, 1, 1), True)
    prev = alignments[0]
    edits = []
    for i, j in alignments[1:]:
        if i > prev[0] and j == prev[1]:
            edits.append('D')
        elif i == prev[0] and j > prev[1]:
            edits.append('I')
        elif i > prev[0] and j > prev[1]:
            edits.append('K' if src[i-1] == tgt[j-1] else 'S')
        prev = (i, j)
    return ''.join(edits).replace('K', 'K  ').replace('D', 'D  ').replace('S', 'S  ')


def extract(data, edit=None):
    edit = edit or f"{data}.lev"
    with open(data, encoding="utf-8") as fd, open(edit, 'w') as fe:
        data = [line for line in fd.read().split("\n") if line]
        for line in data:
            try:
                src, tgt = line.split("\t")
            except Exception:
                continue
            src = src.replace(" ", "")
            tgt = tgt.replace(" ", "")
            edits = align(src, tgt)
            fe.write(f"{src}\n{tgt}\n{edits}\n\n")


def data_clean(para_path, result_path):
    with open(para_path, "r", encoding="utf-8") as f1:
        data = [line.split("\t") for line in f1.read().split("\n") if line]
        clean_data = []
        count0 = 0
        count1 = 0
        for id, src, tgt in data:
            # 重新分句
            src_list = split_sentence(src, flag="zh", limit=200)
            tgt_list = split_sentence(tgt, flag="zh", limit=200)

            if len(src_list) != len(tgt_list):
                src_list = [src]
                tgt_list = [tgt]

            for src, tgt in zip(src_list, tgt_list):

                if len(src) < 10 or len(tgt) < 10:
                    continue

                # 长度差异过大的需要清洗，处理tgt
                if abs(len(tgt)-len(src)) > len(src)/2:
                    # tgt 过短的直接筛掉
                    if len(tgt) < len(src):
                        continue
                    # tgt过长，则在长度差5以内找到一个结尾标点，截断作为tgt
                    start = max(0, len(src)-min(5, int(len(src)/4)))
                    end = min(len(tgt), len(src)+min(5, int(len(src)/4)))

                    temp = ""
                    flag=0
                    for char in tgt[start: end]:
                        if char in "。；！？;!?":
                            temp += char
                            flag = 1
                            break
                        temp += char

                    if flag == 1:
                        tgt = tgt[:start] + temp
                        count0 += 1
                    else: # 找不到可以截断的地方,则筛去
                        count1 += 1
                        continue
                clean_data.append([src, tgt])
        with open(result_path, "w", encoding="utf-8") as f2:
            idx = 1
            for src, tgt in clean_data:
                f2.write(str(idx)+"\t"+src+"\t"+tgt+"\n")
                idx += 1




para_path = "../../data/native/learner_native_mix/train/learner_native_mix.para"
result_path = "../../data/native/learner_native_mix/train/learner_native_mix.clean.para"
data_clean(para_path, result_path)

# extract('../../data/learner/CCL2023/track1/train/lang8.train.ccl22.para', 'lang8.train.lev')
# extract('data/clang8.train', 'clang8.train.lev')

# 然后正则匹配的，%s/[IDKS]\{5,100000000\}//ng
