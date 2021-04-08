import glob
import os

os.chdir("\\\\sieve\\scans")
print(glob.glob("*.jpeg"))
for i in glob.glob("*.jpeg"):
    os.remove(i)
"""


print(glob.glob("\\\\sieve\\scans\\*.jpeg"))


os.chdir("\\\\sieve\\scans")
"""
print(glob.glob("*.jpeg"))