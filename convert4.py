import pandas as pd
import gzip
from pathlib import Path
# for beep sound, not needed for functionality
# import winsound

# Paths
data_folder = Path("data")
output_input = "input.txt"
output_counts = "counts.txt"
improper_rows = "improper.txt"

# Helper to strip extra metadata columns
def is_excluded(col):
    exclusions = ['gene_name', 'gene_chr', 'gene_start', 'gene_end', 'strand',
                  'gene_length', 'gene_biotype', 'gene_description', 'locus', 'family',
                  'description', 'fpkm', 'ensembl', 'symbol',
                  'entrezid', 'refseq', 'genename', 'idtranscript']
    return any(x in col.lower() for x in exclusions)

def read_compressed_file(path, extension):

    if extension == "txt" or extension == "tsv":
        split_char = "\t"
    else:
        split_char = ","

    try:
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print("Error, file not utf-8. Opening as utf-16")
        with gzip.open(path, 'rt', encoding='utf-16') as f:
            lines = f.readlines()

    # If first line has no gene_id, insert it
    header = lines[0].strip().split(split_char)
    if not header[0].lower().startswith('gene'):
        header = ['gene_id'] + header
        lines[0] = split_char.join(header) + '\n'

    # Read file into DataFrame
    if extension == "xlsx":     
        # Special file handling for Excel
        # Load the Excel file into a DataFrame
        df = pd.read_excel(path, dtype=str)

        # If the first column isn't labeled 'gene_id', rename it
        if not df.columns[0].lower().startswith('gene'):
            df.columns = ['gene_id'] + list(df.columns[1:])

        # Clean headers
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        return df
    else:
        from io import StringIO
        df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str)
        # Clean headers
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        # print(df.columns.tolist())
        return df


# Accumulators
input_rows = []
counts = {}
improper = []
all_genes = []
column_order = []

def process_file(file, extension):
    full_name = file.stem  # without .gz
    name_parts = full_name.split('_')
    sample_name = name_parts[0] if name_parts else full_name

    print(f"📄 Processing: {file.name}")

    # Read the file
    try:
        data_file = read_compressed_file(file, extension)
    except Exception as e:
        print(f"❌ Could not read {file.name}: {e}")
        return

    # Skip empty or one-dimensional files
    if data_file.empty or data_file.shape[1] < 2:
        print(f"⚠️ Skipping empty or invalid: {file.name}")
        return

    data_file.columns = data_file.columns.str.strip()
    gene_col = data_file.columns[0]
    value_cols = [col for col in data_file.columns[1:] if not is_excluded(col)]

    # Identify the "names" column (case-insensitive match)
    names_col_candidates = [col for col in data_file.columns if 'name' in col.lower()]
    names_col = names_col_candidates[0] if names_col_candidates else None
    identifier_value = ""
    if names_col and names_col in data_file.columns:
        identifier_value = str(data_file[names_col].iloc[0]).strip()

    # Prepare column names and input rows
    for col in value_cols:
        column_id = f"{sample_name}_{col}"
        if column_id not in column_order:
            column_order.append(column_id)
        input_rows.append([
            column_id,          # SampleColumn (1st)
            column_id,          # Replication
            identifier_value,   # Identifier from "names" column
            file.name           # Original file name
        ])

    # Process gene counts
    for _, row in data_file.iterrows():
        identifier = str(row[gene_col]).strip()
        if not identifier or identifier.lower() == gene_col.lower():
            continue

        # If formatted weird with colon
        # identifier = identifier.split(":")[1]
        if identifier.replace("\"", "").startswith("ENS"):
            if identifier not in counts:
                counts[identifier] = {}
                all_genes.append(identifier)
            for col in value_cols:
                column_id = f"{sample_name}_{col}"
                val = str(row.get(col, ""))
                try:
                    # counts[identifier][column_id] = int(float(val))
                    # below is to combine data. Likely not necessary
                    counts[identifier][column_id] = counts[identifier].get(column_id, 0) + int(float(val))
                except ValueError:
                    print("NAN error in line " + row + " column " + col)
                    counts[identifier][column_id] = 0
        else:
            improper.append((identifier, sample_name))

if __name__ == "__main__":
    # manually change? depending on if .txt or .csv
    for file in sorted(data_folder.glob("*.tsv.gz")):
        process_file(file, "tsv")
    for file in sorted(data_folder.glob("*.xlsx")):
        process_file(file, "xlsx")
    for file in sorted(data_folder.glob("*.csv.gz")):
        process_file(file, "csv")
    for file in sorted(data_folder.glob("*.txt.gz")):
        process_file(file, "txt")

    # # Write input.txt
    pd.DataFrame(input_rows, columns=["SampleColumn", "Replication", "Identifier", "File"]) \
        .to_csv(output_input, sep="\t", index=False)

    # Write improper.txt
    with open(improper_rows, 'w', encoding='utf-8') as f:
        f.write("Identifier\tFile\n")
        for row in improper:
            f.write(f"{row[0]}\t{row[1]}\n")

    # Write counts.txt
    rows = []
    for gene in all_genes:
        row = [gene] + [counts[gene].get(col, 0) for col in column_order]
        rows.append(row)

    pd.DataFrame(rows, columns=["Gene"] + column_order).to_csv(output_counts, sep=",", index=False)
    # winsound.Beep(1500, 500)  # Frequency in Hz, Duration in milliseconds

    print("✅ All done!")