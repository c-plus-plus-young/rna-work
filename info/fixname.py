# File with incorrect first row
counts = open("counts.txt")
line1 = counts.readline().replace("GSE130124_", "").strip()
print(line1)

for line in counts:
    line = line.strip()
    print(line)

    # Make sure to put output in correct file:
    # > example.txt