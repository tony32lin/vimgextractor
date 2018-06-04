import numpy as np 
import click
import logging
import os



logger = logging.getLogger(__name__)

def add_dir_name(fname):
    if(os.path.dirname(fname) == ''):
        return './' + fname
    else:
        return fname

@click.command()
@click.argument('vegas_st2_file',nargs=1,type=click.Path(exists=True))
@click.argument('output_file',nargs=1,type=click.Path(exists=False))
@click.option('--nevt','-n',nargs=1,type=int)
@click.option('--oversampled','-s',is_flag=True,default=False)
@click.option('--debug','-d',is_flag=True,default=False)
def cli(vegas_st2_file,output_file,nevt,oversampled,debug):
    if(debug):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger  = logging.getLogger(__name__)

    import vimgextractor.image_extractor as image_extractor

    output_file = add_dir_name(output_file)
    vegas_st2_file = add_dir_name(vegas_st2_file)
    ext = image_extractor.ImageExtractor(output_file,storage_mode="tel_type",
                                         img_mode="1D",force_all_telescopes=False,
                                         one_D_image_oversampled=oversampled)

    if(nevt is not None):
        ext.process_data(vegas_st2_file,max_events=nevt)
    else:
        ext.process_data(vegas_st2_file)
    
