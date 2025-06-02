Instructions to run convert4.py:

 - Copy all data into data folder (should be compressed folder containing uncompressed files, if it is a compressed folder containing more compressed folders, extract them all- excel files should not be in a folder). 
 - cd into rna-work folder, then run 'python convert4.py'
 - If output is unexpected, try the following:
   - Change delimiter (some .csv files use \t)
   - Skip first row (may have to manually add headers back in - this is probably the best fix if you get a header misalignment error [header = x and rows = x+1])
   - 
 - Manually verify rows (don't have a good way to check them all, but typically rows starting with ENS or some short string of characters like ABCDE are appropriate, most everything else is not
 - Check improper_columns.txt to make sure all looks good (can remove columns from banlist at top of file if not)

To construct input.txt:
 - Typically needs to be done manually since data files don't contain all the needed information. Just copy the 'samples' section from the appropriate page on GEO, duplicate the sample column (tab selection mode [Shift+Alt on vscode] is your friend)
   - Can use input_conversion.py or accession_conversion.py to help
   - 
 - Make sure to save file before copying into appropriate folder
