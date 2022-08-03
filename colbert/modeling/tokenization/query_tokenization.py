import torch

from transformers import BertTokenizerFast,XLMRobertaTokenizer
from colbert.modeling.tokenization.utils import _split_into_batches


class QueryTokenizer():
    def __init__(self, query_maxlen,tokenizer):
        self.tok = BertTokenizerFast.from_pretrained(tokenizer)
        self.query_maxlen = query_maxlen
        self.Q_marker_token, self.Q_marker_token_id = '[Q]', self.tok.convert_tokens_to_ids('[unused1]')
        self.cls_token, self.cls_token_id = self.tok.cls_token, self.tok.cls_token_id
        self.sep_token, self.sep_token_id = self.tok.sep_token, self.tok.sep_token_id
        self.mask_token, self.mask_token_id = self.tok.mask_token, self.tok.mask_token_id
        assert self.Q_marker_token_id == 1 and self.mask_token_id == 103

    def tokenize(self, batch_text, add_special_tokens=False):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        tokens = [self.tok.tokenize(x, add_special_tokens=False) for x in batch_text]

        if not add_special_tokens:
            return tokens

        prefix, suffix = [self.cls_token, self.Q_marker_token], [self.sep_token]
        tokens = [prefix + lst + suffix + [self.mask_token] * (self.query_maxlen - (len(lst)+3)) for lst in tokens]

        return tokens

    def encode(self, batch_text, add_special_tokens=False):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        ids = self.tok(batch_text, add_special_tokens=False)['input_ids']

        if not add_special_tokens:
            return ids

        prefix, suffix = [self.cls_token_id, self.Q_marker_token_id], [self.sep_token_id]
        ids = [prefix + lst + suffix + [self.mask_token_id] * (self.query_maxlen - (len(lst)+3)) for lst in ids]

        return ids

    def tensorize(self, batch_text, bsize=None):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        # add placehold for the [Q] marker
        batch_text = ['. ' + x for x in batch_text]

        obj = self.tok(batch_text, padding='max_length', truncation=True,
                       return_tensors='pt', max_length=self.query_maxlen)

        ids, mask = obj['input_ids'], obj['attention_mask']

        # postprocess for the [Q] marker and the [MASK] augmentation
        ids[:, 1] = self.Q_marker_token_id
        ids[ids == 0] = self.mask_token_id

        if bsize:
            batches = _split_into_batches(ids, mask, bsize)
            return batches
        print(ids,mask)
        exit()
        return ids, mask

class QueryTokenizer_X():
    def __init__(self, query_maxlen,tokenizer):
        print("query_tokenizer : robartaを使用")
        self.tok_name = tokenizer
        self.tok = XLMRobertaTokenizer.from_pretrained(tokenizer)
        self.tok.add_tokens(['[unused1]'])#Q
        self.tok.add_tokens(['[unused2]'])#D
        self.tok.add_tokens(['[zho]'])
        self.tok.add_tokens(['[fas]'])
        self.tok.add_tokens(['[rus]'])
        self.tok.add_tokens(['[eng]'])
        self.query_maxlen = query_maxlen

        self.Q_marker_token, self.Q_marker_token_id = '[Q]',250002
        self.zho_marker_token, self.zho_marker_token_id = '[zho]', 250004
        self.fas_marker_token, self.fas_marker_token_id = '[fas]', 250005
        self.rus_marker_token, self.rus_marker_token_id = '[rus]', 250006
        self.eng_marker_token, self.eng_marker_token_id = '[eng]', 250007
        self.cls_token, self.cls_token_id = self.tok.cls_token, self.tok.cls_token_id
        self.sep_token, self.sep_token_id = self.tok.sep_token, self.tok.sep_token_id
        self.mask_token, self.mask_token_id = self.tok.mask_token, self.tok.mask_token_id

        assert self.Q_marker_token_id == self.tok.convert_tokens_to_ids("[unused1]") and self.mask_token_id == 250001
        assert self.tok.convert_tokens_to_ids("[zho]") == 250004
        assert self.tok.convert_tokens_to_ids("[fas]") == 250005 
        assert self.tok.convert_tokens_to_ids("[rus]") == 250006
        assert self.tok.convert_tokens_to_ids("[eng]") == 250007

    def tokenize(self, batch_text, add_special_tokens=False):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        tokens = [self.tok.tokenize(x, add_special_tokens=False) for x in batch_text]

        if not add_special_tokens:
            return tokens

        prefix, suffix = [self.cls_token, self.Q_marker_token], [self.sep_token]
        tokens = [prefix + lst + suffix + [self.mask_token] * (self.query_maxlen - (len(lst)+3)) for lst in tokens]

        return tokens

    def encode(self, batch_text, add_special_tokens=False):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        ids = self.tok(batch_text, add_special_tokens=False)['input_ids']

        if not add_special_tokens:
            return ids

        prefix, suffix = [self.cls_token_id, self.Q_marker_token_id], [self.sep_token_id]
        ids = [prefix + lst + suffix + [self.mask_token_id] * (self.query_maxlen - (len(lst)+3)) for lst in ids]

        return ids

    def tensorize(self, batch_text, bsize=None):
        assert type(batch_text) in [list, tuple], (type(batch_text))

        # add placehold for the [Q] marker
        batch_text = ['[unused1]' + x for x in batch_text]

        obj = self.tok(batch_text, padding='max_length', truncation=True,
                       return_tensors='pt', max_length=self.query_maxlen)

        ids, mask = obj['input_ids'], obj['attention_mask']

        # postprocess for the [Q] marker and the [MASK] augmentation
        #ids[:, 1] = self.Q_marker_token_id
        ids[ids == 1] = self.mask_token_id ##ここを　1に直す
        
        if bsize:
            batches = _split_into_batches(ids, mask, bsize)
            return batches
        print(mask)
        return ids, mask