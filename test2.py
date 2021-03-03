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

print(is_positive_int('+45'))