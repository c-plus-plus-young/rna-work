input = open("input.txt")
input.readline()

filename = "GSE234489_readcounts_hg19.tsv.gz"

print("SampleColumn" + "\t" + "Replication" + "\t" + "Identifier" + "\t" + "File")
currentLine = 0
for line in input:
    if currentLine % 2 == 0:
        print(line.replace("\n", "")) 
    currentLine += 1
