# LINCS-metadata/c2m2_level1/MCF10A-MDD
This subdirectory contains metadata files for the LINCS MCF10A Molecular Deep Dive (MDD) project in C2M2 format. Schema is current with the **November 2021** C2M2 release. 
The processing of this metadata was completed as part of the deliverable [Base Y2.103: Ingest the MCF10A Deep Dive data into C2M2 and SigCom LINCS](https://github.com/nih-cfde/LINCS/issues/112). 

In order to bypass the GitHub storage size issue in this repo, the MCF10A MDD metadata tables are stored separately from the full LINCS C2M2 metadata tables, which can be found in the parent directory `LINCS-metadata/c2m2_level1`. The files in this subdirectory are designed to be easily appended to the existing main LINCS C2M2 metadata tables of the same name, e.g. the `file.tsv` here can be concatenated to the end of the most recent version of `../file.tsv`. 

Any metadata files that are not included in this repo indicate that no addition was necessary to that file in order to accommodate the MCF10A metadata additions, e.g. there is no `subject.tsv` file here because the only subject studied under this project is the MCF10A cell line, which is already included in `../subject.tsv`. 

*Note: During submission to the CFDE portal, the full datapackage will include all MCF10A MDD metadata.*
