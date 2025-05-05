import pandas as pd
import gzip
from pathlib import Path

# Paths
data_root = Path("data")
output_input = "input.txt"
output_counts = "counts.txt"
output_improper = "improper.txt"

# Helper to strip extra metadata columns
def is_excluded(col):
    exclusions = ['gene_name', 'gene_chr', 'gene_start', 'gene_end', 'strand',
                  'gene_length', 'gene_biotype', 'gene_description', 'locus', 'family',
                  'description', 'fpkm', 'ensembl', 'symbol',
                  'entrezid', 'refseq', 'genename']
    return any(x in col.lower() for x in exclusions)

# Helper: smart decode, use utf-8 or 16 depending on which works
# change depending on if .csv or .txt
def read_compressed_file(path):
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            return pd.read_csv(f, sep='\t', dtype=str)
            # return pd.read_csv(f, sep=',', dtype=str)
    except UnicodeDecodeError:
        with gzip.open(path, 'rt', encoding='utf-16') as f:
            return pd.read_csv(f, sep='\t', dtype=str)
            # return pd.read_csv(f, sep=',', dtype=str)

# Accumulators
input_rows = []
counts = {}
improper = []
all_genes = []
column_order = []

# change depending on if .txt or .csv
for file in sorted(data_root.glob("*.tsv.gz")):
# for file in sorted(data_root.glob("*.txt.gz")):
# for file in sorted(data_root.glob("*.csv.gz")):
    full_name = file.stem  # without .gz
    name_parts = full_name.split('_')
    sample_name = name_parts[0]

    print(f"📄 Processing: {file.name}")

    # Read the file
    try:
        df = read_compressed_file(file)
    except Exception as e:
        print(f"❌ Could not read {file.name}: {e}")
        continue

    if df.empty or df.shape[1] < 2:
        print(f"⚠️ Skipping empty or invalid: {file.name}")
        continue

    df.columns = df.columns.str.strip()
    gene_col = df.columns[0]
    value_cols = [col for col in df.columns[1:] if not is_excluded(col)]

    # Identify the "names" column (case-insensitive match)
    names_col_candidates = [col for col in df.columns if 'name' in col.lower()]
    names_col = names_col_candidates[0] if names_col_candidates else None
    # names_col = df.columns[0]
    identifier_value = ""
    if names_col and names_col in df.columns:
        identifier_value = str(df[names_col].iloc[0]).strip()

    # Prepare column names and input rows
    for col in value_cols:
        column_id = f"{sample_name}_{col}"
        if column_id not in column_order:
            column_order.append(column_id)
        input_rows.append([
            column_id,          # SampleColumn (1st)
            column_id,          # SampleColumn again (2nd)
            identifier_value,   # Identifier from "names" column
            file.name           # Original file name
        ])

    # Process gene counts
    for _, row in df.iterrows():
        identifier = str(row[gene_col]).strip()
        if not identifier or identifier.lower() == gene_col.lower():
            continue

        if identifier.replace("\"", "").startswith("ENS"):
            if identifier not in counts:
                counts[identifier] = {}
                all_genes.append(identifier)
            for col in value_cols:
                column_id = f"{sample_name}_{col}"
                val = str(row.get(col, ""))
                try:
                    counts[identifier][column_id] = int(float(val))
                except ValueError:
                    counts[identifier][column_id] = 0
        else:
            improper.append((identifier, sample_name))

# Write input.txt
pd.DataFrame(input_rows, columns=["SampleColumn", "Replication", "Identifier", "File"]) \
    .to_csv(output_input, sep="\t", index=False)

# Write improper.txt
with open(output_improper, 'w', encoding='utf-8') as f:
    f.write("Identifier\tFile\n")
    for row in improper:
        f.write(f"{row[0]}\t{row[1]}\n")

# Write counts.txt
rows = []
for gene in all_genes:
    row = [gene] + [counts[gene].get(col, 0) for col in column_order]
    rows.append(row)

pd.DataFrame(rows, columns=["Gene"] + column_order).to_csv(output_counts, sep=",", index=False)

print("✅ All done!")

