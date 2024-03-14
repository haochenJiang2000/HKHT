from collections import OrderedDict


with open("hsk.para") as f_in:
    with open("hsk.train", "w") as f_out:
        count_source_sentence = 0
        count_target_sentence = 0
        data = OrderedDict()
        for line in f_in:
            line = line.strip().split("\t")
            source_sentence = line[0]
            target_sentences = line[1:]
            if source_sentence not in data.keys():
                data[source_sentence] = []
            if len(target_sentences) == 0:
                if source_sentence not in data[source_sentence]:
                    data[source_sentence].append(source_sentence)
            for target_sentence in target_sentences:
                if len(target_sentence) <= 1.5 * len(source_sentence) and len(source_sentence) <= 1.5 * len(target_sentence):
                    if len(target_sentence) >= 4 or len(source_sentence) >= 4:
                        if target_sentence not in data[source_sentence]:
                            data[source_sentence].append(target_sentence)
        for source_sentence, target_sentences in data.items():
            if len(target_sentences) == 0:
                continue
            print("S", source_sentence, sep="\t", file=f_out)
            count_source_sentence += 1
            for target_sentence in target_sentences:
                print("T", target_sentence, sep="\t", file=f_out)
                count_target_sentence += 1
            print(file=f_out)
        print(count_source_sentence, count_target_sentence, count_target_sentence / count_source_sentence)
