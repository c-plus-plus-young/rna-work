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
    # may need to add 'total', 'gene', 'go', 'pos', 'end', and 'ec' - but leaving them off bc ec was in infected which is needed
    exclusions = ['gene_name', 'gene_chr', 'gene_start', 'gene_end', 'strand',
                  'gene_length', 'gene_biotype', 'gene_description', 'locus', 'family',
                  'description', 'fpkm', 'ensembl', 'symbol', 'deseq', 'annotation',
                  'entrez', 'refseq', 'genename', 'idtranscript', 'length', 'class',
                  'family', 'kegg', 'eggnog', 'accid', 'chrom', 'start', 
                  'e5vscal', 'e5vsdc', 'type', 'chr', 'nearest', 'idgene_id', 'pvalue',
                  'a_vs_b', 'unique', 'region', 'tpm', 'rpkm', 'ensembl', 'unnamed', 
                  'expression value', 'exons', 'gene id', 'transcripts', 'exon', 'intron',
                  'gene_type', 'expression', 'gene-name', 'width', 'transcript', 
                  'coverage', 'ref', 'uniprot', 'position', 'symbol', 'description',
                  'Gene Name', 'Gene Alias', 'geneid', 'genename', 'refseq',
                  'name', 'direction', 'undetermined', 'tmm', 'chr', 'null', 'id',
                  'genome', 'pos', 'end', 'alias', 'accession']
    if any(x in col.lower() for x in exclusions):
        print(col)
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
    elif extension == "rcc":
        with open(path, 'rt', encoding='utf-8') as f:
                lines = f.readlines()

        # If first line has no gene_id, insert it
        header = lines[0].strip().split(",")
        header = ['gene_id'] + header[0:]

        # Number of columns
        number_of_cols = len(header) - 1
        print("Number of columns: " + str(number_of_cols))

        # This is the best one for most data files - , skiprows=1, usecols=range(1, number_of_cols -1)
        df = pd.read_csv(path, dtype=str, sep=",", usecols=range(1, number_of_cols))
        # Clean headers comment this out if you comment out the one above
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        
        return df
    else:
        if extension == "txt" or extension == "tsv":
            split_char = "\t"
        else:
            split_char = ","
        try:
            # print("trying utf-8")
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
        # except BaseException as e:
        #     print(e)
        except UnicodeDecodeError:
            print("Error, file not utf-8. Opening as utf-16")
            with gzip.open(path, 'rt', encoding='utf-16') as f:
                lines = f.readlines()

        # If first line has no gene_id, insert it
        header = lines[0].strip().split(split_char)
        header = ['gene_id'] + header[0:]

        # Number of columns
        number_of_cols = len(header) - 1
        print("Number of columns: " + str(number_of_cols))
        
        from io import StringIO
        
        # This one is best if there are no headers:
        # df = pd.read_csv(StringIO(''.join(lines)), dtype=str, sep=split_char, header=None, names=["Gene", str(path).split("/")[-1]])

        # Good for misaligned header (too few columns in header)
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str, usecols=range(0, number_of_cols), skiprows=1, header=None, names=header)
        
        # If two header rows and two gene ids
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str, skiprows=1, usecols=range(1,number_of_cols - 1))

        # Unsure if this is useful
        # df = pd.read_csv(StringIO(''.join(lines)), sep=split_char, dtype=str, header=None, names=header)

        # This is the best one for most data files - , skiprows=1, usecols=range(1, number_of_cols -1)
        df = pd.read_csv(path, dtype=str, sep=split_char)
        # Clean headers comment this out if you comment out the one above
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        
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
    sample_name = full_name

    print(f"📄 Processing: {file.name}")

    # Read the file
    try:
        data_file = read_compressed_file(file, extension)
    except Exception as e:
        print(f"❌ Could not read {file.name}: {e}")
        return

    # Skip empty or one-dimensional files
    if data_file.empty:
        print(f"⚠️ Skipping empty file: {file.name}")
        return
    elif data_file.shape[1] < 2:
        print(f"⚠️ Skipping invalid file (too small): {file.name}")
        return

    # data_file.columns = data_file.columns.str.strip()

    # Gene identifier is likely first column, 0
    gene_col = data_file.columns[0]
    # Value columns are all other columns
    value_cols = [col for col in data_file.columns[1:] if not is_excluded(col)]
    # improper_column_list = [col for col in data_file.columns[1:] if is_excluded(col)]
    # for item in improper_column_list:
    #     improper_column.append(item)
    # Identify the "names" column (case-insensitive match)
    names_col_candidates = []
    names_col = names_col_candidates[0] if names_col_candidates else None
    identifier_value = ""
    if names_col and names_col in data_file.columns:
        identifier_value = str(data_file[names_col].iloc[0]).strip()

    # Prepare column names and input rows
    for col in value_cols:
        # Switch to {sample_name} if sample names are filenames
        # column_id = f"{sample_name}"
        column_id = f"{col}"
        # if col == "TNFa":
        #     column_id = f"{col}_{sample_name}"
        # else:
        #     column_id = f"{col}"
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
        identifier = identifier.split(":")[-1]
        identifier = identifier.split("|")[-1]
        # identifier = identifier.split(",")[0]
        if (not identifier.replace("\"", "").startswith("ssc") 
            and not identifier.replace("\"", "").startswith("ERCC") 
            and not identifier.replace("\"", "").startswith("novel") 
            and not identifier.replace("\"", "").startswith("CTRG") 
            and not identifier.replace("\"", "").startswith("TERG")
            and not identifier.replace("\"", "").startswith("17.5")
            and not identifier.replace("\"", "").startswith("__no_feature") 
            and not identifier.replace("\"", "").startswith("__ambiguous") 
            and not identifier.replace("\"", "").startswith("__too_low") 
            and not identifier.replace("\"", "").startswith("__not_aligned")
            and not identifier.replace("\"", "").startswith("__alignment")
            and not identifier.replace("\"", "").startswith("3")
            and not identifier.replace("\"", "").startswith("5-H") 
            and not identifier.replace("\"", "").startswith("bA") 
            and not identifier.replace("\"", "").startswith("RPX-") 
            and not identifier.replace("\"", "").startswith("LINC")
            and not identifier.replace("\"", "").startswith("LOC")
            and not identifier.replace("\"", "").startswith("loc")
            and not identifier.replace("\"", "").startswith("XLOC")
            and not identifier.replace("\"", "").startswith("MIR") 
            and not identifier.replace("\"", "").startswith("TRNA")
            and not identifier.replace("\"", "").startswith("SNORD")
            and not identifier.replace("\"", "").startswith("SNORA")
            and not identifier.replace("\"", "").startswith("GS1-")
            and not identifier.replace("\"", "").startswith("RP11-")
            and not identifier.replace("\"", "").startswith("hsa")
            and not identifier.replace("\"", "").startswith("snR")
            and not identifier.replace("\"", "").startswith("mg")
            and not identifier.replace("\"", "").startswith("MSTRG")
            and not identifier.replace("\"", "").startswith("MERGE")
            and not identifier.replace("\"", "").startswith("NEG")
            and not identifier.replace("\"", "").startswith("POS")
            and not identifier == ""
            and not "Rik" in identifier
            and not "no" in identifier
            and not "ambiguous" in identifier
            and not "low" in identifier
            and not "align" in identifier
            and not "unmapped" in identifier
            and not "multimapping" in identifier
            and not (len(identifier) > 3 and identifier.replace("\"", "").startswith("RP") and identifier[2].isdigit() and identifier[3] == "-")
            and not identifier[0].isdigit()
            and not ("orf") in identifier):

            identifier = identifier.split("|")[-1].replace("\"", "")

            if identifier.split(".")[-1].isdigit:
                identifier = identifier.split(".")[0]

            if identifier not in counts:
                counts[identifier] = {}
                all_genes.append(identifier)
            for col in value_cols:
                # column_id = f"{sample_name}"
                column_id = f"{col}"
                # if col == "tnfa":
                #     column_id = f"{col}_{sample_name}"
                # else:
                #     column_id = f"{col}"
                val = str(row.get(col, ""))
                # if val.isdigit:
                try:
                    # below is to combine data. Likely not necessary
                    counts[identifier][column_id] = counts[identifier].get(column_id, 0) + int(float(val))
                except ValueError:
                # else:
                    print("NAN error in line " + row + " column " + col)
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
    for file in sorted(data_folder.glob("*.RCC")):
        process_file(file, "rcc")
    for file in sorted(data_folder.glob("*.tab.gz")):
        process_file(file, "tsv")
    for file in sorted(data_folder.glob("*.gct.gz")):
        process_file(file, "tsv")

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
    rows = []
    for gene in all_genes:
        row = [gene] + [counts[gene].get(col, 0) for col in column_order]
        rows.append(row)

    print(column_order)
    for x in range(len(column_order)):
        column_order[x] = (column_order[x].replace("-", "_")
                           .replace(".csv", "").replace(".txt", "")
                           .replace(".tsv", "").replace(" Read Count", "")
                           .replace(".out", "").replace(".tab", "")
                           .replace(".hg38.bed.anno.count", "")
                           .replace(".count", "").replace(".stats", "")
                           .replace("\"", "").replace(".bam", "")
                           .replace(".sortedByCoord", "")
                           .replace(":read count", "").replace(".sam", "")
                           .replace("filtered", "").split("/")[-1])
        # column_order[x] = column_order[x].replace("GSE17900", "")
        # column_order[x] = column_order[x].split(':')[0].split('_')[0].split("/")[-1]
    print(column_order)

    pd.DataFrame(rows, columns=["Gene"] + column_order).to_csv(output_counts, sep=",", index=False)
    # winsound.Beep(1500, 500)  # Frequency in Hz, Duration in milliseconds

    print("✅ All done!")