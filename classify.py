import os
import shutil
import calendar
import PyPDF2
import ntpath
import glob
import pytesseract
import argparse
from unidecode import unidecode
import pdf2image
from pdf2image import convert_from_path
from PIL import Image
import time
import ghostscript
import locale
import datetime
import csv
import random
from joblib import Parallel, delayed

MAX_SIMULTANEOUS = 8
COLLECT_QTY = 50
TRIES = 200
DELAY = 0.5
MAX_PAGES_TO_INSPECT = 10
PATH_READ = '\\\\fm-fil-01\public\SCANS\Awaiting Classification'
WORK_ORDER_PATH = '\\\\fm-fil-01\Public\Alex HS\Data Folder\WorkOrders.csv'
UNCLASSIFIED_PATH = '\\\\fm-fil-01\\public\\SCANS\\'

# RECLASSIFICATION
'''
PATH_READ = '\\\\fm-fil-01\public\SCANS\Awaiting Classification\Recategorisation'
UNCLASSIFIED_PATH = '\\\\fm-fil-01\\public\\SCANS\\Awaiting Classification\\Recategorisation\\FAILED_TO_CLASSIFY\\'
'''

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
DEBUG = False

def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)

def ocr_core(file):
    text = pytesseract.image_to_string(file)
    return text
def print_pages(pdf_file):
    images = pdf_to_img(pdf_file)
    for pg, img in enumerate(images):
        return (ocr_core(img))

def is_positive_int(s):
    try: 
        _ = int(s)
        if _ < 0:
            return False
        int(s[:1])
        return True
    except ValueError:
        return False

def get_aw(text):
    #if 'Work Order' not in text:
    #    return None
    guess = ''
    index = 0
    while not (guess.startswith('AW-') and is_positive_int(guess[3:]) and len(guess) > 7 and len(guess) < 10):
        #if DEBUG: print('considering AW.. guess: {}'.format(guess))
        try:
            guess = text.strip().replace(os.linesep, ' ').split(' ')[index].strip()
        except IndexError:
            return None
        index += 1
    return guess.replace('\'', '').replace('\"', '')

def get_batch(text):
    #if 'Batch' not in text:
    #    return None
    guess = ''
    index = 0
    while len(guess) < 7 or not is_positive_int(guess[0:7]) or len(guess) > 8:
        #if DEBUG: print('considering batch guess: {}'.format(guess))
        try:
            guess = text.strip().replace(os.linesep, ' ').split(' ')[index].strip()
            #print('guess is {}'.format(guess))
            try:
                month_no = int(guess[2:4])
                _ = calendar.month_abbr[month_no]
            except:
                #print("Error: {} in {} doesn't look like a month".format(month_no, guess))
                guess = '1'
            try:
                year_no = int(guess[0:2])
                current_two_digit_year = int(str(datetime.datetime.now().year)[2:4])
                if current_two_digit_year < year_no:
                    raise RuntimeError from None
            except:
                guess = '1'
        except IndexError:
            return None
        index += 1
    if guess.startswith('4'):
        guess = '1' + guess[1:]
    return guess.replace('\'', '').replace('\"', '')

def move_to_unclassified(filepath):
    dest_path = UNCLASSIFIED_PATH
    #dest_path = 'unclassified/'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + ntpath.basename(filepath)
    index = 0
    while os.path.exists(destination_full):
        if DEBUG: print('Path ' + destination_full + ' was taken so trying next...')
        index += 1
        destination_full = dest_path + str(index).zfill(3) + '_' + ntpath.basename(filepath)
    try:
        if DEBUG: print("copying from '{}'' to '{}'".format(filepath, destination_full))
        shutil.copy(filepath, destination_full)
    except Exception:
        pass
    os.remove(filepath)
    print('File Moved. Done.')
    print()

def clean_path(destination_full):
    destination_full = destination_full.replace("<", "")
    destination_full = destination_full.replace(">", "")
    destination_full = destination_full.replace("*", "")
    destination_full = destination_full.replace(":", "")
    destination_full = destination_full.replace("?", "")
    destination_full = destination_full.replace("\"", "")
    destination_full = destination_full.replace("\'", "")
    destination_full = destination_full.replace("/", "")
    return destination_full

def move_to_classified(filepath, batch, aw_no):
    with open(WORK_ORDER_PATH, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        work_orders = {rows[0]:rows[1] for rows in reader}
    dest_path = '\\\\fm-fil-01\\qa\\Batch Records\\'
    #dest_path = 'Batch_Records/'
    dest_path += '20' + batch[0:2] + '\\'
    month_no = int(batch[2:4])
    dest_path += str(month_no).zfill(2) + '.' + calendar.month_abbr[month_no] + '\\'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + batch + ' ' + aw_no + '.pdf'
    if aw_no in work_orders:
        destination_full = dest_path + batch + ' ' + aw_no + ' ' + work_orders[aw_no] + '.pdf'
    index = 0;
    temp_destination = destination_full
    while os.path.exists(temp_destination):
        if DEBUG: print('Path ' + destination_full + ' was taken so trying next...')
        index += 1
        temp_destination = destination_full[:-4] + ' ' + str(index).zfill(3) + '.pdf'
    destination_full = temp_destination
    try:
        destination_full = clean_path(destination_full)
        if DEBUG: print("copying from '{}'' to '{}'".format(filepath, destination_full))
        shutil.copy(filepath, destination_full)
    except PermissionError:
        pass
    os.remove(filepath)
    print('File Moved. Done.')
    print()

def remove_weird(text):
    text = unidecode(text)
    text = text.replace(os.linesep, ' ')
    text = text.replace('\n', ' ')
    return unidecode(text).replace(os.linesep, '').replace('\n', '')

"""
# flagged for deletion
def interpret(filepath):
    batch = ''
    aw_no = ''
    try:
        print()
        print('Interpretting {}. This can take a moment...'.format(filepath))
        converted_text = remove_weird(print_pages(filepath))
        if DEBUG:
            #print('         -START CONTENT-')
            #print(converted_text)
            #print('         - END CONTENT -')
            print('Done.')
        batch = (get_batch(converted_text))
        if DEBUG: print('# Found Batch: ' + str(batch))
        aw_no = (get_aw(converted_text))
        if DEBUG: print('# Work Order: ' + str(aw_no))
        if not aw_no.startswith('AW-'):
            aw_no = None
    except Exception as e:
        if DEBUG: print('Some Exception Occured during classification: Classification Failed.')
        if DEBUG: print('Exception details: '.format(e))
        return None, None
    return (batch, aw_no)
"""

def rotate(filepath):
    pdf_in = open(filepath, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_in)
    pdf_writer = PyPDF2.PdfFileWriter()

    for pagenum in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagenum)
        page.rotateClockwise(180)
        pdf_writer.addPage(page)

    pdf_out = open('rotated.pdf', 'wb')
    pdf_writer.write(pdf_out)
    pdf_out.close()
    pdf_in.close()

def pdf2jpeg_stage1(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r500",
            "-dLastPage=1",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]
    ghostscript.Ghostscript(*args)

def pdf2jpeg_stage2(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r500",
            "-dFirstPage=2",
            "-dLastPage=4",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]
    ghostscript.Ghostscript(*args)

def pdf2jpeg_stage3(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r500",
            "-dFirstPage=5",
            "-dLastPage=12",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]
    ghostscript.Ghostscript(*args)

def get_batch_aw(pdf_file):
    if (DEBUG): print()
    if (DEBUG): print('Opening {}'.format(pdf_file))
    os.chdir(PATH_READ)
    if (DEBUG): print('STAGE 1 SPLIT...'.format(pdf_file))
    pdf2jpeg_stage1(pdf_file, pdf_file + "page%03d.jpeg")
    for i in glob.glob(pdf_file + "*.jpeg"):
        if (DEBUG): print('looking at {}, {}.'.format(pdf_file, i))
        try:
            text = str(((pytesseract.image_to_string(Image.open(i)))))
            text = remove_weird(text)
            batch = get_batch(text)
            aw = get_aw(text)
            if batch is not None and aw is not None:
                if DEBUG: print('batch: ' + batch)
                if DEBUG: print('aw: ' + aw)
                return batch, aw
        except Exception as e:
            # do nothing
            print ('Exception: {}'.format(e))
    
    for file in glob.glob(pdf_file + "*.jpeg"):
        os.remove(file)

    pdf2jpeg_stage2(pdf_file, pdf_file + "page%03d.jpeg")
    for i in glob.glob(pdf_file + "*.jpeg"):
        if (DEBUG): print('looking at {}, {}.'.format(pdf_file, i))
        try:
            text = str(((pytesseract.image_to_string(Image.open(i)))))
            text = remove_weird(text)
            batch = get_batch(text)
            aw = get_aw(text)
            if batch is not None and aw is not None:
                if DEBUG: print('batch: ' + batch)
                if DEBUG: print('aw: ' + aw)
                return batch, aw
        except Exception as e:
            # do nothing
            print ('Exception: {}'.format(e))

    for file in glob.glob(pdf_file + "*.jpeg"):
        os.remove(file)

    pdf2jpeg_stage3(pdf_file, pdf_file + "page%03d.jpeg")
    for i in glob.glob(pdf_file + "*.jpeg"):
        if (DEBUG): print('looking at {}, {}.'.format(pdf_file, i))
        try:
            text = str(((pytesseract.image_to_string(Image.open(i)))))
            text = remove_weird(text)
            batch = get_batch(text)
            aw = get_aw(text)
            if batch is not None and aw is not None:
                if DEBUG: print('batch: ' + batch)
                if DEBUG: print('aw: ' + aw)
                return batch, aw
        except Exception as e:
            # do nothing
            print ('Exception: {}'.format(e))

    for file in glob.glob(pdf_file + "*.jpeg"):
        os.remove(file)

    return None, None

def main():
    parser = argparse.ArgumentParser(description='Attempts to detect and the read the type and classify/move files to the correct network locations.')
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    args = parser.parse_args()
    rotated = False
    if args.verbose:
        global DEBUG
        DEBUG = True
    attempts = 0
    while attempts < TRIES:
        attempts += 1
        os.chdir(PATH_READ)
        if os.path.exists('rotated.pdf'): os.remove('rotated.pdf')
        for file in glob.glob("*.jpg"): os.remove(file)
        files = glob.glob("*.pdf")
        print()
        print(f"    *    *    *    FILES REMAINING: {len(files)}    *    *    *    ")
        print()

        #for file in list((sorted(files, key=len)))[:COLLECT_QTY]:
        random.shuffle(files)
        files = files[:COLLECT_QTY]
        if len(files) != 0:
            Parallel(n_jobs=MAX_SIMULTANEOUS)(delayed(assign_location_to)(i) for i in files)

        '''
        for file in files[:COLLECT_QTY]:
            assign_location_to(file)
        '''

        time_total = DELAY * attempts
        print(f"Wait {DELAY} seconds. Total wait {time_total}.")
        time.sleep(DELAY)


def assign_location_to(file):
    start = time.time()
    filepath = file

    # Try to read
    batch, aw_no = get_batch_aw(filepath)
    
    # If reads as junk try rotating
    '''
    if batch is None:
        if DEBUG: print('Failed so going to try again with rotation...')
        rotate(filepath)
        batch, aw_no = get_batch_aw('rotated.pdf')
        if batch is not None:
            rotated = True
    '''
    
    if batch is None:
        print('saving as unclassified')
        move_to_unclassified(filepath)
    else:
        print('saving as classified')
        move_to_classified(filepath, batch, aw_no)
    end = time.time()
    print('finished {} in {} seconds.'.format(file, (end - start)))
    for file in glob.glob(filepath + "*.jpg"): os.remove(file)


if __name__ == "__main__":
    main()