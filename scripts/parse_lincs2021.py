import numpy as np 
import pandas as pd 
import h5py
import os

def get_pert_name(row):
    '''
    Get name of perturbagen. 
    '''
    if pd.isnull(row.cmap_name):
        name = row.pert_id 
    else:
        name = row.cmap_name
    return name.replace('/', '_or_').replace('|', '-').replace(' ','')


def get_gene_map(g):
    '''
    Get mappings for genes. 
    '''
    gene_info = pd.read_csv(
        'cmap_metadata/geneinfo_beta.txt', 
        sep='\t', dtype='U'
    )[['gene_id', 'gene_symbol']]
    gene_symbol_map = {
        row.gene_id: row.gene_symbol for row in gene_info.itertuples
    }
    return gene_symbol_map


def get_pert_metadata():
    '''
    Divide the full metadata into perturbation-specific metadata:
        xpr (CRISPR)
        sh (shRNA)
        cp (chemical perturbation)
        oe (overexpression)
        misc (ligands/antibodies/siRNA: trt_lig, trt_aby, trt_si)
        ctl (vector and vehicle controls: ctl_vector, ctl_vehicle)
    '''
    df = pd.read_csv('inst_info/instinfo_beta.txt', sep='\t')
    perts = {
        'xpr': ['trt_xpr'],
        'sh': ['trt_sh'],
        'cp': ['trt_cp'],
        'oe': ['trt_oe'],
        'misc': ['trt_lig', 'trt_aby', 'trt_si'],
        'ctl': ['ctl_vector', 'ctl_vehicle']
    }
    for p in perts.keys():
        sub_df = df[df['pert_type'].isin(perts[p])]
        sub_df.to_csv(f"inst_info/instinfo_{p}.txt", sep='\t', index=False)


def get_instances(p, gene_map):
    '''
    Divide L1000 data into replicate instances, by perturbation type. 
    Perturbation types are as follows: 
        xpr (CRISPR)
        sh (shRNA)
        ctl (control)
        cp (chemical perturbation)
        oe (overexpression)

    The Broad Institute combines the following three types into a miscellaneous
    perturbation category "misc":
        lig (ligand)
        aby (antibody)
        si (siRNA)

    {gene_map} should be the output of the function get_gene_map
    '''

    print(f"NOW PROCESSING: {p} data")

    # get instance metadata
    # instance info can be manually divided by perturbation ahead of time,
    #   for ease of analysis
    inst_file = f"inst_info/instinfo_{p}.txt"
    df = pd.read_csv(inst_file, sep='\t', dtype={'cmap_name': 'str'})

    # sort by well and plate number
    df_sorted = df.sort_values(by=['det_well', 'det_plate'])
    df_sorted.reset_index(inplace=True)

    # obtain biological replicate sets
    print('...obtaining biological replicate sets...')
    rep_dict = {}
    for row in df_sorted.itertuples():
        pert_name = get_pert_name(row)
        if pd.isnull(row.pert_idose):
            batch_id = '_'.join(row.sample_id.split('_')[:3] +
                            [row.det_well,
                            pert_name])
        else:
            batch_id = '_'.join(row.sample_id.split('_')[:3] +
                            [row.det_well, 
                            pert_name, 
                            row.pert_idose.replace(' ', '').replace('/', '_per_')])

        if batch_id not in rep_dict.keys():
            rep_dict[batch_id] = [row]
        else:
            rep_dict[batch_id].append(row)

    # get actual expression data
    f = h5py.File(f"data/level3_trt_{p}.gctx", 'r')

    # get gene expression matrix
    dset = f['0']['DATA']['0']['matrix']

    # get column/row names and convert to UTF string
    col_mat = f['0']['META']['COL']['id'][()].astype(str)
    row_mat = f['0']['META']['ROW']['id'][()].astype(str)

    # get gene symbol mappings 
    # gene metadata file obtained from CLUE
    gene_symbols = [gene_map[g] for g in row_mat]

    # divide expression data into replicate sets
    print("...creating replicate sets...")
    for key in rep_dict.keys():
        # ignore LITMUS tests
        if key.find('LITMUS') != -1:
            continue
        # check if file already created, in case of stopping/restarting
        filename = f"data/{p}/L1000_LINCS_DCIC_" + key + '.tsv'
        if os.path.exists(f"data/{p}/L1000_LINCS_DCIC_" + key + '.tsv'): 
            continue
        # slice matrix by relevant inst_ids
        inst_ids = [inst.sample_id for inst in rep_dict[key]]
        inst_mask = np.in1d(col_mat, inst_ids)
        pd.DataFrame(
            dset[inst_mask, :], 
            columns=gene_symbols, 
            index=inst_ids
        ).T.to_csv(
            filename, 
            sep='\t', 
            index_label='symbol'
        )

    f.close()