from vimgextractor.root_lib_util import SingletonDecorator
from ROOT import gSystem
import logging
logger = logging.getLogger(__name__)
class VEGASStatus:
    __vegas_loaded = False
    def __init__(self):
        pass

    def loadVEGAS(self):
        if(not self.__vegas_loaded):
            logger.debug('Load VEGAS lib')
            if gSystem.Load("libVEGAScommon") not in [0,1]:
                raise Exception("Problem loading VEGAS Common libraries - please check this before proceeding")
            if gSystem.Load("libVEGASstage1") not in [0,1]:
                raise Exception("Problem loading VEGAS Stage 1 libraries - please check this before proceeding")
            if gSystem.Load("libVEGASstage2") not in [0,1]:
                raise Exception("Problem loading VEGAS Stage 2 libraries - please check this before proceeding")
            if gSystem.Load("libVEGASstage4") not in [0,1]:
                raise Exception("Problem loading VEGAS Stage 2 libraries - please check this before proceeding")
            if gSystem.Load("libVEGASstage5") not in [0,1]:
                raise Exception("Problem loading VEGAS Stage 5 libraries - please check this before proceeding")
            if gSystem.Load("libVEGASstage6") not in [0,1]:
                raise Exception("Problem loading VEGAS Stage 6 libraries - please check this before proceeding") 
            self.__vegas_loaded = True

VEGASStatus = SingletonDecorator(VEGASStatus)
