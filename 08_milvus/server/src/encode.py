# from sentence_transformers import SentenceTransformer
# from sklearn.preprocessing import normalize
# from config import MODEL_PATH
# import gdown
# import zipfile
# import os

# class SentenceModel:
#     """
#     Say something about the ExampleCalass...

#     Args:
#         args_0 (`type`):
#         ...
#     """
#     def __init__(self):
#         if not os.path.exists(MODEL_PATH):
#             os.makedirs(MODEL_PATH)
#         if not os.path.exists("./paraphrase-mpnet-base-v2.zip"):
#             url = 'https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/paraphrase-mpnet-base-v2.zip'
#             gdown.download(url)
#         with zipfile.ZipFile('paraphrase-mpnet-base-v2.zip', 'r') as zip_ref:
#             zip_ref.extractall(MODEL_PATH)
#         self.model = SentenceTransformer(MODEL_PATH)

#     def sentence_encode(self, data):
#         embedding = self.model.encode(data)
#         sentence_embeddings = normalize(embedding)
#         return sentence_embeddings.tolist()

import pandas as pd
import re
import fasttext
import pandas as pd
import numpy as np
import json
import torch
from torch.autograd import Variable
from hazm import Normalizer


def en_remove_punc(s):
    punc = '"#\'*+,-/:;<=>@[\]^_`{|}~\'●,•()»«–‑-،؛−٫—'
    table = str.maketrans(dict.fromkeys(punc, ' ')) 
    new_s = s.translate(table) 
    new_s = ' '.join(new_s.split())
    return new_s


def fa_remove_punc(s):
    punc = '"#\'*+,-:;<=>@[\]^_`{|}~\'●,•()»«–‑-،؛−—'
    table = str.maketrans(dict.fromkeys(punc, ' ')) 
    new_s = s.translate(table) 
    new_s = ' '.join(new_s.split())
    return new_s

def en_normalizer(text):
    text = text.lower()
    text = text.replace('\xa0','')
    #text = text.replace('-',' ')
    text = re.sub(r"\[[\d| ]+\]", " ", text)
    text = en_remove_punc(text)
    #text = re.sub(r"(.)\.([^0-9]|\n|$)", r"\1 . \2", text)
    text = re.sub(r"(\w{2,}| )\.([^0-9]|\n|$)", r"\1 . \2", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\?", " ? ", text)
    text = re.sub(r"؟", " ؟ ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()

def fa_normalizer(text):
    text = arToPersianChar(text)
    text = arToPersianNumb(text)
    text = text.replace('\xa0','')
    #text = text.replace('-',' ')
    text = text.replace('ٔ', '')
    text = fa_remove_punc(text)
    # more_normalization_function()
    normalizer = Normalizer(persian_style = False, punctuation_spacing = False, affix_spacing = False)
    text = normalizer.normalize(text)
    text = text.replace('\u200c',' ')
    text = text.replace('\u200b',' ')
    text = re.sub(r"(\w{2,}| )\.([^0-9]|\n|$)", r"\1 . \2", text)
    text = re.sub(r'([\d+])\.([\d+])', r'\1٫\2', text)
    text = re.sub(r'([\d+])/([\d+])', r'\1٫\2', text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\?", " ? ", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def arToPersianNumb(number):
    dic = {
        '١': '۱',
        '٢': '۲',
        '٣': '۳',
        '٤': '۴',
        '٥': '۵',
        '٦': '۶',
        '٧': '۷',
        '٨': '۸',
        '٩': '۹',
        '٠': '۰',
    }
    return multiple_replace(dic, number)


def arToPersianChar(userInput):
    dic = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی'
    }
    return multiple_replace(dic, userInput)

def multiple_replace(dic, text):
    pattern = "|".join(map(re.escape, dic.keys()))
    return re.sub(pattern, lambda m: dic[m.group()], str(text))

class SentenceModel:
    """
    Say something about the ExampleCalass...

    Args:
        args_0 (`type`):
        ...
    """
    def __init__(self):
        en_bin = './model/model_en.bin'
        fa_bin = './model/model_fa.bin'

        en_vec = './model/model_en.vec'
        fa_vec = './model/model_fa.vec'

        en_idf_addr = './idf/en_idf.csv'
        fa_idf_addr = './idf/fa_idf.csv'
        
        cross_model_addr = './model/cross_ling.pt'
        
        en_idf = pd.read_csv(en_idf_addr)
        en_idf.index = en_idf['word']
        del en_idf['word']

        fa_idf = pd.read_csv(fa_idf_addr)
        fa_idf.index = fa_idf['word']
        del fa_idf['word']
        
        self.cross_model = torch.nn.Sequential(
            torch.nn.Linear(300, 300)
        )
        self.cross_model.load_state_dict(torch.load(cross_model_addr))
        self.cross_model.eval()
        
        self.en_idf = en_idf
        self.fa_idf = fa_idf
        self.model_en = fasttext.load_model(en_bin)
        self.model_fa = fasttext.load_model(fa_bin)
        self.non_vocab_idf_weight = 3

    def encode_en(self, par):
        par_normd_spltd = en_normalizer(par).split(' ')
        vecs = []
        idfs = []
        for word in par_normd_spltd:
            idf = self.en_idf.idf.get(word, self.non_vocab_idf_weight)
            idfs.append(idf)
            vecs.append(idf * self.model_en.get_word_vector(word))
            
        return np.sum(np.array(vecs), axis = 0)/np.sum(idfs)
    
    def encode_fa(self, par):
        par_normd_spltd = fa_normalizer(par).split(' ')
        vecs = []
        idfs = []
        for word in par_normd_spltd:
            idf = self.fa_idf.idf.get(word, self.non_vocab_idf_weight)
            idfs.append(idf)
            vecs.append(idf * self.model_fa.get_word_vector(word))
            
        return np.sum(np.array(vecs), axis = 0)/np.sum(idfs)

    
    def encode_cross(self, par):
        fa_vec = self.encode_fa(par)
        with torch.no_grad():
            fa_tensor = Variable(torch.from_numpy(fa_vec)).float()
            cross_tensor = self.cross_model(fa_tensor)
            return cross_tensor.detach().numpy()