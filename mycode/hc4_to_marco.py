import argparse
from collections import defaultdict   
import json
import random
import os
import csv
import re

class Dataedit():
    def __init__(self):
        self.count = 0
        self.id_dict = {}

    def doc_edit(self,doc_file,doc_tsv):
        with open(doc_file,'r')as fr, open(doc_tsv,'w')as fw:
            writer = csv.writer(fw,delimiter='\t')
            idx = 0
            for line in fr:
                doc_line = []
                data = json.loads(line)
                doc_line.append(idx)
                if data["text"] == '' and data["title"] == '':
                    continue
                doc_line.append(' '.join([re.sub(r"[\r\n\t]",'',data["title"]),re.sub(r"[\r\n\t]",'',data["text"])[:300]])) #コンパイル
                writer.writerow(doc_line)
                if len(doc_line) != 2:
                    print(doc_line)
                idx += 1
        print("文書編集終わり")
        return

    def id_to_number(self,doc_file,id_idx_file):
        with open(doc_file,'r')as fr, open(id_idx_file,'w')as fw:
            writer = csv.writer(fw,delimiter='\t')
            idx = 0
            for line in fr:
                doc_id = []
                data = json.loads(line)
                doc_id.append(idx)
                if data["text"] == '' and data["title"] == '':
                    continue
                doc_id.append(data["id"])
                writer.writerow(doc_id)
                self.id_dict[data["id"]]=idx
                idx += 1
        print("文書idチェック終わり")
        return

    def create_run(self,id_idx_file,rank_file,run_name,lang):
        with open(id_idx_file,'r')as fi, open(rank_file,'r')as fr, open(f'{run_name}.{lang}.tsv','w')as fw:
            writer = csv.writer(fw,delimiter='\t')
            rank_reader = csv.reader(fr,delimiter='\t')
            id_reader = csv.reader(fi,delimiter='\t')
            id_dict = {}
            for line in id_reader:
                id_dict[line[0]] = line[1]
            for line in rank_reader:
                run_line = []
                run_line.append(line[0])
                run_line.append("Q0")
                run_line.append(id_dict[line[1]])
                run_line.append(line[2])
                run_line.append(line[3])
                run_line.append(run_name)
                writer.writerow(run_line)
        print("run生成終了")
        return

    def query_edit(self,query_file,query_tsv,lang,source):
        with open(query_file,'r')as fr, open(f'{query_tsv}.{lang}.tsv','w')as fw:
            for line in fr:
                topic_line = []
                data = json.loads(line)
                topic_line.append(data["topic_id"])
                if lang not in data["languages_with_qrels"]:
                    continue
                for topic in data["topics"]:
                    if topic["lang"] == lang:
                        if topic["source"] == source:
                            topic_line.append(topic["topic_title"]) 
                            writer = csv.writer(fw,delimiter='\t')
                            writer.writerow(topic_line)
        print("クエリ編集終わり")
        return


    def qrels_edit(self,qrels_file,output_qrels):
        with open(qrels_file,"r")as fr, open(output_qrels,"w")as fw:
            writer = csv.writer(fw,delimiter='\t')
            for line in fr:
                line = line.split()
                line[2] = self.id_dict[line[2]]
                writer.writerow(line)
        return

    def run_edit(self,run_file,output_run):
        with open(run_file,"r")as fr, open(output_run,"w")as fw:
            writer = csv.writer(fw,delimiter='\t')
            for line in fr:
                line = line.split()
                line[2] = self.id_dict[line[2]]
                data = [line[0],line[2],int(line[3])+1]
                writer.writerow(data)
        return

def main():
    parser = argparse.ArgumentParser(description='') 
    parser.add_argument('--doc_tsv', help='')
    parser.add_argument('--doc_file', help='')
    parser.add_argument('--query_tsv', help='')
    parser.add_argument('--query_file', help='')
    parser.add_argument('--id_idx_file', help='')
    parser.add_argument('--lang', help='')  
    parser.add_argument('--source', help='')  
    parser.add_argument('--run_name', help='')
    parser.add_argument('--rank_file', help='')
    args = parser.parse_args()
    de = Dataedit()
    #numbers = [400,350,300]
    #de.doc_edit(args.doc_file,args.doc_tsv)

    langs = ["zho","fas","rus"]
    for lang in langs:
        de.query_edit(query_file=args.query_file,query_tsv=args.query_tsv,source="20220114-scale21-sockeye2-tm1",lang=lang)
    #de.query_edit(args.query_file,args.query_tsv,args.lang,source="")

    #de.id_to_number(args.doc_file, args.id_idx_file)

    #de.create_run(args.id_idx_file,args.rank_file,args.run_name,args.lang) #create_run(self,id_idx_file,rank_file,run_file,run_name):

    #de.id_to_number(args.doc_file, args.id_idx_file)
    #de.qrels_edit(qrels_file="/home/aken12/HC4/resources/hc4/zho/test.qrels.v1-0.txt",output_qrels="/home/aken12/HC4/resources/hc4/zho/test.qrels.marco.tsv")
    #de.run_edit(run_file="/home/aken12/neuCLIR/patapsco/runs/Chinese-aken-run-traditional/results.txt",output_run="/home/aken12/neuCLIR/patapsco/runs/Chinese-aken-run-traditional/results.marco.tsv")

if __name__ == '__main__':
    main()

"""
{
    'id': '34da5fcb-b374-4f93-b443-3c8ce3570c57',
    'cc_file': 'crawl-data/CC-NEWS/2020/03/CC-NEWS-20200318014921-01268.warc.gz',
    'time': '2020-03-18T10:50:04+08:00', 'title': 'NetApp 併購 Talon \r\n強化全域檔案快取 - 財經',
    'text': '雲端資料服務領導廠商NetApp(NASDAQ: NTAP)今日宣布併購次世代軟體定義儲存領域的領導廠商Talon Storage，該解決方案能讓全球化企業經由公有雲集中管理及整合其IT儲存基礎架構。在NetApp Cloud Volumes技術與Talon FAST軟體整合後，企業將可無縫接軌地集中管理雲端資料，並在分公司維持一致的使用體驗。\n\nNetApp雲端資料服務事業部資深副總裁暨總經理Anthony Lye表示：「我們致力於運用Cloud Volumes ONTAP、Cloud Volumes Service、Azure NetApp Files和Cloud Insights等解決方案來持續擴展雲端資料服務內涵，因此非常樂見合併後的新團隊能夠為主要工作負載提供更完善的解決方案潛力。我們與Talon 團隊抱有相同的願景，也就是將非結構化資料的儲存空間統合起來，讓使用者無論在何處工作，都能順暢存取所需的資料，就像資料與使用者在同一個實體地點一般。同時，這不僅不會影響工作流程和使用者體驗，還能以更低的成本達成此目標。」\n\nNetApp併購Talon之後將以領先市場的解決方案，進一步增強公司的雲端資料服務產品組合，以解決所有遠端辦公室和分公司在檔案共享方面所遭遇的挑戰。Talon FAST是一項雲端資料服務，針對ROBO工作負載提供「全域檔案快取」服務，可在我們的公有雲平臺上，將檔案伺服器整合到一個安全、可供全球存取的檔案系統之中。\n\nTalon軟體將與NetApp Cloud Volumes ONTAP、Cloud Volumes Service和Azure NetApp Files解決方案整合，能以更低廉的總體擁有成本 (TCO)，為客戶提供更快邁向公有雲的途徑。欲知詳細資訊，請參訪NetApp Cloud Central\n\n(工商 )',
    'url': 'https://www.chinatimes.com/realtimenews/20200318002095-260410'
    }
"""