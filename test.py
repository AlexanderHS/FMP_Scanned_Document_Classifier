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
            guess = text.strip().replace(os.linesep, ' ').split(' ')[index].strip()
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
            guess = text.strip().replace(os.linesep, ' ').split(' ')[index].strip()
        except IndexError:
            return None
        index += 1
    return guess

text = """
DRE420S

Disposable Resectoscope Electrode - 24 Fr 5mm Ball - Rev: 3

30� - Single Stem Monopolar - Storz Compatible
2009011

Work Order No: AW-43489 Batch No:

Date Issued:

9/06/2020 10:11:08 AM

This Document Refers To:

Expiry Date:



Samples Required (units)

| Quantity Required:





Sign/Date for Closure:







Release Check

26.0%. WL
Quality Assurance Release Check List / Sign Off

Complies - doc / evidence
present and complete









Yes

N/A

Reviewed By
Initials/Date





Product Inspection
Finished Product Inspection (QFM311, QFMO70,
QWI088)




Package Integrity testing (QFM113, QWI014)

|
Ea

O
O

O





Production Order
Check for no blanks, all signatures present, cross
outs noted and fixed to GMP standards and a

reason documented where needed










Check in process tests/inspections performed and
within limits

O

O





Labelling
Check the Batch number, expiry date and product
number, box and product labelling, correlate to PO
and actual contents of box








Sterilisation

Cycle No: 2.0246|

Cycle parameters/documentation (sterilization
graphs/printouts)




Bacterial indicators

Od

OO



Clean Room- Magnehelic Gauge Monitoring

Review log book readings



aa











JB F [09/2020













Deviation and actions














Number of Units for release: 4s"



Aware Inventory Transfer Number: IT-



31/08/2020 7:50:29 AM

Printed:

Number of Boxes for release: 24 Final Batch Approval:

Approved By:_' Q B Utiar Date: 8/09/2620 ,

ANS03\



es)! No



Page 1 of 6

"""

print(get_batch(text))
print(get_aw(text))