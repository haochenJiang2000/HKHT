def convert_para2train(para_path, train_path):
    with open(para_path, "r", encoding="utf-8") as f1, open(train_path, "w", encoding="utf8") as f2:
        para_data = [line for line in f1.read().split("\n") if line]
        for line in para_data:
            line = line.split("\t")
            src = line[0]
            tgts = line[1:]
            for tgt in tgts:
                f2.write("S\t"+src+"\nT\t"+tgt+"\n\n")


def convert_para2test(para_path, train_path):
    with open(para_path, "r", encoding="utf-8") as f1, open(train_path, "w", encoding="utf8") as f2:
        para_data = [line for line in f1.read().split("\n") if line]
        for line in para_data:
            line = line.split("\t")
            src = line[0]
            tgts = line[1:]
            for tgt in tgts:
                f2.write("S\t"+src+"\nT\t"+tgt+"\n\n")
                break


def pred_process(pred_path, out_path):
    with open(pred_path, "r", encoding="utf-8") as f1, open(out_path, "w", encoding="utf8") as f2:
        pred_data = [line for line in f1.read().split("\n") if line]
        for line in pred_data:
            line = "".join(line.split(" "))
            f2.write(line+"\n")


def data_split(para_path, train_path, valid_path, count):
    with open(para_path, "r", encoding="utf-8") as f1, open(train_path, "w", encoding="utf8") as f2, open(valid_path, "w", encoding="utf8") as f3:
        para_data = [line for line in f1.read().split("\n") if line]
        train_data = para_data[:-count]
        valid_data = para_data[-count:]

        for line in train_data:
            f2.write(line+"\n")
        for line in valid_data:
            f3.write(line+"\n")


def para2srctgt(para_path, src_path, tgt_path, mode=2):
    with open(para_path, "r", encoding="utf8") as f1, open(src_path, "w", encoding="utf8") as f2, open(tgt_path, "w", encoding="utf8") as f3:
        para_data = [line.split("\t") for line in f1.read().split("\n") if line]

        if mode == 2:
            for tup in para_data:
                src = tup[0]
                tgts = tup[1:]
                for tgt in tgts:
                    if len(tgt) <= 6:
                        tgt = src
                    f2.write(src+"\n")
                    f3.write(tgt+"\n")
        elif mode == 3:
            for tup in para_data:
                src = tup[1]
                tgts = tup[2:]
                for tgt in tgts:
                    if len(tgt) <= 6:
                        tgt = src
                    f2.write(src+"\n")
                    f3.write(tgt+"\n")


def srctgt2para(para_path, src_path, tgt_path, mode=2):
    with open(para_path, "w", encoding="utf8") as f1, open(src_path, "r", encoding="utf8") as f2, open(tgt_path, "r", encoding="utf8") as f3:
        src_data = [line for line in f2.read().split("\n") if line]
        tgt_data = [line for line in f3.read().split("\n") if line]

        for idx, (src, tgt) in enumerate(zip(src_data, tgt_data)):
            if mode == 2:
                f1.write(src+"\t"+tgt+"\n")
            elif mode == 3:
                f1.write(str(idx) + "\t" + src + "\t" + tgt + "\n")


para_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.mix.FCGEC_train.para"
train_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.mix.FCGEC_train.train"
convert_para2train(para_path, train_path)
#
# para_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.valid.para"
# train_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.valid.valid"
# convert_para2train(para_path, train_path)

# para_path = "/data/hcjiang/mrgec/data/exam/train/exam.train.gpt3.5.clean.with_token.edit.W.para"
# train_path = "/data/hcjiang/mrgec/data/exam/train/exam.train.gpt3.5.clean.with_token.edit.W.train"
# convert_para2train(para_path, train_path)

# para_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.train.para"
# train_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.train.train"
# convert_para2train(para_path, train_path)
#
# para_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.valid.para"
# train_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.valid.valid"
# convert_para2train(para_path, train_path)
#
# para_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.test.para"
# train_path = "/data/hcjiang/mrgec/data/hkht/4000/hkht.test.test"
# convert_para2test(para_path, train_path)

# para_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.news.v3.para"
# train_path = "/data/hcjiang/mrgec/data/pseudo/mix/syntax.pseudo.news.v3.para.train"
# convert_para2train(para_path, train_path)

# para_path = "/data/hcjiang/mrgec/data/hkht/test/hkht.test.para"
# train_path = "/data/hcjiang/mrgec/data/hkht/test/hkht.test.test"
# convert_para2test(para_path, train_path)

# para_path = "/data/hcjiang/mrgec/data/exam/test/exam.test.R.read_R.para.clean"
# train_path = "/data/hcjiang/mrgec/data/exam/test/exam.test.R.read_R.test.clean"
# convert_para2test(para_path, train_path)

# src_path = "/data/hcjiang/gec-seq2seq/data/pseudo/M/FCGEC_train.M.4.test.src.clean"
# tgt_path = "/data/hcjiang/gec-seq2seq/data/pseudo/M/FCGEC_train.M.4.test.tgt"
# para_path = "/data/hcjiang/gec-seq2seq/data/pseudo/M/FCGEC_train.M.4.test.para"
# srctgt2para(para_path, src_path, tgt_path, mode=2)

# src_path = "Wudao/train/train.src"
# tgt_path = "Wudao/train/train.tgt"
# para2srctgt(para_path, src_path, tgt_path, mode=2)

# pred_path = "/data/hcjiang/gec-seq2seq/data/FCGEC/valid/FCGEC_valid.pred.out"
# out_path = "/data/hcjiang/gec-seq2seq/data/FCGEC/valid/FCGEC_valid.pred.out.process"
# pred_process(pred_path, out_path)

# para_path = "Wudao/wudao.syntax.pseudo.mix.para"
# train_path = "Wudao/train/train.para"
# valid_path = "Wudao/valid/valid.para"
# data_split(para_path, train_path, valid_path, 10000)
