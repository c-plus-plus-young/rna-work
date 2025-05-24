# File with correct filenames
input = open("input.txt")
# File with correct sample and identifier names, just needs files
new_input = open("new_input.txt")
input.readline()

filenames = []

for line in input:
    filename = line.split("\t")[-1].strip()
    filenames.append(filename)

print(new_input.readline().strip())
curr_line = 0
for line in new_input:
    line = line.strip() + "\t" + filenames[curr_line]
    curr_line += 1
    print(line)

    # Make sure to put output in correct file:
    # > example.txt