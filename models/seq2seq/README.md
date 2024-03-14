conda create -n mrgec python==3.10.10
conda activate mrgec
pip install -r requirements.txt
python -m spacy download en

conda create -n cherrant python==3.8
conda activate cherrant
pip install -r utils/ChERRANT/requirements.txt