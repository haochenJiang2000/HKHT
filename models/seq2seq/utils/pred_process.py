import argparse

def pred_process(pred_path, out_path):
    with open(pred_path, "r", encoding="utf-8") as f1, open(out_path, "w", encoding="utf8") as f2:
        pred_data = [line.split("\n") for line in f1.read().split("\n\n") if line]
        for line in pred_data:
            assert len(line) == 2, print(line)
            tgt = line[1].split("\t")[1]
            tgt = "".join(tgt.split(" "))
            f2.write(tgt+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='pred process.'
    )
    parser.add_argument('--pred_path', '-i', help='path to the pred file')
    parser.add_argument('--out_path', '-o', help='path to the outout file')
    args = parser.parse_args()
    pred_process(args.pred_path, args.out_path)