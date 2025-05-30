import pandas as pd
import gzip
from pathlib import Path
# for beep sound, not needed for functionality
# import winsound

# Paths
data_folder = Path("data")
output_input = "input.txt"
output_counts = "counts.txt"
improper_rows = "improper_rows.txt"
improper_columns = "improper_columns.txt"

# Helper to strip extra metadata columns
def is_excluded(col):
    exclusions = ['gene_name', 'gene_chr', 'gene_start', 'gene_end', 'strand',
                  'gene_length', 'gene_biotype', 'gene_description', 'locus', 'family',
                  'description', 'fpkm', 'ensembl', 'symbol', 'deseq', 'annotation',
                  'entrezid', 'refseq', 'genename', 'idtranscript', 'length', 'class',
                  'family', 'kegg', 'eggnog', 'accid', 'chrom', 'start', 'end', 
                  'e5vscal', 'e5vsdc', 'type', 'chr']
    return any(x in col.lower() for x in exclusions)

def read_compressed_file(path, extension):

    # Read file into DataFrame
    if extension == "xlsx":     
        # Special file handling for Excel
        # Load the Excel file into a DataFrame
        df = pd.read_excel(path, dtype=str, engine='openpyxl')

        # Rename first column gene_id
        df.columns = ['gene_id'] + list(df.columns[1:])

        # Clean headers
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        return df
    elif extension == "xls":
        # Special file handling for old Excel format
        # Load the Excel file into a DataFrame
        df = pd.read_csv(path, dtype=str, sep='\t')

        # Rename first column gene_id
        df.columns = ['gene_id'] + list(df.columns[1:])

        # Clean headers
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        return df
    else:
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
        header = ['gene_id'] + header[1:]

        # Number of columns
        number_of_cols = len(header)

        df = pd.read_csv(path, dtype=str, sep=split_char)
        # from io import StringIO
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str)
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str, usecols=range(0, number_of_cols), skiprows=1, header=None, names=header)
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str, skiprows=1, usecols=range(1,number_of_cols))
        # Clean headers
        df.columns = ['gene_id'] + df.columns.str.strip().str.replace('"', '', regex=False)
        # print(df.columns.tolist())
        return df


# Accumulators
input_rows = []
counts = {}
improper_column = []
improper_row = []
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
    # Gene identifier is likely first column, 0
    gene_col = data_file.columns[0]
    # Value columns are all other columns
    value_cols = [col for col in data_file.columns[1:] if not is_excluded(col)]
    # improper_column_list = [col for col in data_file.columns[1:] if is_excluded(col)]
    # for item in improper_column_list:
    #     improper_column.append(item)
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
            column_id,          # SampleColumn (1st)        col = col.split(':')[0]
            column_id,          # Replication
            identifier_value,   # Identifier from "names" column
            file.name           # Original file name
        ])

    # Process gene counts
    for _, row in data_file.iterrows():
        identifier = str(row[gene_col]).strip()
        # if identifier.startswith("gene"):
        #     identifier = identifier.split(":")[1]
        if not identifier or identifier.lower() == gene_col.lower():
            continue

        # If formatted weird with colon
        # identifier = identifier.split(":")[1] ⚠️ 
        # if identifier.replace("\"", "").startswith("ENS"): 
        if not identifier.replace("\"", "").startswith("17.5"):
            if identifier not in counts:
                counts[identifier] = {}
                all_genes.append(identifier)
            for col in value_cols:
                column_id = f"{sample_name}_{col}"
                val = str(row.get(col, ""))
                try:
                    # below is to combine data. Likely not necessary
                    counts[identifier][column_id] = counts[identifier].get(column_id, 0) + int(float(val))
                except ValueError:
                    # print("NAN error in line " + row + " column " + col)
                    counts[identifier][column_id] = 0
        else:
            improper_row.append((identifier, sample_name))

if __name__ == "__main__":
    # manually change? depending on if .txt or .csv
    for file in sorted(data_folder.glob("*.tsv.gz")):
        process_file(file, "tsv")
    for file in sorted(data_folder.glob("*.xlsx")):
        process_file(file, "xlsx")
    for file in sorted(data_folder.glob("*.xls")):
        process_file(file, "xls")
    for file in sorted(data_folder.glob("*.csv.gz")):
        process_file(file, "csv")
    for file in sorted(data_folder.glob("*.txt.gz")):
        process_file(file, "txt")
    for file in sorted(data_folder.glob("*.RCC.gz")):
        process_file(file, "txt")

    # # Write input.txt
    pd.DataFrame(input_rows, columns=["SampleColumn", "Replication", "Identifier", "File"]).to_csv(output_input, sep="\t", index=False)

    # Write improper_column.txt
    with open(improper_columns, 'w', encoding='utf-8') as f:
        f.write("Identifier\tFile\n")
        for row in improper_column:
            f.write(f"{row[0]}\t{row[1]}\n")

    # Write improper_row.txt
    with open(improper_rows, 'w', encoding='utf-8') as f:
        f.write("Identifier\tFile\n")
        for row in improper_row:
            f.write(f"{row[0]}\t{row[1]}\n")

    # Write counts.txt
    rows = []
    for gene in all_genes:
        row = [gene] + [counts[gene].get(col, 0) for col in column_order]
        rows.append(row)

    print(column_order)
    for x in range(len(column_order)):
        column_order[x] = column_order[x].replace("-", "_").split("/")[-1].split("_")[0]
        # column_order[x] = column_order[x].replace("GSE17900", "")
        # column_order[x] = column_order[x].split(':')[0].split('_')[0].split("/")[-1]
    print(column_order)

    pd.DataFrame(rows, columns=["Gene"] + column_order).to_csv(output_counts, sep=",", index=False)
    # winsound.Beep(1500, 500)  # Frequency in Hz, Duration in milliseconds

    print("✅ All done!")