### Script for mapping LINCS MCF10A MDD specimen IDs and gene/probe symbols ###

import pandas as pd 
from os import listdir, mkdir

data_dir = 'LINCS-MCF10A-MDD' # directory containing all files

# read in relevant sample metadata
# metadata file can be downloaded from https://www.synapse.org/#!Synapse:syn18662790
# more information on metadata columns can be found at https://www.synapse.org/#!Synapse:syn12979102
sample_meta = pd.read_csv(
    'metadata/MDD_sample_annotations.csv',
    usecols=[
        'specimenID', 'ligand', 'experimentalTimePoint', 'replicate', 'collection', 
        'ligandDose', 'timePointUnit', 'ligandDoseUnit', 
        'secondLigand', 'secondLigandDose', 'secondLigandDoseUnit'
    ]
)

# generate new sample name mapping
# single ligand perturbation naming format is {Ligand}-{LigandDose}_{Timepoint}_{ReplicateID}_{CollectionID}
# combo ligand perturbation naming format is {Ligand1}-{Ligand1Dose}_{Ligand2}-{Ligand2Dose}_{Timepoint}_{ReplicateID}_{CollectionID}
sample_id_map = {}
for row in sample_meta.itertuples(): 
    if row.secondLigand == 'none': 
        full_name = '_'.join([
            row.ligand.upper() + '-' + str(row.ligandDose) + row.ligandDoseUnit.replace('/', 'PER'),
            str(row.experimentalTimePoint) + row.timePointUnit, 
            'Rep' + row.replicate, 'Collection' + row.collection
        ])
    else: 
        full_name = '_'.join([
            row.ligand.upper() + '-' + str(row.ligandDose) + row.ligandDoseUnit.replace('/', 'PER'),
            row.secondLigand.upper() + '-' + str(row.secondLigandDose) + row.secondLigandDoseUnit.replace('/', 'PER'),
            str(row.experimentalTimePoint) + row.timePointUnit, 
            'Rep' + row.replicate, 'Collection' + row.collection
        ])
    sample_id_map[row.specimenID] = full_name

# save new sample names along with original metadata
sample_meta['new_sid'] = sample_meta['specimenID'].apply(lambda x: sample_id_map[x])
sample_meta.to_csv('metadata/MDD_sample_annotations_abr.csv', index=False)

# create gene symbol mappings for L1000/RNAseq data
l1000probe_meta = pd.read_csv('metadata/MDD_L1000_probeAnnotations.csv', usecols=['probeset', 'pr_gene_id', 'pr_gene_symbol']).set_index('probeset')
rnaprobe_meta = pd.read_csv('metadata/MDD_RNAseq_geneAnnotations.csv', usecols=['ensembl_gene_id', 'hgnc_symbol']).set_index('ensembl_gene_id')

for f in listdir(data_dir): 
    df = pd.read_csv(f"{data_dir}/{f}", index_col=0)
    if 'L1000' in f:
        # for L1000 data file, convert probeset IDs to gene symbols
        df.index = df.index.map(lambda x: l1000probe_meta.loc[x, 'pr_gene_symbol'])
        df.index = df.index.rename('gene')
    if 'RNAseq' in f: 
        # for RNAseq data file, convert Ensembl IDs to gene symbols
        df.index = df.index.map(lambda x: rnaprobe_meta.loc[x, 'hgnc_symbol'])
        df.index = df.index.rename('gene')
    df.columns = df.columns.map(lambda x: sample_id_map[x])
    # save new files with new gene/sample IDs to a separate directory
    mkdir(f"{data_dir}-annot")
    df.to_csv(f"{data_dir + '-annot'}/{f}")