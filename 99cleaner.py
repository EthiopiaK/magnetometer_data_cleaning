'''
This code opens daily magnetometer data, cleans up instrument noises marked by 999, 9999 or 9999.9 and uses linear interpolation to fill in the blank. 
It can look through multiple files under the same folder. 
It outputs the processed files into a separate folder.  
'''
import os 
import time
import numpy as np
import pandas as pd
from itertools import islice 

start_time = time.time()
#============================================================================================================================================================= 
#input and output directories, Output files will be placed in a dedicated folder alongside the input folder. Please update the input directory path with the specific path. 
input_directory = r"C:\Users\documents\inputfile"
output_dir = os.path.join(os.path.dirname(input_directory), "cleaned_files") 
os.makedirs(output_dir, exist_ok = True)

header_length = 17 
#=============================================================================================================================================================

#look through multiple files in the folder, keep date and time information on the input file name but create a new output file 
for input_file in os.listdir(input_directory):
    input_path = os.path.join(input_directory, input_file)
    input_name, input_ext = os.path.splitext(input_file)
    output_file = f"{input_name}_cln{input_ext}"  
    output_path = os.path.join(output_dir, output_file)
    
    #To not use another for loop, we will use itertools
    with open (input_path) as f:
        metadata = list(islice(f, header_length))
     
        #read table and replace 99s with NaNs, so subsequent calculation is not impacted
        df = pd.read_csv(input_path, skiprows = header_length, sep = "\s+")
        col_indices = [3, 4, 5]
        df.iloc[:, col_indices] = df.iloc[:, col_indices].replace(99999.99, np.nan)
        
        # and apply linear extrapolation for each column
        df.iloc[:, col_indices] = df.iloc[:, col_indices].interpolate("linear")

        #Use forward fill and backward fill If any 9999s were at the begining or at the end and were not filled by interpolation
        df.iloc[:, col_indices] = df.iloc[:, col_indices].ffill().bfill()
        
        #recalculate the total magnetic field strength
        cln_columns = df.iloc[:, col_indices].to_numpy()
        df.iloc[:,6] = np.linalg.norm(cln_columns, axis = 1)
                   
        #write this and the metadata in the output file and save
        with open (output_path, "w") as f_out:
            f_out.writelines(metadata)
            df.to_csv(f_out, sep = "\t", index = False, header = True)
end_time = time.time()
time_elapsed = end_time-start_time
print(f"Done!\nTime_elapsed = {time_elapsed} seconds")
 