import csv

filename = "/home/aken12/ColBERT/zho_clir300.tsv" #"/home/aken12/ColBERT/zho_id.tsv"#

def main():
    with open(filename,"r")as f:
        for idx,l in enumerate(f):
            if len(l.split('\t')) != 2: 
                print(len(l.split('\t')))
                print(l)
        return

if __name__ == "__main__":
    main()