# -*- coding: utf-8 -*-

import os

import errant
from typing import Iterable, Union
from tempfile import NamedTemporaryFile
import torch
from torch.optim import AdamW, Optimizer

from supar.parser import Parser
from supar.config import Config
from supar.utils.common import BOS, EOS, PAD, UNK
from supar.utils.field import Field
from supar.utils.logging import get_logger
from supar.utils.tokenizer import BPETokenizer, TransformerTokenizer
from supar.utils.transform import Batch
import time

from .metric import PerplexityMetric
from .model import Seq2SeqModel
from .transform import Text
from .field import MrField

logger = get_logger(__name__)


class Seq2SeqParser(Parser):
    NAME = 'seq2seq'
    MODEL = Seq2SeqModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SRC = self.transform.SRC
        self.TGT = self.transform.TGT
        self.annotator = errant.load("en")

    def init_optimizer(self) -> Optimizer:
        return AdamW(
            params=[{'params': p, 'lr': self.args.lr * (1 if n.startswith('encoder') else self.args.lr_rate)} for n, p in self.model.named_parameters()],
            lr=self.args.lr,
            betas=(self.args.get('mu', 0.9), self.args.get('nu', 0.999)),
            eps=self.args.get('eps', 1e-8),
            weight_decay=self.args.get('weight_decay', 0),
        )

    def train_step(self, batch: Batch) -> torch.Tensor:
        src, ref = batch
        if isinstance(ref, dict):
            tgt, ref_nums = ref['padded_tensor'], ref['ref_nums']
        else:
            tgt = ref
        src_mask, tgt_mask = batch.mask, tgt.ne(self.args.pad_index)
        x = self.model(src)
        if isinstance(ref, dict):
            loss = self.model.mr_loss(x, tgt, src_mask, tgt_mask, ref_nums, self.epoch)
        else:
            loss = self.model.loss(x, tgt, src_mask, tgt_mask)
        return loss

    @torch.no_grad()
    def eval_step(self, batch: Batch) -> PerplexityMetric:
        src, ref = batch
        if isinstance(ref, dict):
            tgt, ref_nums = ref['padded_tensor'], ref['ref_nums']
        else:
            tgt = ref
        src_mask, tgt_mask = batch.mask, tgt.ne(self.args.pad_index)
        x = self.model(src)
        if isinstance(ref, dict):
            loss = self.model.mr_loss(x, tgt, src_mask, tgt_mask, ref_nums, self.epoch)
        else:
            loss = self.model.loss(x, tgt, src_mask, tgt_mask)
        preds = golds = None
        if self.args.eval_tgt:
            golds = [(s.values[0], s.values[1], t.tolist()) for s, t in zip(batch.sentences, tgt[tgt_mask].split(tgt_mask.sum(-1).tolist()))]
            preds = self.model.decode(x, batch.mask)[:, 0]
            pred_mask = preds.ne(self.args.pad_index)
            preds = [i.tolist() for i in preds[pred_mask].split(pred_mask.sum(-1).tolist())]
            preds = [(s.values[0], self.TGT.tokenize.decode(i), i) for s, i in zip(batch.sentences, preds)]
        return PerplexityMetric(loss, preds, golds, tgt_mask, self.annotator, not self.args.eval_tgt)

    @torch.no_grad()
    def pred_step(self, batch: Batch) -> Batch:
        (src,) = batch
        x = self.model(src)
        tgt = self.model.decode(x, batch.mask)
        batch.tgt = [[self.TGT.tokenize.decode(cand) for cand in i] for i in tgt.tolist()]
        return batch

    @classmethod
    def build(cls, path, min_freq=2, fix_len=20, ref='cs', **kwargs):
        r"""
        Build a brand-new Parser, including initialization of all data fields and model parameters.

        Args:
            path (str):
                The path of the model to be saved.
            min_freq (str):
                The minimum frequency needed to include a token in the vocabulary. Default: 2.
            fix_len (int):
                The max length of all subword pieces. The excess part of each piece will be truncated.
                Required if using CharLSTM/BERT.
                Default: 20.
            kwargs (dict):
                A dict holding the unconsumed arguments.
        """

        args = Config(**locals())
        os.makedirs(os.path.dirname(path) or './', exist_ok=True)
        if os.path.exists(path) and not args.build:
            return cls.load(**args)

        logger.info("Building the fields")
        if args.encoder == 'transformer':
            t = BPETokenizer(path=os.path.join(os.path.dirname(path)), files=args.vocab, backend='huggingface', pad=PAD, unk=UNK, bos=BOS, eos=EOS)
        else:
            t = TransformerTokenizer(name=args.bart)
        SRC = Field('src', pad=t.pad, unk=t.unk, bos=t.bos, eos=t.eos, tokenize=t)
        if ref == 'mr':
            TGT = MrField('tgt', pad=t.pad, unk=t.unk, bos=t.bos, eos=t.eos, tokenize=t)
        else:
            TGT = Field('tgt', pad=t.pad, unk=t.unk, bos=t.bos, eos=t.eos, tokenize=t)
        transform = Text(SRC=SRC, TGT=TGT)

        # share the vocab
        SRC.vocab = TGT.vocab = t.vocab
        args.update({'n_words': len(SRC.vocab), 'pad_index': SRC.pad_index, 'unk_index': SRC.unk_index, 'bos_index': SRC.bos_index, 'eos_index': SRC.eos_index})
        logger.info(f"{transform}")
        logger.info("Building the model")
        model = cls.MODEL(**args)
        logger.info(f"{model}\n")

        parser = cls(args, model, transform)
        parser.model.to(parser.device)
        return parser

    def postprocess(self, data: str, pred: str = None, max_len: int = 512, **kwargs):
        with open(data, "r+") as data_file, open(pred, "r+") as pred_file:
            data_list = data_file.read().strip().split("\n\n")
            pred_list = pred_file.read().strip().split("\n\n")

            idx = 0
            while len(pred_list) != len(data_list) and idx < 10:
                time.sleep(10)
                pred_list = pred_file.read().strip().split("\n\n")
                idx += 1

            out_list = [para.split("\n")[1].split("\t")[1] for para in pred_list]
            input_list = [para.split("\n")[0].split("\t")[1] for para in data_list]
            count = 0
            pred_file.seek(0)
            pred_file.truncate(0)
            for src in input_list:
                print("S", src, sep="\t", file=pred_file, flush=True)
                if len(self.SRC.tokenize(src)) >= max_len - 2:
                    print("T", src, sep="\t", end="\n\n", file=pred_file, flush=True)
                else:
                    print("T", ''.join(out_list[count].split()), sep="\t", end="\n\n", file=pred_file, flush=True)
                    count += 1

    def evaluate(self, pred: str = None, gold: str = None, eval: str = None, scorer=None, bpe=False, **kwargs):
        if scorer == "ChERRANT":
            bpe = ' --bpe' if bpe else ''
            para_file_path = '.'.join(pred.split(".")[:-1]) + ".para"
            pred_m2_file_path = '.'.join(pred.split(".")[:-1]) + ".m2.char"

            with open(pred, "r", encoding="utf8") as pred_file, open(para_file_path, "w", encoding="utf8") as para_file, open(pred_m2_file_path, "w", encoding="utf8") as pred_m2_file:
                pred_list = pred_file.read().strip().split("\n\n")
                for index, para in enumerate(pred_list, start=1):
                    src = para.split("\n")[0].split("\t")[1]
                    tgt = para.split("\n")[1].split("\t")[1]
                    para_file.write(str(index)+"\t"+src+"\t"+tgt+"\n")

            os.system(f"conda run -n cherrant python utils/ChERRANT/parallel_to_m2.py -f {para_file_path} -o {pred_m2_file_path} -g char" + bpe)
            os.system(f"conda run -n cherrant python utils/ChERRANT/compare_m2_for_evaluation.py -hyp {pred_m2_file_path} -ref {gold} -v -cat 3 >{eval}")
