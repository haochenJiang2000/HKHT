# Step1. Data Preprocessing

## Download Structbert
if [ ! -f ./plm/chinese-struct-bert-large/pytorch_model.bin ]; then
    wget https://alice-open.oss-cn-zhangjiakou.aliyuncs.com/StructBERT/ch_model
    mv ch_model ./plm/chinese-struct-bert-large/pytorch_model.bin
fi

## Tokenize
SRC_FILE=../../../data/hkht-test/train/hkht.train.src  # 每行一个病句
TGT_FILE=../../../data/hkht-test/train/hkht.train.tgt  # 每行一个正确句子，和病句一一对应
if [ ! -f $SRC_FILE".char" ]; then
    python ../../tools/segment/segment_bert.py < $SRC_FILE > $SRC_FILE".char"  # 分字
fi
if [ ! -f $TGT_FILE".char" ]; then
    python ../../tools/segment/segment_bert.py < $TGT_FILE > $TGT_FILE".char"  # 分字
fi

DEV_SRC_FILE=../../../data/hkht-test/valid/hkht.valid.src  # 每行一个病句
DEV_TGT_FILE=../../../data/hkht-test/valid/hkht.valid.tgt  # 每行一个正确句子，和病句一一对应
if [ ! -f $DEV_SRC_FILE".char" ]; then
    python ../../tools/segment/segment_bert.py < $DEV_SRC_FILE > $DEV_SRC_FILE".char"  # 分字
fi
if [ ! -f $DEV_TGT_FILE".char" ]; then
    python ../../tools/segment/segment_bert.py < $DEV_TGT_FILE > $DEV_TGT_FILE".char"  # 分字
fi

## Generate label file
LABEL_FILE=../../../data/hkht-test/train/hkht.train.label  # 训练数据
if [ ! -f $LABEL_FILE ]; then
    python ./utils/preprocess_data.py -s $SRC_FILE".char" -t $TGT_FILE".char" -o $LABEL_FILE --worker_num 32
    shuf $LABEL_FILE > $LABEL_FILE".shuf"
fi

DEV_LABEL_FILE=../../../data/hkht-test/valid/hkht.valid.label  # 验证集数据
if [ ! -f $DEV_LABEL_FILE ]; then
    python ./utils/preprocess_data.py -s $DEV_SRC_FILE".char" -t $DEV_TGT_FILE".char" -o $DEV_LABEL_FILE --worker_num 32
    shuf $DEV_LABEL_FILE > $DEV_LABEL_FILE".shuf"
fi

for SEED in 1 2 3
do
  # Step2. Training
  CUDA_DEVICE=4

  PRETRAIN_WEIGHTS_DIR=../plm/chinese-struct-bert-large
  VOCAB_PATH=../data/output_vocabulary_chinese_char_hsk+lang8_5

  MODEL_DIR=../exps/seq2edit.hkht.gpt.$SEED
  if [ ! -d $MODEL_DIR ]; then
    mkdir -p $MODEL_DIR
  fi

  mkdir ${MODEL_DIR}/src_bak
  cp ./run_hkht.sh $MODEL_DIR/src_bak
  cp -r ../gector $MODEL_DIR/src_bak
  cp ../train.py $MODEL_DIR/src_bak
  cp ../predict.py $MODEL_DIR/src_bak

  ## Freeze encoder (Cold Step)
  #COLD_LR=1e-3
  #COLD_BATCH_SIZE=128
  #COLD_MODEL_NAME=Best_Model_Stage_1
  #COLD_EPOCH=2
  #
  #CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python train.py --tune_bert 0\
  #                --train_set $LABEL_FILE".shuf"\
  #                --dev_set $DEV_SET\
  #                --model_dir $MODEL_DIR\
  #                --model_name $COLD_MODEL_NAME\
  #                --vocab_path $VOCAB_PATH\
  #                --batch_size $COLD_BATCH_SIZE\
  #                --n_epoch $COLD_EPOCH\
  #                --lr $COLD_LR\
  #                --weights_name $PRETRAIN_WEIGHTS_DIR\
  #                --seed $SEED

  # Unfreeze encoder
  # stage1
  LR=1e-5
  PREDICTOR_DROPOUT=0.4
  BATCH_SIZE=32
  ACCUMULATION_SIZE=4
  MODEL_NAME=Best_Model_Stage_4
  EPOCH=20
  PATIENCE=3

  PRETRAIN_FOLDER=../exps/seq2edit.hkht.baseline.$SEED

  train_path=$GPT_LABEL_FILE".shuf"
  dev_path=$DEV_LABEL_FILE".shuf"
  train_path2=$LABEL_FILE".shuf"
  dev_path2=$DEV_LABEL_FILE".shuf"

  CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python train.py --tune_bert 1\
                  --train_set $train_path\
                  --dev_set $dev_path\
                  --model_dir $MODEL_DIR\
                  --model_name $MODEL_NAME\
                  --vocab_path $VOCAB_PATH\
                  --batch_size $BATCH_SIZE\
                  --n_epoch $EPOCH\
                  --lr $LR\
                  --accumulation_size $ACCUMULATION_SIZE\
                  --patience $PATIENCE\
                  --weights_name $PRETRAIN_WEIGHTS_DIR\
                  --pretrain_folder $PRETRAIN_FOLDER\
                  --pretrain "Best_Model_Stage_3"\
                  --seed $SEED

  # stage2
  LR=1e-5
  PREDICTOR_DROPOUT=0.4
  BATCH_SIZE=32
  ACCUMULATION_SIZE=4
  MODEL_NAME=Best_Model_Stage_5
  EPOCH=20
  PATIENCE=3

  PRETRAIN_FOLDER=./exps/seq2edit.hkht.gpt.$SEED

  CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python train.py --tune_bert 1\
                  --train_set $train_path2\
                  --dev_set $dev_path2\
                  --model_dir $MODEL_DIR\
                  --model_name $MODEL_NAME\
                  --vocab_path $VOCAB_PATH\
                  --batch_size $BATCH_SIZE\
                  --n_epoch $EPOCH\
                  --lr $LR\
                  --accumulation_size $ACCUMULATION_SIZE\
                  --patience $PATIENCE\
                  --weights_name $PRETRAIN_WEIGHTS_DIR\
                  --pretrain_folder $PRETRAIN_FOLDER\
                  --pretrain "Best_Model_Stage_4"\
                  --seed $SEED

# Step3. Inference
  MODEL_DIR=/data/hcjiang/MuCGEC-main/models/seq2edit-based-CGEC/exps/seq2edit.hkht.gpt.$SEED
  MODEL_PATH=$MODEL_DIR/Best_Model_Stage_5.th
  RESULT_DIR=$MODEL_DIR/results

  INPUT_FILE=../../../data/hkht-test/test/hkht.test.src # 输入文件
  if [ ! -f $INPUT_FILE".char" ]; then
      python ../../tools/segment/segment_bert.py < $INPUT_FILE > $INPUT_FILE".char"  # 分字
  fi
  if [ ! -d $RESULT_DIR ]; then
    mkdir -p $RESULT_DIR
  fi
  OUTPUT_FILE=$RESULT_DIR/seq2edit.hkht.gpt.$SEED.stage2.out

  echo "Generating..."
  SECONDS=0
  CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python predict.py --model_path $MODEL_PATH\
                    --weights_name $PRETRAIN_WEIGHTS_DIR\
                    --vocab_path $VOCAB_PATH\
                    --input_file $INPUT_FILE".char"\
                    --output_file $OUTPUT_FILE --log

  echo "Generating Finish!"

  duration=$SECONDS
  echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."

  # 评估
  para_file_path=$RESULT_DIR/seq2edit.hkht.gpt.$SEED.stage2.para
  pred_m2_file_path=$RESULT_DIR/seq2edit.hkht.gpt.$SEED.stage2.para.m2.char
  gold=../../../data/hkht-test/test/hkht.test.para.m2.char
  eval=$RESULT_DIR/seq2edit.hkht.gpt.$SEED.stage2.pred.cherrant

  python ../../tools/srctgt2para.py -s $INPUT_FILE -t $OUTPUT_FILE -o $para_file_path
  conda run -n cherrant python ../../scorers/ChERRANT/parallel_to_m2.py -f $para_file_path -o $pred_m2_file_path -g char
  conda run -n cherrant python ../../scorers/ChERRANT/compare_m2_for_evaluation.py -hyp $pred_m2_file_path -ref $gold -v -cat 3 >$eval
done