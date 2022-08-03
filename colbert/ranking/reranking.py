import os
import time
import faiss
import random
import torch

from colbert.utils.runs import Run
from multiprocessing import Pool
from colbert.modeling.inference import ModelInference, ModelInference_X
from colbert.evaluation.ranking_logger import RankingLogger

from colbert.utils.utils import print_message, batch
from colbert.ranking.rankers import Ranker


def rerank(args):
    if not args.use_roberta:
        inference = ModelInference(args.colbert, amp=args.amp)
    else:
        print("model_inference: robertaを使用")
        inference = ModelInference_X(args.colbert, amp=args.amp)
    ranker = Ranker(args, inference, faiss_depth=None)

    ranking_logger = RankingLogger(Run.path, qrels=None)
    milliseconds = 0

    with ranking_logger.context('ranking.tsv', also_save_annotations=False) as rlogger:
        queries = args.queries
        qids_in_order = list(queries.keys()) ##クエリ辞書

        for qoffset, qbatch in batch(qids_in_order, 100, provide_offset=True): ##クエリidを進めていく
            qbatch_text = [queries[qid] for qid in qbatch] ##クエリのテキスト
            qbatch_pids = [args.topK_pids[qid] for qid in qbatch] ###クエリに対するpassage上位の辞書

            rankings = []

            for query_idx, (q, pids) in enumerate(zip(qbatch_text, qbatch_pids)): #クエリと上位文書のリスト
                torch.cuda.synchronize('cuda:0')
                s = time.time()

                Q = ranker.encode([q])
                pids, scores = ranker.rank(Q, pids=pids) ##クエリに対する分割文書の中で最大のものをとる
                print(pids)
                torch.cuda.synchronize()
                milliseconds += (time.time() - s) * 1000.0

                if len(pids):
                    print(qoffset+query_idx, q, len(scores), len(pids), scores[0], pids[0],
                          milliseconds / (qoffset+query_idx+1), 'ms')

                rankings.append(zip(pids, scores)) ##1000個のpidsとスコア　このときすでに文書を選択しているようにしたい

            for query_idx, (qid, ranking) in enumerate(zip(qbatch, rankings)):
                query_idx = qoffset + query_idx

                if query_idx % 100 == 0:
                    print_message(f"#> Logging query #{query_idx} (qid {qid}) now...")

                ranking = [(score, pid, None) for pid, score in ranking]
                rlogger.log(qid, ranking, is_ranked=True)

    print('\n\n')
    print(ranking_logger.filename)
    print("#> Done.")
    print('\n\n')
