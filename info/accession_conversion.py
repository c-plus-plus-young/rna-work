# # File with all data
# input = open("sample.csv")
# input.readline()

# filename = "GSE177040_Haeder_etal_counts.tsv.gz"

# print("SampleColumn" + "\t" + "Replication" + "\t" + "Identifier" + "\t" + "File")
# for line in input:
#     line_parts = line.split(",")
#     print(line_parts[0] + "\t" + line_parts[0] + "\t" + line_parts[1].replace("\"", "") + "\t" + filename)

# # Make sure to put output in correct file:
# # > example.txt

# For data where all info is in filename:
input = open("old_input.txt")
input.readline()

filename = "GSE234489_readcounts_hg19.tsv.gz"

print("SampleColumn" + "\t" + "Replication" + "\t" + "Identifier" + "\t" + "File")
for line in input:
    filename = line.split("\t")[-1].replace("\n", "")
    line_parts = filename.split("_")
    # print(line_parts)
    print(line_parts[0] + "\t" + line_parts[0] + "\t" + line_parts[1] + "_" + line_parts[2] + "_" + line_parts[3] + "\t" + filename)


# Make sure to put output in correct file:
# > example.txt
