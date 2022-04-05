# Scripts for Converting Data into C2M2 Format
**From the April 2022 CFDE Cross-Pollination Meeting**

The files and code contained in this repository comprise a standalone demo of how LINCS metadata can be converted into C2M2 format. 
These files were used as part of a presentation from the CFDE Cross-Pollination Meeting on April 5, 2022; the full slides can 
be found [here](https://docs.google.com/presentation/d/1LryaA6F37aWNIYUnCbx-n_C5n77H9uZiFi5EyNLLb_I/edit?usp=sharing).

The notebook demo is *lincs_c2m2_demo_04052022.ipynb*. Note that while the version of the *C2M2_package.json* found in this repository was used for 
the demo, it is NOT updated. For the most recent schema, please check [here](https://osf.io/c63aw/). 

Files within *lincs_metadata* are LINCS-specific metadata mappings, and are generally generated from existing LINCS metadata, supplemented
with information extracted from the relevant ontologies. Most files were built through a combination of manual and programmatic methods, and required 
pulling information from multiple sources. 

Files with *lincs_data* are the example LINCS files used in the demo. 
