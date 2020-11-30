import numpy as np 
import pandas as pd 
import h5py
import os

# get instance metadata
inst_file = "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE92742&format=file&file=GSE92742_Broad_LINCS_inst_info.txt.gz"
df = pd.read_csv(inst_file, sep='\t')

# sort by well and plate number
df_sorted = df.sort_values(by=['rna_well', 'rna_plate'])
df_sorted.reset_index(inplace=True)

# obtain biological replicate sets
rep_dict = {}
for row in df_sorted.itertuples():
    if str(row.pert_dose).startswith('-'):
        batch_id = '_'.join([row.inst_id.split('_X')[0],
                        row.rna_well,
                        row.pert_iname.replace('/', '_or_')])
    else:
        batch_id = '_'.join([row.inst_id.split('_X')[0], 
                        row.rna_well, 
                        row.pert_iname.replace('/', '_or_'), 
                        f"{row.pert_dose:.2f}{row.pert_dose_unit.replace('/', '_per_')}"])
    if batch_id not in rep_dict.keys():
        rep_dict[batch_id] = [row]
    else:
        if (rep_dict[batch_id][0].rna_well == row.rna_well 
                and rep_dict[batch_id][0].pert_iname == row.pert_iname
                and f"{rep_dict[batch_id][0].pert_dose:.2f}" == f"{row.pert_dose:.2f}"
                and rep_dict[batch_id][0].pert_time == row.pert_time):
            rep_dict[batch_id].append(row)
        else:
            print(rep_dict[batch_id][0], '\n\n', row)
            raise Exception("no match somehow")

# get actual expression data
f = h5py.File('https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE92742&format=file&filGSE92742_Broad_LINCS_Level3_INF_mlr12k_n1319138x12328.gctx', 'r')

# get gene expression matrix
dset = f['0']['DATA']['0']['matrix']

# get column/row names and convert to UTF string
col_mat = f['0']['META']['COL']['id'].value.astype(str)
row_mat = f['0']['META']['ROW']['id'].value.astype(str)

# get gene symbol mappings 
gene_info = pd.read_csv('Homo_sapiens.gene_info', sep='\t', dtype='U')
gene_info = gene_info[['GeneID', 'Symbol']]

gene_symbols = []
replacement_mappings = {
    '80761': 'UPK3B',
    '9142': 'TMEM257',
    '10896': 'OCLM',
    '23285': 'KIAA1107',
    '100507424': 'LOC100507424',
    '25787': 'DGCR9',
    '79686': 'LINC00341',
    '26148': 'C10orf12',
    '117153': 'MIA2'
}
for gene_id in row_mat:
    try: 
        gene_symbols.append(gene_info.loc[gene_info['GeneID'] == gene_id, 'Symbol'].iloc[0])
    except:
        gene_symbols.append(replacement_mappings[gene_id])

# divide expression data into replicate sets
for key in rep_dict.keys():
    filename = 'rep_sets/L1000_LINCS_DCIC_' + key + '.tsv'
    if os.path.exists(filename): 
        continue
    rep_array = []
    cols = []
    for inst in rep_dict[key]:
        inst_id = inst.inst_id
        cols.append(inst_id)
        inst_id_idx = np.where(col_mat == inst_id)[0][0]
        rep_array.append(dset[inst_id_idx,:][:])
    pd.DataFrame(rep_array, columns=gene_symbols, index=cols).T.to_csv(filename, sep='\t', index_label='symbol')