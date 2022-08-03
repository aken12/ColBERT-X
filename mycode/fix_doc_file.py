import argparse
from collections import defaultdict   
import json
import random
import csv
import re

def fix_doc(filename,output):
    doc_dict_list = []
    with open(filename,"r")as fr:
        with open(output, "w") as fw:
            for line in fr:
                doc_dict = {}
                line = json.loads(line)
                doc_dict["docid"] = line["id"]
                doc_dict["title"] = line["title"]
                doc_dict["text"] = line["text"][:500]
                doc_dict_list.append(doc_dict)
                json.dump(doc_dict, fw, ensure_ascii=False)
                fw.write('\n')
    print("終わりました")
    return

def jsonl_to_tsv(jsonl_file,doc_tsv,id_tsv):
    comp = re.compile(r"[\r\n\t]")
    with open(jsonl_file,"r")as fr,open(doc_tsv,"w")as f_w,open(id_tsv,'w')as f_id:
        writer_id = csv.writer(f_id,delimiter='\t')
        writer_doc = csv.writer(f_w,delimiter='\t')
        for idx,line in enumerate(fr):
            line_list = []
            line = json.loads(line)
            docid = line["id"]
            content = re.sub(comp,'',line["title"])
            title = re.sub(comp,'',line["text"][:360])
            line_list.append(idx)
            line_list.append(title)
            line_list.append(content)
            writer_id.writerow([idx,docid])
            writer_doc.writerow(line_list)

def main():
    parser = argparse.ArgumentParser(description='') 
    parser.add_argument('--doc_output', help='')
    parser.add_argument('--docs_file', help='')
    args = parser.parse_args()
    output = args.doc_output
    filename = args.docs_file
    #fix_doc(filename,output)
    jsonl_to_tsv(jsonl_file='/home/aken12/HC4/data/fas/hc4_docs.jsonl',doc_tsv='fas_360.tsv',id_tsv='fas_id.tsv')

if __name__ == "__main__":
    main()
    