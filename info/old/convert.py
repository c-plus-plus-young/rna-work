import sys
import os

import pandas as pd



encodings = ["utf-8","utf-16"]
def tryEncodings(file):
    for enc in encodings:
        try:
            f = open(file, "r", encoding=enc)
            f.readline()
            return enc
        except UnicodeError:
            continue


def txtToCSV(file):
    f = pd.read_table(file)
    print(f)


# def convertToCSV(file):
#     currentRow = 0
#
#     enc = tryEncodings(file)
#     f = open(file, encoding=enc)
#
#
#     if os.path.exists("counts.csv"):
#         os.remove("counts.csv")
#
#     improperNames = open("improper.txt", "a")
#
#     newfile = open("counts.csv", "x", encoding="utf-8")
#     for line in f:
#         line = line.replace("\n", "")
#         items = line.split("\t")
#
#         # verify row
#         # print row
#         if currentRow != 0:
#             if "ENS" in items[0]:
#                 newfile.write(",".join(items) + "\n")
#             else:
#                 # keep track of unused rows
#                 improperNames.write(items[0] + " " + file + "\n")
#
#         else:
#             newfile.write("Gene,")
#             for item in items[1:]:
#                 newfile.write(item + ",")
#             newfile.write("\n")
#         currentRow += 1
#
#     f.close()
#     newfile.close()
#     improperNames.close()

if __name__ == '__main__':
    # convertToCSV(sys.argv[1])
    txtToCSV(sys.argv[1])
