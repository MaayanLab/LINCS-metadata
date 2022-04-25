### Script for updating individual LINCS project tables to April 2022 C2M2 schema ###

import pandas as pd 
import json

lincs_meta_repo = '/Users/maayanlab/Documents/GitHub/LINCS-metadata/c2m2_level1'

def extract_cols(tablename): 
    # get columns for {tablename} table directly from C2M2 datapackage schema
    f = json.load(open(f'{lincs_meta_repo}/datapackage.json', 'r'))
    for obj in f['resources']: 
        if obj['name'] == tablename: 
            return [field['name'] for field in obj['schema']['fields']]
    raise Exception(f"'{tablename}' is not a valid C2M2 table.")

def get_col_tax():
    coll = pd.read_csv(f'{lincs_meta_repo}/collection.tsv', sep='\t')
    col_tax = coll.copy()
    col_tax['taxon'] = 'NCBI:txid9606'
    col_tax = col_tax.rename(columns = {'id_namespace': 'collection_id_namespace', 'local_id': 'collection_local_id'})
    col_tax[extract_cols('collection_taxonomy')]\
        .to_csv(f'{lincs_meta_repo}/collection_taxonomy.tsv', sep='\t', index=False)

def get_col_anat(): 
    bio = pd.read_csv(f'{lincs_meta_repo}/biosample.tsv', sep='\t').set_index('local_id')
    bio_in_col = pd.read_csv(f'{lincs_meta_repo}/biosample_in_collection.tsv', sep='\t')
    anat_map = {}
    anat_col_map = {}
    for row in bio_in_col.itertuples(): 
        anat = bio.loc[row.biosample_local_id, 'anatomy']
        col = row.collection_local_id
        if row.collection_local_id in anat_map.keys(): 
            anat_map[col].append(anat)
        else:
            anat_map[col] = [anat]
    for k, v in anat_map.items(): 
        if len(set(v)) == 1: 
            anat_col_map[k] = v[0]
    if len(anat_col_map) > 0:
        coll_anat = pd.DataFrame([['https://www.lincsproject.org/', k, v] for k,v in anat_col_map.items()], columns=extract_cols('collection_anatomy'))
        coll_anat = coll_anat.dropna(axis=0)
        coll_anat.to_csv(f'{lincs_meta_repo}/collection_anatomy.tsv', sep='\t', index=False)

def get_col_dz():
    bio_disease = pd.read_csv(f'{lincs_meta_repo}/biosample_disease.tsv', sep='\t').set_index('biosample_local_id')
    bio_in_col = pd.read_csv(f'{lincs_meta_repo}/biosample_in_collection.tsv', sep='\t')
    dz_map = {}
    dz_col_map = {}
    for row in bio_in_col.itertuples(): 
        try:
            dz = bio_disease.loc[row.biosample_local_id, 'disease']
        except:
            continue
        col = row.collection_local_id
        if row.collection_local_id in dz_map.keys(): 
            dz_map[col].append(dz)
        else:
            dz_map[col] = [dz]
    for k, v in dz_map.items(): 
        if len(set(v)) == 1: 
            dz_col_map[k] = v[0]
    if len(dz_col_map) > 0:
        coll_dz = pd.DataFrame([['https://www.lincsproject.org/', k, v] for k,v in dz_col_map.items()], columns=extract_cols('collection_disease'))
        coll_dz = coll_dz.dropna(axis=0)
        coll_dz.to_csv(f'{lincs_meta_repo}/collection_disease.tsv', sep='\t', index=False)

# add biosample disease association type
bio_dz = pd.read_csv(f'{lincs_meta_repo}/biosample_disease.tsv', sep='\t')
bio_dz['association_type'] = 'cfde_disease_association_type:0'
bio_dz[extract_cols('biosample_disease')].to_csv(f'{lincs_meta_repo}/biosample_disease.tsv', sep='\t', index=False)

# add subject disease association type
sub_dz = pd.read_csv(f'{lincs_meta_repo}/subject_disease.tsv', sep='\t')
sub_dz['association_type'] = 'cfde_disease_association_type:0'
sub_dz[extract_cols('subject_disease')].to_csv(f'{lincs_meta_repo}/subject_disease.tsv', sep='\t', index=False)

# add new file columns
f = pd.read_csv(f'{lincs_meta_repo}/file.tsv', sep='\t')
f['dbgap_study_id'] = '' 
f['analysis_type'] = '' 
f[extract_cols('file')].to_csv(f'{lincs_meta_repo}/file.tsv', sep='\t', index=False)

# build new empty tables
pd.DataFrame(columns=extract_cols('collection_phenotype')).to_csv(f'{lincs_meta_repo}/collection_phenotype.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('collection_substance')).to_csv(f'{lincs_meta_repo}/collection_substance.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('collection_gene')).to_csv(f'{lincs_meta_repo}/collection_gene.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('phenotype_gene')).to_csv(f'{lincs_meta_repo}/phenotype_gene.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('subject_phenotype')).to_csv(f'{lincs_meta_repo}/subject_phenotype.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('protein_gene')).to_csv(f'{lincs_meta_repo}/protein_gene.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('collection_protein')).to_csv(f'{lincs_meta_repo}/collection_protein.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('phenotype_disease')).to_csv(f'{lincs_meta_repo}/phenotype_disease.tsv', sep='\t', index=False)
pd.DataFrame(columns=extract_cols('collection_compound')).to_csv(f'{lincs_meta_repo}/collection_compound.tsv', sep='\t', index=False)

# build non-empty tables
get_col_anat()
get_col_tax()
get_col_dz()