# script for building C2M2 Level 1-compliant 'subject.tsv' and 'biosample.tsv'
import numpy as np 
import pandas as pd 

# BIOSAMPLE
# modify columns: local_id
# add columns: anatomy
# keep columns: id_namespace, project_id_namespace, project_local_id, 
#               persistent_id, creation_time
def build_biosample(df):
    new_df = df[[
        'id_namespace',
        'local_id',
        'project_id_namespace',
        'project_local_id',
        'persistent_id',
        'creation_time'
    ]]

    # add anatomy mappings in later
    new_df['anatomy'] = ''

    samp_ids = []
    for row in df.itertuples():
        if row.project_local_id == 'L1000-Phase1':
            # filename ex: L1000_LINCS_DCIC_AML001_CD34_24H_A03_securinine_10.00um.tsv.gz
            # sample ex: AML001_CD34_24H_A03
            bs = '_'.join(row.filename.split('DCIC_')[1].split('_')[:4])
        elif row.project_local_id == 'L1000-PCCSE':
            # filename ex: L1000_LINCS_DCIC_LPROT001_A375_6H_X1_B20_entinostat_2.00um.tsv.gz
            # sample ex: LPROT001_A375_6H_X1_B20
            bs = '_'.join(row.filename.split('DCIC_')[1].split('_')[:5])
        else:
            # filename ex: L1000_LINCS_DCIC_GTEX-ZC5H-2226.tsv.gz
            # sample ex: GTEX-ZC5H-2226
            bs = row.filename.split('DCIC_')[1].split('.tsv')[0]
        samp_ids.append(bs)
    new_df['local_id'] = samp_ids

    # remove duplicate samples
    new_df = new_df.drop_duplicates(subset='local_id')

    new_df.set_index('id_namespace').to_csv('level_1/biosample.tsv', sep='\t')

# SUBJECT
# modify columns: local_id
# add columns: granularity
# keep columns: id_namespace, project_id_namespace, project_local_id, 
#               persistent_id, creation_time
def build_subject(df):
    new_df = df[[
        'id_namespace',
        'local_id',
        'project_id_namespace',
        'project_local_id',
        'persistent_id',
        'creation_time'
    ]]

    sub_ids = []
    granularities = []
    for row in df.itertuples():
        if row.project_local_id == 'L1000-Phase1':
            # filename ex: L1000_LINCS_DCIC_AML001_CD34_24H_A03_securinine_10.00um.tsv.gz
            # subject ex: CD34
            s = row.filename.split('DCIC_')[1].split('_')[1]
            gran = 'cfde_subject_granularity:4' # cell line
        elif row.project_local_id == 'L1000-PCCSE':
            # filename ex: L1000_LINCS_DCIC_LPROT001_A375_6H_X1_B20_entinostat_2.00um.tsv.gz
            # subject ex: A375
            s = row.filename.split('DCIC_')[1].split('_')[1]
            gran = 'cfde_subject_granularity:4' # cell line
        else:
            # filename ex: L1000_LINCS_DCIC_GTEX-ZC5H-2226.tsv.gz
            # subject ex: GTEX-ZC5H
            s = '-'.join(row.filename.split('DCIC_')[1].split('-')[:2])
            gran = 'cfde_subject_granularity:0' # individual
        sub_ids.append(s)
        granularities.append(gran)

    new_df['local_id'] = sub_ids
    new_df['granularity'] = granularities

    # remove duplicate subjects
    new_df = new_df.drop_duplicates(subset='local_id')

    new_df.set_index('id_namespace').to_csv('level_1/subject.tsv', sep='\t')

# FILE DESCRIBES BIOSAMPLE
def build_fdb(df):
    new_df = df[[
        'id_namespace',
        'local_id'
    ]]

    new_df = new_df.rename(columns={
        'id_namespace': 'file_id_namespace',
        'local_id': 'file_local_id'
    })

    new_df['biosample_id_namespace'] = 'http://www.lincsproject.org/'

    samp_ids = []
    for row in df.itertuples():
        if row.project_local_id == 'L1000-Phase1':
            # filename ex: L1000_LINCS_DCIC_AML001_CD34_24H_A03_securinine_10.00um.tsv.gz
            # sample ex: AML001_CD34_24H_A03
            bs = '_'.join(row.filename.split('DCIC_')[1].split('_')[:4])
        elif row.project_local_id == 'L1000-PCCSE':
            # filename ex: L1000_LINCS_DCIC_LPROT001_A375_6H_X1_B20_entinostat_2.00um.tsv.gz
            # sample ex: LPROT001_A375_6H_X1_B20
            bs = '_'.join(row.filename.split('DCIC_')[1].split('_')[:5])
        else:
            # filename ex: L1000_LINCS_DCIC_GTEX-ZC5H-2226.tsv.gz
            # sample ex: GTEX-ZC5H-2226
            bs = row.filename.split('DCIC_')[1].split('.tsv')[0]
        samp_ids.append(bs)
    new_df['biosample_local_id'] = samp_ids

    new_df.set_index('file_id_namespace').to_csv('level_1/file_describes_biosample.tsv', sep='\t')

# FILE DESCRIBES SUBJECT
def build_fds(df):
    new_df = df[[
        'id_namespace',
        'local_id'
    ]]

    new_df = new_df.rename(columns={
        'id_namespace': 'file_id_namespace',
        'local_id': 'file_local_id'
    })

    new_df['subject_id_namespace'] = 'http://www.lincsproject.org/'

    sub_ids = []
    for row in df.itertuples():
        if row.project_local_id == 'L1000-Phase1':
            # filename ex: L1000_LINCS_DCIC_AML001_CD34_24H_A03_securinine_10.00um.tsv.gz
            # subject ex: CD34
            s = row.filename.split('DCIC_')[1].split('_')[1]
        elif row.project_local_id == 'L1000-PCCSE':
            # filename ex: L1000_LINCS_DCIC_LPROT001_A375_6H_X1_B20_entinostat_2.00um.tsv.gz
            # subject ex: A375
            s = row.filename.split('DCIC_')[1].split('_')[1]
        else:
            # filename ex: L1000_LINCS_DCIC_GTEX-ZC5H-2226.tsv.gz
            # subject ex: GTEX-ZC5H
            s = '-'.join(row.filename.split('DCIC_')[1].split('-')[:2])
        sub_ids.append(s)
    new_df['subject_local_id'] = sub_ids

    new_df.set_index('file_id_namespace').to_csv('level_1/file_describes_subject.tsv', sep='\t')

build_biosample(pd.read_csv('level_1/file.tsv', sep='\t'))
build_subject(pd.read_csv('level_1/file.tsv', sep='\t'))
build_fdb(pd.read_csv('level_1/file.tsv', sep='\t'))
build_fds(pd.read_csv('level_1/file.tsv', sep='\t'))