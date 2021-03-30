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

COLLECT_QTY = 10
TRIES = 5

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
DEBUG = True

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
        except IndexError:
            return None
        index += 1
    if guess.startswith('4'):
        guess = '1' + guess[1:]
    return guess.replace('\'', '').replace('\"', '')

def move_to_unclassified(filepath):
    dest_path = '\\\\fm-fil-01\\public\\SCANS\\'
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
    dest_path = '\\\\fm-fil-01\\qa\\Batch Records\\'
    #dest_path = 'Batch_Records/'
    dest_path += '20' + batch[0:2] + '\\'
    month_no = int(batch[2:4])
    dest_path += str(month_no).zfill(2) + '.' + calendar.month_abbr[month_no] + '\\'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + batch + ' ' + aw_no + '.pdf'
    index = 0;
    while os.path.exists(destination_full):
        if DEBUG: print('Path ' + destination_full + ' was taken so trying next...')
        index += 1
        destination_full = dest_path + batch + ' ' + aw_no + '_' + str(index).zfill(3) + '.pdf'
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


def get_batch_aw(pdf_file):
    os.chdir("\\\\sieve\\scans")
    print()
    print('Opening {}'.format(pdf_file))
    pages = convert_from_path(pdf_file, 500)
    image_counter = 1
    print('Splitting {} into pages...'.format(pdf_file))
    for page in pages:
        filename = pdf_file + "_page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1
    filelimit = image_counter-1
    print('Finished making files.')
    for i in range(1, filelimit + 1):
        filename = pdf_file + "_page_"+str(i)+".jpg"
        print('looking at {}, {}.'.format(pdf_file, filename))
        try:
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = remove_weird(text)
            batch = get_batch(text)
            aw = get_aw(text)
            if batch is not None and aw is not None:
                if DEBUG: print('batch: ' + batch)
                if DEBUG: print('aw: ' + aw)
                return batch, aw
            #print(text)
            #print('output_text is now {} lines.'.format(len(output_text)))
        except Exception as e:
            # do nothing
            print ('Exception: {}'.format(e))
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
        os.chdir("\\\\sieve\\scans")
        if os.path.exists('rotated.pdf'):
            os.remove('rotated.pdf')
        for file in glob.glob("*.jpg"):
            os.remove(file)
        os.chdir("\\\\sieve\\scans")
        if os.path.exists('rotated.pdf'):
            os.remove('rotated.pdf')
        for file in glob.glob("*.jpg"):
            os.remove(file)
        files = glob.glob("*.pdf")
        #for file in list((sorted(files, key=len)))[:COLLECT_QTY]:
        for file in list(reversed(sorted(files, key=len)))[:COLLECT_QTY]:
            start = time.time()
            filepath = file

            # Try to read
            batch, aw_no = get_batch_aw(filepath)
            
            # If reads as junk try rotating
            if batch is None:
                if DEBUG: print('Failed so going to try again with rotation...')
                rotate(filepath)
                batch, aw_no = get_batch_aw('rotated.pdf')
                if batch is not None:
                    rotated = True
            if batch is None:
                print('saving as unclassified')
                move_to_unclassified(filepath)
            else:
                print('saving as classified')
                move_to_classified(filepath, batch, aw_no)
            end = time.time()
            print('finished {} in {} seconds.'.format(file, (end - start)))
            for file in glob.glob("*.jpg"):
                os.remove(file)
        print('waiting 10...')
        time.sleep(10)


if __name__ == "__main__":
    main()