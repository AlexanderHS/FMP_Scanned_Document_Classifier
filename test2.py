import glob
import os
import datetime

os.chdir("\\\\sieve\\scans")
print(glob.glob("*.jpeg"))
for i in glob.glob("*.jpeg"):
    os.remove(i)
"""


print(glob.glob("\\\\sieve\\scans\\*.jpeg"))


os.chdir("\\\\sieve\\scans")
"""
print(glob.glob("*.jpeg"))

guess = '2101001'

try:
    year_no = int(guess[0:2])
    current_two_digit_year = int(str(datetime.datetime.now().year)[2:4])
    if current_two_digit_year < year_no:
        raise RuntimeError from None
except:
    guess = '1'

print(guess)