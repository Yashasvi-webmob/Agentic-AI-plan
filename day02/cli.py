import argparse
from parser import parse_line
from stats import summarize

def main()->None:
   ap = argparse.ArgumentParser(description="Parsing File Args")
   ap.add_argument(path)
   ap.add_argument("--top",type=int,default=5)
   args = ap.parse_args()
   print(args.top, args.path)
   bad_records = list()
   records = list()
   with open("sample.jsonl", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            record = parse_line(line, line_no)
            if record is None:
                bad_records.append(line_no)
            else:
                records.append(record)
    
            
    
    

if __name__ == "__main__":
    main()