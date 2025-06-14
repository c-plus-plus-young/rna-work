input = open("input.txt")
input.readline()

filename = "GSE234489_readcounts_hg19.tsv.gz"

print("SampleColumn" + "\t" + "Replication" + "\t" + "Identifier" + "\t" + "File")
for line in input:
    print(line.replace("\n", "") + "\t" + filename) 
