import argparse
from collections import defaultdict   
import json
import random
import os
import csv
import re
##query id + queryに対して、positive(relevance judgment==3or1)のものをとってくる
##query id + queryに対して、BM25で上位なものをとってきて、そのクエリidに対してnegativeならそれを取ってくる

class CreateTrainData():
    def __init__(self,qrels_file,result_file,topk):
        self.id_qrels = self.extract_positive_id(qrels_file)
        self.candidate_ids = self.extract_topk_id(result_file,topk)
        self.comp = re.compile(r"[\r\n\t]")
        print("終了")
        
    def make_id_docs(self,docs_file): ##docとidを対応させたdict
        docs_dict = defaultdict(list)
        #with open(os.path.join(self.data_dir,docs_json)) as fj:
        with open(docs_file,"r") as fj:
            for line in fj:
                data = line.split('\t')
                topic_id = data[0]
                docs_dict[topic_id] = data[1]
        print("終了")
        return docs_dict

    def make_id_query(self,query_file): ##docとidを対応させたdict
        query_dict = defaultdict(list)
        #with open(os.path.join(self.data_dir,docs_json)) as fj:
        with open(query_file,"r") as fq:
            for line in fq:
                data = line.split('\t')
                topic_id = data[0]
                query_dict[topic_id] = data[1]
        print("終了")
        return query_dict

    def extract_positive_id(self,qrels_file): ##queryid docid qrels
        id_qrels = defaultdict(list)
        with open(qrels_file,"r") as fq:
            for line in fq:
                data = line.split()
                topic_id,doc_id = data[0],data[2]
                id_qrels[topic_id].append(doc_id) ##topic_id doc_id
        return dict(id_qrels)
    
    def extract_topk_id(self,result_file,topk): #(id_qrel,result_file):
        candidate_ids = defaultdict(list)
        with open(result_file,"r") as fr:
            for line in fr:
                data = line.split()
                topic_id,doc_id,rank = data[0],data[1],data[2]
                if int(rank)+1 <= topk:
                    candidate_ids[topic_id].append(doc_id)
        return dict(candidate_ids)

    def create_negative(self): #ネガティブidの辞書
        negative_passages = {}
        for topic_id in self.candidate_ids:
            negative_list = self.random_sample(topic_id,hn_num=30)
            if negative_list != None:
                negative_passages[topic_id] = negative_list
        self.candidate_ids = None
        return negative_passages

    def random_sample(self,topic_id,hn_num):
        negative_list = []
        doc_list = self.candidate_ids[topic_id]
        random.shuffle(doc_list)
        for doc_id in doc_list:
            if self.id_qrels.get(topic_id) == None: #qrelsにない場合
                return None
            if doc_id not in self.id_qrels[topic_id]:
                negative_list.append(doc_id)
                if len(negative_list) == hn_num:
                    return negative_list
            else:
                continue
        return negative_list
    """
    def random_sample(self,topic_id):
        doc_list = self.candidate_ids[topic_id]
        random.shuffle(doc_list)
        for doc_id in doc_list:
                if doc_id not in self.id_qrels.get(topic_id):
                    return doc_id
                else:
                    continue
        return
    """ 
    def create_triples_file(self,negative_passages,output_file,docs_dict,lang): #文章を読み込むときは改行文字に注意
        with open(output_file,"w")as fw:
            for topic_id in self.id_qrels:
                positive_id = random.choice(self.id_qrels[topic_id])
                positive_passage = f"[{lang}]" + docs_dict[positive_id].replace('\n','')
                if negative_passages.get(topic_id) is not None:
                    negative_list = negative_passages[topic_id]
                    for negative_id in negative_list:
                        negative_passage = f"[{lang}]" + docs_dict[negative_id].replace('\n','')
                        fw.write(f'{topic_id}\t{positive_passage}\t{negative_passage}\n')
        print("終了")
        return

    def create_triples(self,negative_passages,output_file,docs_dict,lang): #positive id の辞書
        triples_list = []
        with open(output_file,"w",newline='')as fw:
            for topic_id in self.id_qrels:
                for positive_id in self.id_qrels[topic_id]:
                    if negative_passages.get(topic_id) is not None:
                        negative_list = negative_passages[topic_id]
                        for negative_id in negative_list:
                            a = [topic_id,f"{[lang]}{docs_dict[positive_id]}",docs_dict[negative_id]]
                            triples_list.append(a)
            random.shuffle(triples_list)
            writer = csv.writer(fw,delimiter='\t')
            for triple in triples_list:
                writer.writerow(triple)
        print("終了")
        return

    def append_triples(self,negative_passages,docs_dict,lang,triples_list,query_dict): #positive id の辞書
        for topic_id in self.id_qrels:
            for positive_id in self.id_qrels[topic_id]:
                if negative_passages.get(topic_id) is not None:
                    negative_list = negative_passages[topic_id]
                    for negative_id in negative_list:
                        query = re.sub(self.comp,'',query_dict[topic_id])
                        p_pas = re.sub(self.comp,'',docs_dict[positive_id])
                        n_pas = re.sub(self.comp,'',docs_dict[negative_id])
                        a = [f'[{lang}]{query}',p_pas,n_pas]
                        triples_list.append(a)
        print("triple終了")
        return triples_list

    @classmethod
    def write_triples(cls,triples_list,output_file):
        print("開始")
        with open(output_file,"w")as fw:
            writer = csv.writer(fw,delimiter='\t')
            print(len(triples_list))
            for i in random.sample(triples_list,len(triples_list)):
                writer.writerow(i)
        return 

def main():
    parser = argparse.ArgumentParser(description='') 
    parser.add_argument('--qrel_file', help='')
    parser.add_argument('--result_file', help='')
    parser.add_argument('--docs_file', help='')
    parser.add_argument('--output_file', help='')
    parser.add_argument('--query_file', help='')
    args = parser.parse_args() 
    ctd = CreateTrainData(args.qrel_file,args.result_file,200)
    lang_list = ["rus","fas","zho"] 
    negative_passages = ctd.create_negative() # /home/aken12/eng-fas/msmarco.collection.20210731-scale21-sockeye2-tm1.tsv
    query_dict = ctd.make_id_query(args.query_file)
    triples_list = []
    for lang in lang_list:
        docs_dict = ctd.make_id_docs(f"/home/aken12/eng-{lang}/msmarco.collection.20210731-scale21-sockeye2-tm1.tsv")
        triples_list = ctd.append_triples(negative_passages=negative_passages,query_dict=query_dict,lang=lang,
        triples_list=triples_list,docs_dict=docs_dict)
    print("終了")
    #ctd.create_triples_file(negative_passages=negative_passages,output_file=args.output_file,docs_dict=docs_dict)
    ctd.write_triples(triples_list=triples_list,output_file=args.output_file)

    #docs_dict = ctd.make_id_docs(args.docs_file)

    #ctd.create_triples(negative_passages,args.output_file)

if __name__ == '__main__':
    main()