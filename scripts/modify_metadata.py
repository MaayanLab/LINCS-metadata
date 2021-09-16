'''
This script contains functions for modifying an existing C2M2-compliant 
metadata datapackage containing LINCS data to reflect any new updates. 
'''
import pandas as pd 
import numpy as np

###### September 2021 #####

# subject_disease.tsv
def subject_disease(sub_fpath):
    '''
    Using an existing subject.tsv file and a LINCS to disease mapping, 
    build the subject_disease.tsv table. 
    '''
    df = pd.read_csv(sub_fpath, sep='\t', usecols=['id_namespace', 'local_id'])
    dz_map = pd.read_csv('mappings/lincs_disease_ontology_mappings.tsv', 
        sep='\t', usecols=['cell_line', 'doid']).set_index('cell_line')
    df['disease'] = [
        dz_map.loc[row.local_id.split('.')[0], 'doid'] 
        if row.local_id.split('.')[0] in dz_map.index else np.nan
        for row in df.itertuples()]
    df = df.rename(columns={
        'id_namespace': 'subject_id_namespace',
        'local_id': 'subject_local_id'
    })
    df = df.dropna(subset=['disease'])
    return df.set_index('subject_id_namespace')

# biosample_disease.tsv
def biosample_disease(bio_fpath, bfs_fpath):
    '''
    Using an existing biosample.tsv files and a LINCS to disease 
    mapping, build the biosample_disease.tsv table. 
    '''
    df = pd.read_csv(bio_fpath, sep='\t', usecols=['id_namespace', 'local_id'])
    bfs = pd.read_csv(bfs_fpath, sep='\t', usecols=['biosample_local_id', 'subject_local_id']) \
        .set_index('biosample_local_id')
    dz_map = pd.read_csv('mappings/lincs_disease_ontology_mappings.tsv', 
        sep='\t', usecols=['cell_line', 'doid']).set_index('cell_line')
    new_dz = []
    for row in df.itertuples():
        subject = bfs.loc[row.local_id, 'subject_local_id']
        try:
            new_dz.append(dz_map.loc[subject, 'doid'])
        except:
            new_dz.append(np.nan)
    df['disease'] = new_dz
    df = df.rename(columns={
        'id_namespace': 'biosample_id_namespace',
        'local_id': 'biosample_local_id'
    })
    df = df.dropna(subset=['disease'])
    return df.set_index('biosample_id_namespace')

# add assay_type to biosample
def biosample_assay_type(bio_fpath, fdb_fpath, file_fpath):
    '''
    Add assay type field to existing biosample.tsv file, using
    file_describes_biosample and file tables.
    '''
    df = pd.read_csv(bio_fpath, sep='\t')
    f = pd.read_csv(file_fpath, sep='\t', usecols=['local_id', 'assay_type']) \
        .set_index('local_id')
    fdb = pd.read_csv(fdb_fpath, sep='\t', usecols=['file_local_id', 'biosample_local_id']) \
        .drop_duplicates(subset=['biosample_local_id']) \
        .set_index('biosample_local_id')
    assays = []
    for row in df.itertuples():
        f1 = fdb.loc[row.local_id, 'file_local_id']
        assays.append(f.loc[f1, 'assay_type'])
    df['assay_type'] = assays
    return df.set_index('id_namespace')
