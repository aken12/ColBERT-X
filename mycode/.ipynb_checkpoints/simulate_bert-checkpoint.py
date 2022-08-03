import torch
from transformers import BertTokenizerFast,XLMRobertaTokenizer
import string
import torch.nn as nn
from transformers import BertPreTrainedModel, BertModel, BertTokenizerFast
from transformers import RobertaPreTrainedModel,XLMRobertaConfig, XLMRobertaTokenizer, XLMRobertaModel

batch_text = ["I like a cat", "I am a student"]
tok2 = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
#print(tok2.convert_tokens_to_ids(' '))

#tok = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
#tok.add_tokens(['[D]'])
#D_marker_token, D_marker_token_id = '[D]', tok.convert_tokens_to_ids('[unused1]')
#print(tok.tokenize("[D]"))
#print(len(tok))
#batch_text = ['. ' + x for x in batch_text]
obj = tok2(batch_text, padding='max_length', truncation=True,
                return_tensors='pt',add_special_tokens=False,max_length=10)
#tok = BertTokenizerFast.from_pretrained("bert-base-multilingual-cased")
ids, mask = obj['input_ids'], obj['attention_mask']

#cls_token, cls_token_id = tok.cls_token, tok.cls_token_id
#sep_token, sep_token_id = tok.sep_token, tok.sep_token_id
#mask_token, mask_token_id = tok.mask_token, tok.mask_token_id
#D_marker_token, D_marker_token_id = '[D]', tok.convert_tokens_to_ids('[unused0]')
print(ids)






#print(f"mBERTの特殊トークン {tok.special_tokens_map}")
#print(f"xlm-robertaの特殊トークン {tok2.special_tokens_map}")
#for i in range(1000):
    #print(tok.convert_ids_to_tokens(i),tok2.convert_ids_to_tokens(i))

#print(cls_token_id,sep_token_id,mask_token_id)

