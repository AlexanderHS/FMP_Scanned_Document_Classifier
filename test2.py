from classify import COLLECT_QTY
import os, glob

def bylength(word1,word2):
    return len(word2)-len(word1)

def sortlist(a):
    a.sort(cmp=bylength)
    return a



def is_positive_int(s):
    try: 
        _ = int(s)
        if _ < 0:
            return False
        int(s[:1])
        return True
    except ValueError:
        return False

COLLECT_QTY = 1
os.chdir("\\\\sieve\\scans")
if os.path.exists('rotated.pdf'):
    os.remove('rotated.pdf')
for file in glob.glob("*.jpg"):
    os.remove(file)
files = glob.glob("*.pdf")
#for file in list((sorted(files, key=len)))[:COLLECT_QTY]:
for file in list(reversed(sorted(files, key=len)))[:COLLECT_QTY]:
    print(file)