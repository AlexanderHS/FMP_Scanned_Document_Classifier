import os

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def get_aw(text):
    if 'Work Order No:' not in text:
        return None
    guess = ''
    index = 0
    while not (guess.startswith('AW-') and is_int(guess[4:])):
        try:
            guess = text.split('Work Order No:')[1].strip().replace(os.linesep, ' ').split(' ')[index].strip()
        except IndexError:
            return None
        index += 1
    return guess

def get_batch(text):
    if 'Batch No:' not in text:
        return None
    guess = ''
    index = 0
    while len(guess) < 7 or not is_int(guess[0:4]):
        try:
            guess = text.split('Batch No:')[1].strip().replace(os.linesep, ' ').split(' ')[index].strip()
        except IndexError:
            return None
        index += 1
    return guess

text = """
DRE9110 Disposable Resectoscope Electrode - 24 Fr Cutting Revi3 Page 1 of 6
Loop 90� - Single Stem Bipolar - Olympus Compatible

Work Order No: AW-43487 Batch No: 2009009 Expiry Date: Sep 2023

Date Issued: 9/06/2020 10:11:10AM | This Document Refers To:



Samples Required (units) Quantity Required:





Sign/Date for Closure:



Quality Assurance Release Check List / Sign Off

Complies - doc / evidence

Release Check present and complete Reviewed By







Yes No N/A Initials/Date
Product Inspection
Finished Product Inspection (QFM311, QFMO070,

QWI088) eal O
Package Integrity testing (QFM113, QWI014) cr oO Cl



Production Order
Check for no blanks, all signatures present, cross
outs noted and fixed to GMP standards and a
reason documented where needed

Check in process tests/inspections performed and
within limits



Labelling
Check the Batch number, expiry date and product
number, box and product labelling, correlate to PO
and actual contents of box



Sterilisation

Cycle No:___ 202 4b]

Cycle parameters/documentation (sterilization
graphs/printouts)

Bacterial indicators



Clean Room- Magnehelic Gauge Monitoring

Review log book readings









Deviation and actions





Number of Boxes for release: Vt Final Batch Approval: No

Number of Units forrelease: =O

Approved By: ( 14 uterr Date: R/OF ore

Aware Inventory Transfer Number: HSole



Printed: 31/08/2020 7:49:42 AM


"""

print(get_batch(text))
print(get_aw(text))