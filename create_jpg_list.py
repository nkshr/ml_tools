import os
import sys

if __name__ == "__main__":
    args = sys.argv
    sdir = args[1]
    ofile = args[2]
    f = open(ofile, "w")
    
    for root_dir, dirs, files in os.walk(sdir):
        for file in files:
            if file.lower().endswith((".jpg")):
                abs_path = os.path.abspath(root_dir + "/" + file)
                f.write(abs_path + "\n")

                
