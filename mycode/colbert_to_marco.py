import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description='') 
    parser.add_argument('--rank_tsv', help='')
    parser.add_argument('--output_file', help='')
    args = parser.parse_args() 

    ranking = args.rank_tsv
    output = args.output_file
    with open(ranking,'r')as fr, open(output,'w')as fw:
        for line in fr:
            data = line.split()
            _ = data.pop(-1)
            writer = csv.writer(fw,delimiter='\t')
            writer.writerow(data)
    print("終了")
    return 

if __name__ == '__main__':
    main()