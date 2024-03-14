with open("/data/hcjiang/gec-seq2seq/data/hkht/valid/valid.para", 'r', encoding='utf8') as f:
    content = f.readlines()
src = [i.split('\t')[0] + '\n' for i in content]
tgt = [i.split('\t')[1] for i in content]
with open("/data/hcjiang/MuCGEC-main/data/hkht/valid/valid.src", 'w', encoding='utf8') as f:
    f.writelines(src)
with open("/data/hcjiang/MuCGEC-main/data/hkht/valid/valid.tgt", 'w', encoding='utf8') as f:
    f.writelines(tgt)
