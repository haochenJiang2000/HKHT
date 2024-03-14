# 航空航天项目-代码整合包

## 环境安装
请先安装运行需要的三个环境：

+ seq2seq：序列到序列纠错模型

+ seq2edit：序列到编辑纠错模型

+ cherrant：模型性能评估工具

安装环境请按照如下命令运行：
（注：pytorch需要适配服务器的GPU驱动版本，如运行报错请自行前往官网安装对应版本）

seq2seq环境：
```
conda create -n seq2seq python==3.10.10

conda activate seq2seq

pip install -r requirements_seq2seq.txt

python -m spacy download en
```
seq2edit环境：
```
conda create -n seq2edit python==3.8

conda activate seq2edit

pip install -r requirements_seq2edit.txt
```
cherrant环境：
```
conda create -n cherrant python==3.8

conda activate cherrant

pip install -r requirements_cherrant.txt
```
## seq2seq模型训练与评估：
+ 下载基础模型bart-large-chinese，放入models/seq2seq/pretrained_models
+ 运行脚本位置：models/seq2seq/bash/run_hkht.sh
+ 请参考脚本内容，确保训练数据已放入文件夹后再运行

## seq2edit模型训练与评估：
+ 下载基础模型chinese-struct-bert-large，放入models/seq2edit/plm
+ 运行脚本位置：models/seq2edit/bash/run_hkht.sh
+ 请参考脚本内容，确保训练数据已放入文件夹后再运行

# 数据
+ 模型备份：hkht-bak压缩包，其中包括了baseline模型，hkht-train微调模型，GPT数据增强后hkht-train微调模型
+ 数据备份：baseline模型训练数据 lang8+hsk， 航空航天领域标注数据集 hkht-test， 针对hkht-test的GPT增强数据集 hkht-gpt-pseudo