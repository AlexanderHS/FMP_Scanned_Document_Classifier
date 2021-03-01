import datetime

batch = '4509167'
if batch.startswith('45'):
    batch = '15' + batch[2:]

print(batch)