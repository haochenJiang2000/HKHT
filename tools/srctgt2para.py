import argparse

def srctgt2para(para_path, src_path, tgt_path, mode=2):
    with open(para_path, "w", encoding="utf8") as f1, open(src_path, "r", encoding="utf8") as f2, open(tgt_path,
                                                                                                       "r",
                                                                                                       encoding="utf8") as f3:
        src_data = [line for line in f2.read().split("\n") if line]
        tgt_data = [line for line in f3.read().split("\n") if line]

        for idx, (src, tgt) in enumerate(zip(src_data, tgt_data)):
            if mode == 2:
                f1.write(src + "\t" + tgt + "\n")
            elif mode == 3:
                f1.write(str(idx) + "\t" + src + "\t" + tgt + "\n")

def main(args):
    para_path = args.output
    src_path = args.src_file
    tgt_path = args.tgt_file
    srctgt2para(para_path, src_path, tgt_path, mode=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="srctgt_file to para_file")
    parser.add_argument("-s", "--src_file", type=str, required=True, help="src file")
    parser.add_argument("-t", "--tgt_file", type=str, required=True, help="tgt file")
    parser.add_argument("-o", "--output", type=str, help="Output file", required=True)
    args = parser.parse_args()
    main(args)