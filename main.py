import Functions
import sys
from os.path import exists

if __name__ == "__main__":
    file = ""
    if len(sys.argv) == 1:
        print("No .xlsx-file supplied as argument.", file=sys.stderr)
        exit(1)
    else:
        file = sys.argv[1]
        if not exists(file):
            print(f"File {file} not found.")
            exit(1)
        
        if not file.endswith(".xlsx"):
            print(f"File {file} is not an .xlsx file.")
            exit(1)

    Functions.loadSettings()
    events = Functions.loadData(file)
    Functions.writeCertificates(events)