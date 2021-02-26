import os

from pytesseract.pytesseract import TesseractError
from unidecode import unidecode


def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def get_aw(text):
    if 'Work Order' not in text:
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
    if 'Batch' not in text:
        return None
    guess = ''
    index = 0
    while len(guess) < 7 or not is_int(guess[0:7]):
        print('considering guess: ' + guess)
        try:
            guess = text.strip().replace(os.linesep, ' ').split(' ')[index].strip()
        except IndexError:
            return None
        index += 1
    return guess

def remove_weird(text):
    return unidecode(text)

text = """
b"DOT9008 Disposable Oxygen Tubing - Smooth Bore: 8m Revi 8 'Page 1 of 6\n\n   \n\n \n\nWork Order No: AW-44507 Batch No: 2011314 Expiry Date: Nov 2025\n\nDate Issued: 16/10/2020 11:38:43 AM This Document Refers To: PWI 145\n\n \n\n \n\nSamples Required (units) Quantity Required: 600\n\n \n\n \n\nSign/Date for Closure:\n\n \n\nQuality Assuranee Release Check List / Sign Off\n\nComplies - doc / evidence |\npresent and complete Reviewed By\n\nRelease Check see\nNo N/A Initials/Date\n\n \n\n \n\nYes\nProduct Inspection\nFinished Product Inspection (QFM311, QFMO070, ee Ol\n\nQwiogs)\noOo a\n\nPackage Integrity testing (QFM113, QWI014)\n\n \n\nProduction Order\nCheck for no blanks, all signatures present, cross\nouts noted and fixed to GMP standards and a\nreason documented where needed\n\nCheck in process tests/inspections performed and\nwithin limits\n\n \n\nLabelling\nCheck the Batch number, expiry date and product\nnumber, box and product labelling, correlate to PO\nand actual contents of box\n\n \n\nSterilisation\nCycle No:\n\nCycle parameters/documentation (sterilization\ngraphs/printouts)\n\nBacterial indicators\n\n \n\nClean Room- Magnehelic Gauge Monitoring\n\nReview log book readings\n\n \n\n \n\n \n\n \n\nDeviation and actions\n\n \n\n \n\nNumber of Boxes for release: {2 Final Batch Approval: (fo No\n\nNumber of Units for release: 600\n\nApproved By: EUR AZ uticn Date: 2}2} 2020\n\nAware Inventory Transfer Number: I#;_ (NVA O(33-4C/ 34\n\n \n\nPrinted: 26/11/2020 7:37:21 AM\n\x0c'
"""
text = remove_weird(text)

import pdf2image
import pytesseract
from pdf2image import convert_from_path
from PIL import Image 

def get_batch_aw(pdf_file):
    pages = convert_from_path(pdf_file, 500)
    image_counter = 1
    for page in pages:
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1
    filelimit = image_counter-1
    output_text = ''
    for i in range(1, filelimit + 1):
        filename = "page_"+str(i)+".jpg"
        print('looking at {}, {}.'.format(pdf_file, filename))
        try:
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace('-\n', '')
            batch = get_batch(text)
            aw = get_aw(text)
            if batch is not None and aw is not None:
                return batch, aw
            #print(text)
            #print('output_text is now {} lines.'.format(len(output_text)))
        except Exception as e:
            # do nothing
            print ('Exception: {}'.format(e))
    
    mydir = os.getcwd()
    filelist = [ f for f in os.listdir(mydir) if f.endswith(".jpg") ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
    return None, None

#print(get_batch(text))
#print(get_aw(text))

#print('hello {}'.format(1))
filepath = '2012058.pdf'
os.chdir("/mnt/c/Users/alex.hamilton-smith/vscode_repos/FMP_Scanned_Document_Classifier/FMP_Scanned_Document_Classifier")

allpages = (print_pages(filepath))
#print((allpages))
print(len(allpages))
print(get_batch(allpages))
print(get_aw(allpages))