"""
ymliu@2023.5.29
process NaSGEC dataset
"""

import argparse
from collections import OrderedDict


def main(args):
    with open(args.input) as f_in, open(args.output, "w") as f_out:
        count_source_sentence = 0
        count_target_sentence = 0
        data = OrderedDict()
        for line in f_in:
            line = line.strip().split("\t")
            source_sentence = line[1]
            annotations = line[2:]
            if source_sentence not in data.keys():
                count_source_sentence += 1
                data[source_sentence] = []
            else:
                print(line)
            if len(annotations) == 0:
                data[source_sentence].append(source_sentence)
                count_target_sentence += 1
            else:
                for annotation in annotations:
                    if annotation[-11:] == "【##需要上下文##】":
                        annotation = annotation[0:-11]
                    elif annotation[-7:] == "#需要上下文#":
                        annotation = annotation[0:-7]
                    if annotation in ["没有错误", "噪音数据", "句意不明", "无法标注", "歧义句"]:
                        target_sentence = source_sentence
                    else:
                        target_sentence = annotation
                    if target_sentence not in data[source_sentence]:
                        data[source_sentence].append(target_sentence)
                        count_target_sentence += 1
        for source_sentence, target_sentences in data.items():
            print("S", source_sentence, sep="\t", file=f_out)
            for target_sentence in target_sentences:
                print("T", target_sentence, sep="\t", file=f_out)
            print(file=f_out)
        print(count_source_sentence, count_target_sentence, count_target_sentence / count_source_sentence)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to para.txt")
    parser.add_argument("output", help="path to output")
    args = parser.parse_args()
    main(args)
