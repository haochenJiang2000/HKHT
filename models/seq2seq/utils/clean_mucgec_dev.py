from collections import OrderedDict

with open("MuCGEC_dev.txt") as f_in, open("mucgec.dev", "w") as f_out:
    data = OrderedDict()
    src_cnt = 0
    tgt_cnt = 0
    for line in f_in:
        line = line.strip().split("\t")
        src = line[1]
        if src not in data.keys():
            data[src] = []
        tgts = line[2:]
        assert len(tgts) > 0
        for tgt in tgts:
            if tgt in ["没有错误", "无法标注"]:
                tgt = src
            if tgt not in data[src]:
                data[src].append(tgt)
    for src, tgts in data.items():
        print("S", src, sep="\t", file=f_out)
        src_cnt += 1
        for tgt in tgts:
            print("T", tgt, sep="\t", file=f_out)
            tgt_cnt += 1
        print(file=f_out)
    print(src_cnt)
    print(tgt_cnt)
