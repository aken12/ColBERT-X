import argparse
from collections import defaultdict   
import json
import random
import os

##query id + queryに対して、positive(relevance judgment==3or1)のものをとってくる
##query id + queryに対して、BM25で上位なものをとってきて、そのクエリidに対してnegativeならそれを取ってくる

class CreateTrainData():
    def __init__(self,qrels_file,result_file,topk):
        #self.id_qrels_3,self.id_qrels_1,self.id_qrels = self.extract_positive_id(qrels_file)
        #self.candidate_ids = self.extract_topk_id(result_file,topk)
        #self.defective = []
        pass

    def make_id_docs(self,docs_json):
        docs_dict = defaultdict(list)
        #with open(os.path.join(self.data_dir,docs_json)) as fj:
        with open(docs_json.replace('\u2028',''),"r") as fj:
            for line in fj:
                line = json.loads(line)
                doc_id = line["docid"]
                if doc_id == "a6a3d39d-cd15-416c-a809-43b9f126ae15":
                    print("うんち")
                docs_dict[doc_id].append(line["title"])
                docs_dict[doc_id].append(line["text"])
                doc_len = len(line["text"])
                #if line["text"]:
                    #print(line["title"])
        return docs_dict

    def extract_positive_id(self,qrels_file): ##queryid docid qrels
        id_qrels_3 = defaultdict(list)
        id_qrels_1 = defaultdict(list)
        id_qrels = defaultdict(list)
        #with open(os.path.join(self.data_dir,qrels_file)) as fq:
        with open(qrels_file.replace('\u2028',''),"r") as fq:
            for line in fq:
                data = line.split()
                topic_id,doc_id,qrels = data[0],data[2],data[3]
                if qrels=='3':
                    id_qrels_3[topic_id].append(doc_id)
                    id_qrels[topic_id].append(doc_id)
                elif qrels=='1':
                    id_qrels_1[topic_id].append(doc_id)
                    id_qrels[topic_id].append(doc_id)
        return dict(id_qrels_3),dict(id_qrels_1),dict(id_qrels)
    
    def extract_topk_id(self,result_file,topk): #(id_qrel,result_file):
        candidate_ids = defaultdict(list)
        #with open(os.path.join(self.data_dir,result_file)) as fr:
        with open(result_file.replace('\u2028',''),"r") as fr:
            for line in fr:
                data = line.split()
                topic_id,doc_id,rank = data[0],data[2],data[3]
                if int(rank)+1 <= topk:
                    candidate_ids[topic_id].append(doc_id)
        return dict(candidate_ids)

    def extract_hard_negtive(self,hn_num,doc_dict):
        negative_passages = {}
        count = 0
        for topic_id in self.candidate_ids:
            negative_list = self.random_sample(topic_id,hn_num)
            if isinstance(negative_list,list):
                count += 1
                negative_passage_list = self.create_negative_dict(negative_list,topic_id,doc_dict)
                negative_passages[topic_id] = negative_passage_list
        return negative_passages

    def create_negative_dict(self,negative_list,topic_id,doc_dict): ##topic_idの処理を加えてどのクエリに対してか明示したい
        negative_passage_list = []
        for doc_id in negative_list:
            negative_dict = {}
            negative_dict["docid"] = doc_id
            negative_dict["title"] = doc_dict[doc_id][0]
            negative_dict["text"] = doc_dict[doc_id][1]
            negative_passage_list.append(negative_dict)
        return negative_passage_list

    def random_sample(self,topic_id,hn_num):
        negative_list = []
        doc_list = self.candidate_ids[topic_id]
        random.shuffle(doc_list)
        for doc_id in doc_list:
            if self.id_qrels_3.get(topic_id) is not None or self.id_qrels_1.get(topic_id) is not None:
                negative_list.append(doc_id)
                if len(negative_list) == hn_num:
                    return negative_list
            else:
                continue
        self.defective.append(topic_id)
        return

    def extract_positive_passage(self,doc_dict):
        positive_passages = {}
        for topic_id in self.id_qrels:
            positive_passage_list = self.create_positive_dict(topic_id,doc_dict)
            positive_passages[topic_id] = positive_passage_list
        return positive_passages

    def create_positive_dict(self,topic_id,doc_dict): ##topic_idの処理を加えてどのクエリに対してか明示したい
        positive_passage_list = []
        for doc_id in self.id_qrels[topic_id]:
            if doc_id not in doc_dict:
                continue
            positive_dict = {}
            positive_dict["docid"] = self.id_qrels[topic_id][0]
            positive_dict["title"] = doc_dict[doc_id][0]
            positive_dict["text"] = doc_dict[doc_id][1]
            positive_passage_list.append(positive_dict)
        return positive_passage_list

    def make_train_dict(self,topic_id,query,positive_passages,negative_passages):
        train_dict = {}
        train_dict["query_id"] = topic_id
        train_dict["query"] = query
        train_dict["positive_passages"] = positive_passages[topic_id]
        train_dict["negative_passages"] = negative_passages[topic_id]
        return train_dict

    @classmethod
    def load_topic_eng(cls,topic_json):
        topic_dict = {}
        with open(topic_json.replace('\u2028',''),"r") as ft:
            for line in ft:
                data = json.loads(line)
                topic_id = data["topic_id"]
                for topic in data["topics"]:
                    topic_dict[topic_id] = topic["topic_title"]
        return topic_dict
    
    @classmethod
    def load_topic(cls,topic_json,lang):
        topic_dict = {}
        with open(topic_json.replace('\u2028',''),"r") as ft:
            for line in ft:
                data = json.loads(line)
                topic_id = data["topic_id"]
                for topic in data["topics"]:
                    if (topic["lang"] == lang) and (topic["source"] == "20220114-scale21-sockeye2-tm1"):
                        topic_dict[topic_id] = topic["topic_title"]
        return topic_dict

    def make_train_file(self,topic_dict,output,positive_passages,negative_passages):
        p_topic = set(self.id_qrels_1.keys())
        n_topic = set(negative_passages.keys())
        topic_ids = p_topic & n_topic
        print(p_topic,n_topic)
        print(topic_ids)
        with open(output.replace('\u2028',''), "w") as f:
            for topic_id in topic_ids:
                query = topic_dict[topic_id]
                train_dict = self.make_train_dict(topic_id,query,positive_passages,negative_passages)
                json.dump(train_dict, f, ensure_ascii=False)
                f.write('\n')
        return

    def make_dev_file(self,topic_dict,output_dev):
        with open(output_dev, "w") as f:
            for topic_id in topic_dict.keys():
                topic = {}
                topic_title = topic_dict[topic_id]
                topic["query_id"] = topic_id
                topic["query"] = topic_title
                topic["positive_passages"] = []
                topic["negative_passages"] = []
                json.dump(topic, f, ensure_ascii=False)
                f.write('\n')
        return

def main():
    parser = argparse.ArgumentParser(description='') 
    parser.add_argument('--qrel_file', help='')
    parser.add_argument('--result_file', help='')
    parser.add_argument('--docs_json', help='')
    parser.add_argument('--topic_json', help='')
    parser.add_argument('--output', help='')
    parser.add_argument('--output_dev', help='')
    args = parser.parse_args() 
    ctd = CreateTrainData(args.qrel_file,args.result_file,300) ##qrels_file,result_file,topk,data_dir
    #doc_dict = ctd.make_id_docs(args.docs_json)
    #negative_passages = ctd.extract_hard_negtive(hn_num=15,doc_dict=doc_dict)
    #positive_passages = ctd.extract_positive_passage(doc_dict=doc_dict)
    lang = "zho"
    topic_dict = ctd.load_topic_eng(args.topic_json)
    #ctd.make_train_file(topic_dict,args.output,positive_passages,negative_passages)
    ctd.make_dev_file(topic_dict,args.output_dev)
    
if __name__ == '__main__':
    main()

