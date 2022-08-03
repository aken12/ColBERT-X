import argparse
from collections import defaultdict   
import json
import random
import os
import csv
import re


def change(filename,id_file):
    with open(filename,"r")as fr,open(id_file,"r")as f_id,open("new_qrels.tsv","w")as fw:
        id_dict = {}
        writer = csv.writer(fw,delimiter='\t')
        for id_line in f_id:
            id_line = id_line.split('\t')
            id_dict[id_line[1].strip('\n')] = id_line[0]
        for line in fr:
            line = line.split()
            if line[3] != "0":
                qrels_line = [line[0],"0",id_dict[line[2]],"1"]
                writer.writerow(qrels_line)
        return

def main():
    filename = "/home/aken12/HC4/resources/hc4/zho/test.qrels.v1-0.txt"
    id_file = "/home/aken12/ColBERT/test_data/hc4_zho_id.tsv"
    change(filename=filename,id_file=id_file)
if __name__ == '__main__':
    main()