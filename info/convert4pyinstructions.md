Instructions to run convert4.py:

 - Copy all data into data folder (should be compressed folder containing uncompressed files, if it is a compressed folder containing more compressed folders, extract them all- excel files should not be in a folder). 
 - cd into rna-work folder, then run 'python convert4.py'
 - If output is unexpected, try the following:
   - Change delimiter (some .csv files use \t, some txt files use spaces)
   - Skip first row (may have to manually add headers back in - this is probably the best fix if you get a header misalignment error [header = x and rows = x+1])
 - Manually verify rows (don't have a good way to check them all, but typically rows starting with ENS or some short string of characters like ABCDE are appropriate, most everything else is not 
 - Check improper_columns.txt to make sure all looks good (can remove columns from banlist at top of file if not)
 - For RCC files:
   - Run gunzip on all data files
   - Run rcc-adapter.py from project root folder
   - Run as normal

To construct input.txt:
 - Typically needs to be done manually since data files don't contain all the needed information. Just copy the 'samples' section from the appropriate page on GEO, duplicate the sample column (tab selection mode [Shift+Alt on vscode] is your friend)
   - Can use input_conversion.py, accession_conversion.py, add_filename.py, and delete_odd_lines.py to help (these require the output to be redirected to a new file- for example you'd do 'info/delete_odd_lines.py > new_input.txt' 
 - Make sure to save file before copying into appropriate folder



QA:
Q: What if it's taking too long?
A: You can try running it on a faster computer, but it will typically just take a while, particularly if there is a lot of data. If you notice NAN error keeps getting printed, this significantly slows down the process. Fix the NAN error to improve performance (typically need to exclude an additional column)
