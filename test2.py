import os, glob

def bylength(word1,word2):
    return len(word2)-len(word1)

def sortlist(a):
    a.sort(cmp=bylength)
    return a

os.chdir("\\\\sieve\\scans")
files = glob.glob("*.pdf")
for file in list(reversed(sorted(files, key=len)))[:5]:
    print(file)