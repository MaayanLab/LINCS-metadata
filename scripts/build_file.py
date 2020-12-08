# script for building C2M2 Level 1-compliant 'file.tsv'
import os
import hashlib 
import numpy as np 
import pandas as pd 
import gzip
import shutil

dir_paths = [
    '101406/replica_sets',
    '92743/replica_sets',
    '92742/replica_sets'
]

s3_paths = {
    '101406': 'https://lincs-dcic.s3.amazonaws.com/L1000-PCCSE-GSE101406/',
    '92743': 'https://lincs-dcic.s3.amazonaws.com/L1000-GTEX-GSE92743/',
    '92742': 'https://lincs-dcic.s3.amazonaws.com/LINCS-data-phase-1/L1000/'
}

project_ids = {
    '101406': 'L1000-PCCSE',
    '92743': 'L1000-GTEx',
    '92742': 'L1000-Phase1'
}

columns = [
    'id_namespace',
    'local_id',
    'project_id_namespace',
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

# iterate through each project
for d in dir_paths:
    gse = d.split('/')[0]

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    metadata_arr = []
    
    # iterate through each replica file in project
    for f in os.listdir(d):
        # store each row of the table
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
            with gzip.open(d + '/' + f + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        size_in_bytes = os.path.getsize(d + '/' + f + '.gz')

        # remove unzipped file to conserve space
        os.remove(d + '/' + f)
        
        # FILL IN ROW BY METADATA CATEGORY

        # id_namespace
        file_row.append('http://www.lincsproject.org/')
        # local_id
        file_row.append(f + '.gz')
        # project_id_namespace
        file_row.append('http://www.lincsproject.org/')
        # project_local_id
        file_row.append(project_ids[gse])
        # persistent_id
        file_row.append(s3_paths[gse] + f + '.gz')
        # creation_time
        file_row.append('')
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
        file_row.append('text/tab-separated-values')

        # add row to array
        metadata_arr.append(file_row)

    fname = '/'.join([gse, 'c2m2_level1', 'file.tsv'])
    pd.DataFrame(data=np.array(metadata_arr), columns=columns).set_index('id_namespace').to_csv(fname, sep='\t')

# combine all file.tsv files
pd.concat([
    pd.read_csv('101406/c2m2_level1/file.tsv', sep='\t'),
    pd.read_csv('92742/c2m2_level1/file.tsv', sep='\t'),
    pd.read_csv('92743/c2m2_level1/file.tsv', sep='\t')
]).set_index('id_namespace').to_csv('level_1/file.tsv', sep='\t')