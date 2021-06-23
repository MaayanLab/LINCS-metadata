# functions for building C2M2 Level 1-compliant 'file.tsv'
import os
import hashlib 
import numpy as np 
import pandas as pd 
import gzip
import shutil
from os.path import exists
from datetime import datetime
from urllib import parse

# list all pert categories
perts = [
    'xpr',
    'cp',
    'sh',
    'misc',
    'ctl',
    'oe'
]

# S3 bucket path
s3_base = 'https://lincs-dcic.s3.amazonaws.com/LINCS-data-2020/'

# C2M2 columns
columns = [
    'id_namespace',
    'local_id',
    'project_id_namespace',
    'project_local_id',
    'persistent_id',
    'creation_time',
    'size_in_bytes',
    'uncompressed_size_in_bytes',
    'sha256',
    'md5',
    'filename',
    'file_format',
    'data_type',
    'assay_type',
    'mime_type'
]

# iterate through each perturbation type
for p in perts:
    # pert-specific directory
    d = f"data/{p}"
    # array to hold all metadata
    metadata_arr = []

    # iterate through each replica file in project
    for f in os.listdir(d):

        # check if file has already been processed and zipped
        if exists(d + '_zip/' + f + '.gz'):
            continue
        # array to hold metadata for each file
        file_row = []

        # compute uncompressed size
        uncompressed_size_in_bytes = os.path.getsize(d + '/' + f)
        
        # compute hashes
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(d + '/' + f, 'rb') as data:
            for chunk in iter(lambda: data.read(4096), b""):
                md5.update(chunk)
                sha256.update(chunk)
        md5_hash = md5.hexdigest()
        sha256_hash = sha256.hexdigest()

        # gzip file and compute compressed size
        with open(d + '/' + f, 'rb') as f_in:
            with gzip.open(d + '_zip/' + f + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        size_in_bytes = os.path.getsize(d + '_zip/' + f + '.gz')

        # remove unzipped file to conserve space
        # os.remove(d + '/' + f)
        
        # FILL IN ROW BY METADATA CATEGORY

        # id_namespace
        file_row.append('http://www.lincsproject.org/')
        # local_id
        file_row.append(f.replace(' ', '') + '.gz')
        # project_id_namespace
        file_row.append('http://www.lincsproject.org/')
        # project_local_id
        file_row.append('LINCS-2020')
        # persistent_id
        file_row.append(parse.quote_plus('https://lincs-dcic.s3.amazonaws.com/LINCS-data-2020/L1000/compound/' + f + '.gz', safe='-/:'))
        # creation_time
        file_row.append(datetime(2021, 1, 28))
        # size_in_bytes
        file_row.append(size_in_bytes)
        # uncompressed_size_in_bytes
        file_row.append(uncompressed_size_in_bytes)
        # sha256
        file_row.append(sha256_hash)
        # md5
        file_row.append(md5_hash)
        # filename
        file_row.append(f + '.gz')
        # file_format
        file_row.append('format:3475')
        # data_type
        file_row.append('data:0928')
        # assay_type
        file_row.append('OBI:0002965')
        # mime_type
        file_row.append('application/gzip')

        # add row to array
        metadata_arr.append(file_row)

    fname = f'metadata/trt_{p}_file.tsv'
    pd.DataFrame(
        data=np.array(metadata_arr), 
        columns=columns
    ).astype({
        'size_in_bytes': 'int32', 
        'uncompressed_size_in_bytes': 'int32'
     }).set_index('id_namespace').to_csv(fname, sep='\t')