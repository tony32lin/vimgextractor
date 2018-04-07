import numpy as np
from vimgextractor.squarecam import SquareCam

IMAGE_SHAPES = {"VTS":(54,54)}
TEL_NUM_PIXELS = {"VTS":2916}

class TraceConverter:
    def __init__(self,img_dtypes,pixvar_length,img_dim_order='channels_last'):
        self.img_dtypes = img_dtypes
        if img_dim_order in ['channels_first','channels_last']:
            self.img_dim_order = img_dim_order
        else:
            raise ValueError('Invalid dimension ordering: {}.'.format(img_dim_order))
        self.pixvar_length  = pixvar_length
        dummy_img           = np.zeros(pixvar_length)
        self.cam_           = SquareCam(dummy_img,pic_size=IMAGE_SHAPES['VTS'][0])

    def convert(self,charge):
        """
        :param charge: a numpy array of dimension (500, )
        :return: images numpy array of dimension (1, 54, 54) or (54,54,1)
        """
    
        self.cam_.load_pixVal(charge)
        img = self.cam_.get_simple_oversampled_image()
        img = img.astype(self.img_dtypes['VTS'])        
        if(self.img_dim_order == 'channels_first'):
            return img.reshape((1,IMAGE_SHAPES['VTS'][0],IMAGE_SHAPES['VTS'][1])) 
        else:
            return img.reshape((IMAGE_SHAPES['VTS'][0],IMAGE_SHAPES['VTS'][1],1)) 
