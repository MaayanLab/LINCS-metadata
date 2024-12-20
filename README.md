# LINCS-metadata
This repo was established to place the LINCS metadata files that were converted into C2M2 and other relevant formats 

## Cloning

Files in this repository regularly exceed github's 100MB and so we're forced to use `git-lfs`.

Please install git-lfs for your system using the instructions on <https://docs.github.com/en/github/managing-large-files/installing-git-large-file-storage>. This involves an independent binary which integrates with git. **After this is installed**, `git lfs install` will activate the extension on all repositories. Then cloning this repository will become seemless. Please note that issues with older versions of git have been reported, please ensure git is up to date before installing git lfs.

**Note:** As of the January 2022 release, the following files are no longer able to be updated with git-lfs due to exceeding the data quota: 
- file
- file_describes_biosample
- file_describes_subject
- biosample
- biosample_from_subject
- biosample_disease

For access to the most updated version of these files, please contact the LINCS team directly. All other files are up-to-date. 

## Older Releases

Looking for the older versions of this assessment? All main versions of this repo are accessed through the [Github Releases](https://github.com/nih-cfde/LINCS-metadata/releases).
