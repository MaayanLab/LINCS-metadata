### Convert MCF10A MDD metadata to C2M2 format ###
### Based on Nov 2021 C2M2 Release schema ###

import pandas as pd 
import hashlib 
import shutil
import gzip
from os import listdir, path
import json 
import datetime
from urllib.parse import quote_plus

def extract_cols(tablename): 
    # get columns for {tablename} table directly from C2M2 datapackage schema
    f = json.load(open('C2M2_datapackage.json', 'r'))
    for obj in f['resources']: 
        if obj['name'] == tablename: 
            return [field['name'] for field in obj['schema']['fields']]
    raise Exception(f"'{tablename}' is not a valid C2M2 table.")

def build_proj(proj_id): 
    proj = {
        'id_namespace': 'https://www.lincsproject.org/', 
        'local_id': proj_id, 
        'persistent_id': 'https://www.synapse.org/#!Synapse:syn21577710/wiki/601042', 
        'creation_time': datetime.datetime(2020, 2, 6), 
        'abbreviation': 'LINCS MCF10A MDD', 
        'name': 'LINCS MCF10A Molecular Deep Dive (MDD)',
        'description': 'A comprehensive resource dataset that catalogs the transcriptional, proteomic, epigenomic and phenotypic changes experienced by MCF10A mammary epithelial cells as they respond to the ligands EGF, HGF, OSM, IFNG, TGFB and BMP2.'
    }
    proj_df = pd.DataFrame([proj])
    proj_df = proj_df[extract_cols('project')]
    proj_df.to_csv('C2M2/project.tsv', sep='\t', index=False)


def build_p_in_p(): 
    proj = pd.read_csv('C2M2/project.tsv', sep='\t', usecols=['id_namespace', 'local_id'])
    proj = proj.rename(columns={'id_namespace': 'child_project_id_namespace', 'local_id': 'child_project_local_id'})
    proj['parent_project_id_namespace'] = 'https://www.lincsproject.org/'
    proj['parent_project_local_id'] = 'LINCS'
    proj = proj[extract_cols('project_in_project')]
    proj.to_csv('C2M2/project_in_project.tsv', sep='\t', index=False)


def build_file(proj_path, proj_id): 
    # file

    persistent_map = {
        'ATACseq': 'https://www.synapse.org/#!Synapse:syn18485480.5', 
        'cycIF': 'https://www.synapse.org/#!Synapse:syn18811162.1', 
        'GCP': 'https://www.synapse.org/#!Synapse:syn18804314.4', 
        'IF': 'https://www.synapse.org/#!Synapse:syn21498854.1',
        'L1000': 'https://www.synapse.org/#!Synapse:syn18918362.2',
        'RNAseq': 'https://www.synapse.org/#!Synapse:syn15574167.4',
        'RPPA': 'https://www.synapse.org/#!Synapse:syn12555331'
    }

    assay_map = {
        'ATACseq': 'OBI:0002039', 
        'cycIF': 'OBI:0002969', 
        'GCP': 'OBI:0002961', 
        'IF': 'OBI:0001501', 
        'L1000': 'OBI:0002965', 
        'RNAseq': 'OBI:0001271', 
        'RPPA': 'OBI:0002957'
    }

    time_map = {
        'ATACseq': datetime.datetime(2019, 8, 8), 
        'cycIF': datetime.datetime(2019, 6, 5), 
        'GCP': datetime.datetime(2019, 8, 5), 
        'IF': datetime.datetime(2020, 2, 28), 
        'L1000': datetime.datetime(2019, 8, 5), 
        'RNAseq': datetime.datetime(2019, 8, 5), 
        'RPPA': datetime.datetime(2019, 8, 5)
    }

    data_map = {
        'ATACseq': 'data:3917', # count matrix (counts per peak) 
        'cycIF': 'data:2603', 
        'GCP': 'data:2603', 
        'IF': 'data:2603', 
        'L1000': 'data:3112', # gene expression matrix
        'RNAseq': 'data:3112', # gene expression matrix
        'RPPA': 'data:2603' # (protein quantification) expression data 
    }

    dsets = []

    for fname in listdir(dir_path): 
        if fname.startswith('.DS'): continue
        # compute checksum
        md5 = hashlib.md5() 
        sha256 = hashlib.sha256() 
        with open(f"{proj_path}/{fname}", 'rb') as fb: 
            for chunk in iter(lambda: fb.read(4096), b""): 
                md5.update(chunk) 
                sha256.update(chunk)
            md5_hash = md5.hexdigest() 
            sha256_hash = sha256.hexdigest() 

        orig_size = path.getsize(f"{proj_path}/{fname}")
        with open(f"{proj_path}/{fname}", 'rb') as f_in:
            with gzip.open(f"{proj_path}-zipped/{fname}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        zip_size = path.getsize(f"{proj_path}-zipped/{fname}.gz")

        assay_name = fname.split('_')[1]
        
        file_data = {
            'id_namespace': 'https://www.lincsproject.org/', 
            'local_id': f"{fname.replace('.csv', '')}", 
            'project_id_namespace': 'https://www.lincsproject.org/', 
            'project_local_id': proj_id, 
            'persistent_id': quote_plus(persistent_map[assay_name], safe='/:.#!'), 
            'creation_time': time_map[assay_name], 
            'size_in_bytes': zip_size, 
            'uncompressed_size_in_bytes': orig_size, 
            'sha256': sha256_hash, 
            'md5': md5_hash, 
            'filename': fname, 
            'file_format': 'format_3752', 
            'compression_format': 'format:3989',  # gzip
            'data_type': data_map[assay_name], 
            'assay_type': assay_map[assay_name],
            'analysis_type': '', 
            'mime_type': 'application/gzip',
            'bundle_collection_id_namespace': '', 
            'bundle_collection_local_id': ''
        }

        dsets.append(file_data)

    final_df = pd.DataFrame(dsets)
    final_df = final_df[extract_cols('file')] # ensure same order as schema 
    final_df.to_csv('C2M2/file.tsv', sep='\t', index=False)


def build_biosample(proj_id): 
    # biosample
    sample_meta = pd.read_csv('metadata/MDD_sample_annotations_abr.csv')

    bios = []

    for row in sample_meta.itertuples(): 

        bio = {
            'id_namespace': 'https://www.lincsproject.org/', 
            'local_id': row.new_sid,
            'project_id_namespace': 'https://www.lincsproject.org/', 
            'project_local_id': proj_id, 
            'persistent_id': '', 
            'creation_time': datetime.datetime(2019, 12, 9), 
            'assay_type': '', 
            'anatomy': 'UBERON:0000310' # breast
        }

        bios.append(bio)
    
    bio_df = pd.DataFrame(bios)
    bio_df = bio_df[extract_cols('biosample')] 
    bio_df.to_csv('C2M2/biosample.tsv', sep='\t', index=False)


def build_fdb(): 
    # file describes biosample
    f = pd.read_csv('C2M2/file.tsv', sep='\t', usecols=['id_namespace', 'local_id'])
    bio = pd.read_csv('C2M2/biosample.tsv', sep='\t', usecols=['id_namespace', 'local_id'])

    fdb = pd.DataFrame()

    for row in f.itertuples(): 
        samples = pd.read_csv(f'LINCS-MCF10A-MDD-annot/{row.local_id}.csv').columns
        rep_samples = bio[bio['local_id'].isin(samples)]
        rep_samples['file_id_namespace'] = rep_samples['id_namespace']
        rep_samples['file_local_id'] = row.local_id
        rep_samples = rep_samples.rename(columns={'id_namespace': 'biosample_id_namespace', 'local_id': 'biosample_local_id'})
        fdb = pd.concat([fdb, rep_samples])

    fdb = fdb[extract_cols('file_describes_biosample')].drop_duplicates(subset=['file_local_id', 'biosample_local_id'])
    fdb.to_csv('C2M2/file_describes_biosample.tsv', sep='\t', index=False)


def filter_mcf10a(f): 
    # filter existing file {f} to include only MCF10A row
    # mainly subject, subject_disease
    df = pd.read_csv(f'old_C2M2/{f}.tsv', sep='\t')
    local_id_cols = [col for col in df.columns if 'local_id' in col]
    mcf10a_inds = [df[col].tolist().index('MCF10A') for col in local_id_cols if 'MCF10A' in df[col].tolist()]
    new_df = df.loc[mcf10a_inds]
    cols = extract_cols(f)
    if set(cols) != set(new_df.columns.tolist()):
        print(f"Warning! The following columns are missing from {f}.tsv: {'; '.join(set(cols).difference(set(new_df.columns.tolist())))}")
    new_df.to_csv(f'C2M2/{f}.tsv', sep='\t', index=False)


def build_fds(): 
    # file describes subject
    f = pd.read_csv('C2M2/file.tsv', sep='\t', usecols=['id_namespace', 'local_id'])
    f = f.rename(columns={'id_namespace': 'file_id_namespace', 'local_id': 'file_local_id'})
    f['subject_id_namespace'] = f['file_id_namespace'].to_list()
    f['subject_local_id'] = 'MCF10A'
    f = f[extract_cols('file_describes_subject')].drop_duplicates(subset=['file_local_id', 'subject_local_id'])
    f.to_csv('C2M2/file_describes_subject.tsv', sep='\t', index=False)


def build_bfs(): 
    # biosample from subject
    bio = pd.read_csv('C2M2/biosample.tsv', sep='\t', usecols=['id_namespace', 'local_id'])
    bio = bio.rename(columns={'id_namespace': 'biosample_id_namespace', 'local_id': 'biosample_local_id'})
    bio['subject_id_namespace'] = bio['biosample_id_namespace'].to_list()
    bio['subject_local_id'] = 'MCF10A'
    bio['age_at_sampling'] = ''
    bio = bio[extract_cols('biosample_from_subject')].drop_duplicates(subset=['biosample_local_id', 'subject_local_id'])
    bio.to_csv('C2M2/biosample_from_subject.tsv', sep='\t', index=False)


def build_bd(): 
    # biosample_disease
    sd = pd.read_csv('C2M2/subject_disease.tsv', sep='\t', usecols=['subject_local_id', 'disease']).set_index('subject_local_id')
    bfs = pd.read_csv('C2M2/biosample_from_subject.tsv', sep='\t', usecols=['biosample_id_namespace', 'biosample_local_id', 'subject_local_id'])

    bfs['disease'] = bfs['subject_local_id'].apply(lambda x: sd.loc[x, 'disease'])
    bfs['association_type'] = 'cfde_disease_association_type:0'
    bfs = bfs[extract_cols('biosample_disease')].drop_duplicates(subset=['biosample_local_id', 'disease'])
    bfs.to_csv('C2M2/biosample_disease.tsv', sep='\t', index=False)

### variables
dir_path = 'LINCS-MCF10A-MDD-annot' # file directory
proj = 'MCF10A-MDD' # project local ID

### add new project
build_proj(proj)
build_p_in_p()

### build core entity tables (file, biosample, subject)
build_file(dir_path, proj)
build_biosample(proj)
filter_mcf10a('subject') # since MCF10A already exists in previous metadata, we can just isolate the MCF10A entry

### build relevant association tables between core entitites
build_fdb()
build_fds()
build_bfs()

### build other association tables
filter_mcf10a('subject_disease') # as before, we can isolate the MCF10A entry
build_bd()





