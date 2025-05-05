import pandas as pd
from pathlib import Path

# Paths
data_dir = Path("data")
output_input_file = "input.txt"
output_counts_file = "counts.txt"
output_improper_file = "improper.txt"

# Exclusion rules for non-numeric metadata columns
exclusion_keywords = [
    'gene', 'strand', 'start', 'end', 'length', 'biotype', 'description', 'chr', 'family'
]

# Output containers
input_rows = []
counts_dict = {}
improper_rows = set()
all_genes = set()

def read_file_safely(filepath):
    try:
        return pd.read_csv(filepath, sep="\t", dtype=str, encoding='utf-8')
    except UnicodeError:
        return pd.read_csv(filepath, sep="\t", dtype=str, encoding='utf-16')

def is_excluded_column(col_name):
    return any(keyword in col_name.lower() for keyword in exclusion_keywords)

# Process each file
for filepath in data_dir.glob("*.txt"):
    full_filename = filepath.name
    raw_name = filepath.stem
    simple_name = raw_name.split('_')[0]
    tar_gz_name = raw_name + ".tar.gz"

    input_rows.append([simple_name, simple_name, "", tar_gz_name])

    try:
        df = read_file_safely(filepath)
    except Exception as e:
        print(f"Error reading {filepath.name}: {e}")
        continue

    if df.empty or df.shape[1] < 2:
        continue

    df.columns = [col.strip() for col in df.columns]
    df = df.dropna(how='all')

    gene_column = df.columns[0]

    # Identify valid countable columns (not excluded)
    count_columns = [col for col in df.columns[1:] if not is_excluded_column(col)]

    for _, row in df.iterrows():
        identifier = str(row[gene_column]).strip()

        if not identifier or identifier.lower() == gene_column.lower():
            continue

        # Collect values from countable columns
        count_values = []
        for col in count_columns:
            val = str(row.get(col, "")).strip()
            try:
                count_values.append(float(val))
            except ValueError:
                count_values.append(0)

        count = int(sum(count_values))

        if identifier.startswith("ENS"):
            all_genes.add(identifier)
            if identifier not in counts_dict:
                counts_dict[identifier] = {}
            counts_dict[identifier][simple_name] = count
        else:
            improper_rows.add((identifier, simple_name))


# Write input.txt
input_df = pd.DataFrame(input_rows, columns=["SampleName", "Replication", "Identifier", "File"])
input_df.to_csv(output_input_file, sep="\t", index=False)

# Write improper.txt
with open(output_improper_file, "w", encoding="utf-8") as f:
    f.write("Identifier\tFile\n")
    for identifier, file_stem in sorted(improper_rows):
        f.write(f"{identifier}\t{file_stem}\n")

# Write counts.txt
file_names = sorted({row[0] for row in input_rows})
rows = []

for gene in sorted(all_genes):
    row = [gene]
    for fname in file_names:
        row.append(counts_dict.get(gene, {}).get(fname, 0))
    rows.append(row)

counts_df = pd.DataFrame(rows, columns=["Gene"] + file_names)
counts_df.to_csv(output_counts_file, sep="\t", index=False)
