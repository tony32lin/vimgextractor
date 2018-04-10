# vimgextractor

vimagextractor is an image extractor for converting VEGAS Stage 2 File to HDF5 file.
## Prerequisite

Both VEGAS and a compatible ROOT( with PyRoot enabled) need to be installed. The installation script doesn't check for the existence of either at this stage. 

## Install

For installing and vimgextractor, it is recomended that you use anaconda's distribution of python enviornment.
Simply run:

> pip install .

And the required library will be installed.

# Usage

After installation, an executable script call extractIMGFromVEGAS_St2 will be installed (to /path_to_conda/bin if you are using anaconda). The usage is as follows:

> Usage: extractImgFromVEGAS_St2 [OPTIONS] VEGAS_ST2_FILE OUTPUT_FILE

> Options:
>  -n, --nevt INTEGER
>  -d, --debug
>  --help              Show this message and exit.

If the option -n is not used all the events will be converted.
