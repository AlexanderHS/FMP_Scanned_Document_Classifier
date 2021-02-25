import os
import shutil
import argparse
import pdf2image
import calendar
import PyPDF2
import ntpath
import glob

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)

def ocr_core(file):
    text = pytesseract.image_to_string(file)
    return text
def print_pages(pdf_file):
    images = pdf_to_img(pdf_file)
    for pg, img in enumerate(images):
        return (ocr_core(img))

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

def move_to_unclassified(filepath):
    dest_path = '/mnt/scans/unrecognised/'
    #dest_path = 'unclassified/'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + ntpath.basename(filepath)
    try:
        shutil.copy(filepath, destination_full)
    except Exception:
        pass
    os.remove(filepath)

def move_to_classified(filepath, batch, aw_no):
    dest_path = '/mnt/scans/Batch_Records/'
    #dest_path = 'Batch_Records/'
    dest_path += '20' + batch[0:2] + '/'
    month_no = int(batch[2:4])
    dest_path += calendar.month_abbr[month_no] + '/'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + batch + '_' + aw_no + '.pdf'
    #filepath = ntpath.basename(filepath)
    try:
        shutil.copy(filepath, destination_full)
    except PermissionError:
        pass
    os.remove(filepath)

def interpret(filepath):
    batch = ''
    aw_no = ''
    try:
        print('Interpretting. This can take a moment...')
        converted_text = print_pages(filepath)
        print('--')
        print(converted_text)
        print('--')
        print('Done.')
        batch = (get_batch(converted_text))
        print('# Found Batch: ' + batch)
        aw_no = (get_aw(converted_text))
        print('# Work Order: ' + aw_no)
        if not aw_no.startswith('AW-'):
            aw_no = None
    except Exception as e:
        print('Error: Unable to read a valid file at that path.')
        print(e)
        return None, None
    return (batch, aw_no)

def rotate(filepath):

    pdf_in = open(filepath, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_in)
    pdf_writer = PyPDF2.PdfFileWriter()

    for pagenum in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagenum)
        if pagenum % 2:
            page.rotateClockwise(180)
        pdf_writer.addPage(page)

    pdf_out = open('rotated.pdf', 'wb')
    pdf_writer.write(pdf_out)
    pdf_out.close()
    pdf_in.close()

def main():
    # Parsing stuff...
    #parser = argparse.ArgumentParser(description='When given a file path, attempts to detect the read the type and classify/move that file to the correct network location.')
    #parser.add_argument('filepath')
    #args = parser.parse_args()

    os.chdir("/mnt/sieve_scans")
    for file in glob.glob("*.pdf"):
        print('Considering ' + file)
        filepath = file

        # Try to read
        batch, aw_no = interpret(filepath)

        reads_as_valid = batch is not None and aw_no is not None
        
        # If reads as junk try rotating
        if not reads_as_valid:
            print('going to try a rotation...')
            rotate(filepath)
            batch, aw_no = interpret('rotated.pdf')
            reads_as_valid = batch is not None and aw_no is not None
            if os.path.exists('rotated.pdf'):
                os.remove('rotated.pdf')
        if not reads_as_valid:
            print('saving as unclassified')
            move_to_unclassified(filepath)
        else:
            print('saving as classified')
            move_to_classified(filepath, batch, aw_no)

if __name__ == "__main__":
    main()