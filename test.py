import calendar
import os
import shutil

def move_to_classified(filepath, batch, aw_no):
    dest_path = '/mnt/scans/Batch Records/'
    #dest_path = 'Batch_Records/'
    dest_path += '20' + batch[0:2] + '/'
    month_no = int(batch[2:4])
    dest_path += str(month_no).zfill(2) + '.' + calendar.month_abbr[month_no] + '/'
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    destination_full = dest_path + batch + ' ' + aw_no + '.pdf'
    index = 0;
    while os.path.exists(destination_full):
        index += 1
        destination_full = dest_path + batch + ' ' + aw_no + index.zfill(3) + '.pdf'
    try:
        shutil.copy(filepath, destination_full)
    except PermissionError:
        pass
    os.remove(filepath)

move_to_classified('~/192.168.0.109.txt', '2001001', 'AW-001')