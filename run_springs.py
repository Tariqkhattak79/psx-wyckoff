import os, subprocess, sys 
files = [f[:-4] for f in os.listdir("data") if f.endswith(".csv")] 
subprocess.run([sys.executable, "detect_spring.py"] + files) 
