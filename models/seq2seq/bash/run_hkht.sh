REF=hkht-bak

for SEED in 1 2 3
do
  MODEL_DIR=saved_models/$REF

  #=========================================================================================#
  # stage1 pseudo-data
  MODEL_PATH=$MODEL_DIR/gpt-pseudo+hkht-train-finetune/hkht.pseudo.gpt.$SEED.pt
  config=configs/bart_chinese.ini

  TRAIN_PATH=../../../data/hkht-gpt-pseudo/hkht.train.gpt3.5.clean.with_token.edit.train
  VALID_PATH=../../../data/hkht-test/valid/hkht.valid.valid

  echo "devices: ${devices:=4}"
  echo "lr:      ${lr:=1e-99}"

  python -u run_old.py train --amp --build \
        --ref cs \
        --conf $config \
        --device $devices \
        --seed $SEED \
        --path $MODEL_PATH \
        --train $TRAIN_PATH \
        --dev $VALID_PATH \
        --lr=$lr \
        --bart='pretrained_models/bart-large-chinese'

  #=========================================================================================#
  # stage2 true-data
  TRAIN_PATH2=../../../data/hkht-test/train/hkht.train.train
  VALID_PATH2=../../../data/hkht-test/valid/hkht.valid.valid

  MODEL_PATH=$MODEL_DIR/gpt-pseudo+hkht-train-finetune/hkht.pseudo.gpt.$SEED.pt
  MODEL_PATH2=$MODEL_DIR/gpt-pseudo+hkht-train-finetune/hkht.pseudo.gpt.$SEED.stage2.pt
  config=configs/bart.yaml

  echo "devices: ${devices:=3}"
  echo "lr:      ${lr:=3e-05}"
  echo "update:  ${update:=5}"
  echo "warmup:  ${warmup:=200}"
  echo "encoder: ${encoder:=bart}"

  cp $MODEL_PATH $MODEL_PATH2
  python -u run.py train  \
        -s $SEED \
        -d $devices \
        --update-steps=$update \
        -c $config \
        -p $MODEL_PATH2 \
        --amp \
        --encoder $encoder \
        --train $TRAIN_PATH2 \
        --dev $VALID_PATH2 \
        --lr=$lr \
        --warmup-steps=$warmup \
        --bart='pretrained_models/bart-large-chinese'

  #=========================================================================================#
  ## predict
  MODEL_PATH=$MODEL_DIR/general.media.$SEED.pt
  devices=3
  lr=3e-05
  config=configs/bart_chinese.ini

  TEST_PATH=../../../data/hkht-test/test/hkht.test.test
  GOLD_PATH=../../../data/hkht-test/test/hkht.test.para.m2.char
  PRED_PATH=$MODEL_DIR/gpt-pseudo+hkht-train-finetune/hkht.pseudo.gpt.$SEED.stage2.pt

  python -u run_old.py predict --binarize \
          --device $devices \
          --seed $SEED \
          --conf $config \
          --path $MODEL_PATH \
          --data $TEST_PATH \
          --pred $PRED_PATH \
          --batch-size=1024 \
          --beam-size=12 \
          --max-len=1024 \
          --bart='pretrained_models/bart-large-chinese' \
          --scorer ChERRANT \
          --gold $GOLD_PATH
done