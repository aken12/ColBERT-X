import os
import ujson
import torch
import random

from collections import defaultdict, OrderedDict

from colbert.parameters import DEVICE
from colbert.modeling.colbert import ColBERT,ColBERT_X
from colbert.utils.utils import print_message, load_checkpoint


def load_model(args, do_print=True):
    if args.use_roberta:
        print("loading... roberta")
        colbert = ColBERT_X.from_pretrained(args.model_name,
                                      tokenizer=args.model_name,
                                      query_maxlen=args.query_maxlen,
                                      doc_maxlen=args.doc_maxlen,
                                      dim=args.dim,
                                      similarity_metric=args.similarity,
                                      mask_punctuation=args.mask_punctuation)
        colbert.roberta.resize_token_embeddings(len(colbert.tokenizer))
        print(colbert.roberta.config)
    else:
        colbert = ColBERT.from_pretrained(args.model_name,
                                      tokenizer=args.model_name,
                                      query_maxlen=args.query_maxlen,
                                      doc_maxlen=args.doc_maxlen,
                                      dim=args.dim,
                                      similarity_metric=args.similarity,
                                      mask_punctuation=args.mask_punctuation)
                                      
    colbert = colbert.to(DEVICE)

    print_message("#> Loading model checkpoint.", condition=do_print)

    checkpoint = load_checkpoint(args.checkpoint, colbert, do_print=do_print)

    colbert.eval()

    return colbert, checkpoint
