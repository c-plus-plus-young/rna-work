# Takes in an RCC file, removes HTML syntax leaving only data frame
from pathlib import Path
data_folder = Path("data")

for file in sorted(data_folder.glob("*.RCC")):
    has_hit_start = False
    has_hit_end = False
    with open(file, 'r', encoding='ascii') as f:
        lines = f.readlines()

    with open(file, 'w', encoding='ascii') as f:
        for line in lines:
            if "</Code_Summary>" in line:
                has_hit_end = True

            if has_hit_start and not has_hit_end:
                f.write(line)

            if "<Code_Summary>" in line:
                has_hit_start = True