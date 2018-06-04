# -*- coding: utf-8 -*-
"""
Module for main ImageExtractor class
Author: Tony T.Y. Lin
"""

import logging
import os

import tables
import numpy as np

import vimgextractor.row_types as row_types
import vimgextractor.image as image 
from vimgextractor.vegas_io import VARootFile 

logger = logging.getLogger(__name__)

class ImageExtractor:

    img_dtypes = {'VTS':'float32'}    
    IMAGE_SHAPES = image.IMAGE_SHAPES
    TEL_NUM_PIXELS = image.TEL_NUM_PIXELS 

    def __init__(self,
                 output_path,
                 storage_mode='tel_type',
                 img_mode='1D',
                 img_dim_order='channels_last',
                 force_all_telescopes=False,is_gamma=True,one_D_image_oversampled=False):
        if os.path.isdir(os.path.dirname(output_path)):
            self.output_path = output_path
        else:
            raise ValueError('Output file directory does not exist: {}.'.format(os.path.dirname(output_path)))                 

        if storage_mode in ['tel_type','tel_id']:
            self.storage_mode = storage_mode
        else:
            raise ValueError('Invalid storage mode: {}.'.format(storage_mode))

        if img_mode in ['1D','2D']:
            self.img_mode = img_mode
        else:
            raise ValueError('Invalid img_mode: {}.'.format(img_mode))        
        
        if img_dim_order in ['channels_first','channels_last']:
            self.img_dim_order = img_dim_order
        else:
            raise ValueError('Invalid dimension ordering: {}.'.format(img_dim_order))

        self.trace_converter= image.TraceConverter(
            self.img_dtypes,
            500,
            img_dim_order = self.img_dim_order
            )
        self.force_all_telescopes  = force_all_telescopes
        self.is_gamma    = is_gamma
        self.one_D_image_oversampled = one_D_image_oversampled
    def select_telescopes(self,data_file):
        """
        dummy method for getting telescope type for now. 
        """ 
        return {'VTS':[1,2,3,4]},4 

    def write_metadata(self,HDF5_file,data_file):
        attributes = HDF5_file.root._v_attrs
        if(self.is_gamma):
            attributes.particle_type   =   0
        else:
            attributes.particle_type   =   101

    def process_data(self,filename,max_events=None):
        #Open output hdf5 file
        f = tables.open_file(self.output_path, mode="a", title="Output File")
       
        # Open Root File 
        root_file = VARootFile(filename)
        self.write_metadata(f,root_file)

        selected_tels, num_tel = self.select_telescopes(root_file)
        arr_info = root_file.get_array_info() 

        if not f.__contains__('/Array_Info'):
            arr_table = f.create_table(f.root, 'Array_Info',
                                       row_types.Array,
                                       ("Table of array data"))

            arr_row = arr_table.row

            for tel_type in selected_tels:
                for tel_id in selected_tels[tel_type]:
                    arr_row["tel_id"] = arr_info[tel_id]['tel_id']
                    arr_row["tel_x"] = arr_info[tel_id]['tel_x']
                    arr_row["tel_y"] = arr_info[tel_id]['tel_y']
                    arr_row["tel_z"] = arr_info[tel_id]['tel_z']
                    arr_row["tel_type"] = arr_info[tel_id]['tel_type'] 
                    arr_row["run_array_direction"] = arr_info[tel_id]['run_array_direction'] 
                    arr_row.append()

        if not f.__contains__('/Telescope_Info'):
            tel_table = f.create_table(f.root, 'Telescope_Info',
                                       row_types.Tel,
                                       ("Table of telescope data"))

            descr = tel_table.description._v_colobjects
            descr2 = descr.copy()

            descr2["pixel_pos"] = tables.Float32Col(shape=(2, 54*54))

            tel_table2 = f.create_table(f.root, 'temp', descr2, "Table of telescope data")
            tel_table.attrs._f_copy(tel_table2)
            tel_table.remove()
            tel_table2.move(f.root, 'Telescope_Info')

            tel_row = tel_table2.row

            # add units to table attributes
            random_tel_type = "VTS" 
            random_tel_id = 0 
            tel_table2.attrs.tel_pos_units = str("aru")
            tel_row['tel_type'] = "VTS"
            posx,posy  = np.meshgrid(np.arange(0,54,dtype='float32'),np.arange(0,54,dtype='float32'))
            
            tel_row['pixel_pos'] = [posx.ravel(),posy.ravel()] 
            tel_row.append()
            
        
        
        #create event table
        if not f.__contains__('/Event_Info'):
            table = f.create_table(f.root, 'Event_Info',
                                   row_types.Event,
                                   "Table of Event metadata")

            descr = table.description._v_colobjects
            descr2 = descr.copy()

            if self.storage_mode == 'tel_type':
                for tel_type in selected_tels:
                    descr2[tel_type + '_indices'] = tables.Int32Col(shape=(len(selected_tels[tel_type])))
            elif self.storage_mode == 'tel_id':
                descr2["indices"] = tables.Int32Col(shape=(num_tel))

            table2 = f.create_table(f.root, 'temp', descr2, "Table of Events")
            table.attrs._f_copy(table2)
            table.remove()
            table2.move(f.root, 'Event_Info')

            #add units to table attributes
            table2.attrs.core_pos_units    = 'm' 
            table2.attrs.h_first_int_units = 'm' 
            table2.attrs.mc_energy_units   = 'TeV' 
            table2.attrs.alt_az_units      = 'rad' 

        #create image tables
        for tel_type in selected_tels:
            if self.img_mode == '2D':
                img_width = self.IMAGE_SHAPES[tel_type][0]
                img_length = self.IMAGE_SHAPES[tel_type][1]
    
                if self.img_dim_order == 'channels_first':
                    array_shape = (1,img_width,img_length)
                elif self.img_dim_order == 'channels_last':
                    array_shape = (img_width,img_length,1)

                np_type = np.dtype((np.dtype(self.img_dtypes[tel_type]), array_shape))
                columns_dict = {"image":tables.Col.from_dtype(np_type),"event_index":tables.Int32Col()}
            elif self.img_mode == '1D':
                array_shape = (image.TEL_NUM_PIXELS_OVER_SAMPLED[tel_type],) if self.one_D_image_oversampled else (image.TEL_NUM_PIXELS[tel_type],) 
                np_type = np.dtype((np.dtype(self.img_dtypes[tel_type]), array_shape))

                columns_dict = {"image_charge":tables.Col.from_dtype(np_type),
                                "event_index":tables.Int32Col(),
                                "image_peak_times":tables.Col.from_dtype(np_type)}

            description = type('description', (tables.IsDescription,), columns_dict)
            if self.storage_mode == 'tel_type':
                if not f.__contains__('/' + tel_type):
                    table = f.create_table(f.root,tel_type,description,"Table of {} images".format(tel_type))

                    #append blank image at index 0
                    image_row = table.row
                    
                    if self.img_mode == '2D':
                        image_row['image'] =  self.trace_converter.convert(np.zeros(500))  
 
                    elif self.img_mode == '1D':
                        shape = (image.TEL_NUM_PIXELS_OVER_SAMPLED[tel_type],) if self.one_D_image_oversampled else (image.TEL_NUM_PIXELS[tel_type],)
                        image_row['image_charge'] = np.zeros(shape,dtype=self.img_dtypes[tel_type])
                        image_row['image_peak_times'] = np.zeros(shape,dtype=self.img_dtypes[tel_type])
                        image_row['event_index'] = -1

                    image_row.append()
                    table.flush()
                     
            elif self.storage_mode == 'tel_id':
                for tel_id in selected_tels[tel_type]:

                    if not f.__contains__('/T' + str(tel_id)):
                        table = f.create_table(f.root,'T'+str(tel_id),description,"Table of T{} images".format(str(tel_id)))
                        #append blank image at index 0
                        image_row = table.row
                        
                        if self.img_mode == '2D':
                            image_row['image'] = self.trace_converter.convert(np.zeros(500))  
                        
                        elif self.img_mode == '1D':
                            shape = (image.TEL_NUM_PIXELS_OVER_SAMPLED[tel_type],) if self.one_D_image_oversampled else (image.TEL_NUM_PIXELS[tel_type],)
                            image_row['image_charge'] = np.zeros(shape,dtype=self.img_dtypes[tel_type])
                            image_row['image_peak_times'] = np.zeros(shape,dtype=self.img_dtypes[tel_type])
                            image_row['event_index'] = -1

                        image_row.append()
                        table.flush()

        # specify calibration and other processing options

        logger.info("Processing events...")

        event_count = 0
        passing_count = 0
        if(max_events is None):
            source = root_file.read_st2_calib_channel_charge(tels=[ i-1 for i in selected_tels[tel_type]],cleaning=None)   
        else:
            source = root_file.read_st2_calib_channel_charge(tels=[ i-1 for i in selected_tels[tel_type]],cleaning=None,stop_event=max_events)   

        for i,simData,event,tzero,triggeredTels in source:
            if((max_events is not None) and 
               (event_count > max_events)):
               break

            event_count += 1
     
            table = f.root.Event_Info
            table.flush()
            event_row = table.row
            event_index = table.nrows

            if self.storage_mode == 'tel_type':
                tel_index_vectors = {tel_type:[] for tel_type in selected_tels}
            elif self.storage_mode == 'tel_id':
                all_tel_index_vector = []

            for tel_type in selected_tels.keys():
                for tel_id in sorted(selected_tels[tel_type]):
                    if self.storage_mode == 'tel_type':
                        index_vector = tel_index_vectors[tel_type]
                    elif self.storage_mode == 'tel_id':
                        index_vector = all_tel_index_vector

                    if(self.force_all_telescopes):
                        triggeredTels=[1,2,3,4]        

                    if tel_id in triggeredTels:
                        pixel_vector = event[tel_id -1,:] 
                        timing_vector = tzero[tel_id -1,:] 
                        logger.debug('Storing image from tel_type {} ({} pixels)'.format(tel_type,len(pixel_vector)))

                        if self.storage_mode == 'tel_type':
                            table = eval('f.root.{}'.format(tel_type))
                        elif self.storage_mode == 'tel_id':
                            table = eval('f.root.T{}'.format(tel_id))
                        next_index = table.nrows
                        image_row = table.row
                        imgs       = self.trace_converter.convert(pixel_vector)
                        time_imgs  = self.trace_converter.convert(timing_vector)*4  
                        if self.img_mode == '2D':
                            image_row['image'] = imgs  

                        elif self.img_mode == '1D':
                            if(self.one_D_image_oversampled):
                                image_row['image_charge']     = imgs.reshape(array_shape).copy() 
                                image_row['image_peak_times'] = time_imgs.reshape(array_shape).copy() 
                            else:
                                image_row['image_charge']     =  pixel_vector.copy() 
                                image_row['image_peak_times'] =  timing_vector.copy() 
           
                        image_row["event_index"] = event_index

                        image_row.append()
                        index_vector.append(next_index)
                        table.flush()
                    else:
                        index_vector.append(0)

                if self.storage_mode == 'tel_type':
                    for tel_type in tel_index_vectors:
                        event_row[tel_type+'_indices'] = tel_index_vectors[tel_type]
                elif self.storage_mode == 'tel_id':
                    event_row['indices'] = all_tel_index_vector

                event_row['event_number'] = i 
                event_row['run_number']   = simData.fRunNum 
                event_row['particle_id']  = simData.fCORSIKAParticleID 
                event_row['core_x']       = simData.fCoreEastM 
                event_row['core_y']       = simData.fCoreSouthM*-1 
                event_row['h_first_int']  = 0 
                event_row['mc_energy']    = simData.fEnergyGeV/1000. 
                event_row['alt'] = simData.fPrimaryZenithDeg*np.pi*180. 
                event_row['az']  = simData.fPrimaryAzimuthDeg*np.pi*180.

                event_row.append()
                table.flush()
        f.root.Event_Info.flush()
        total_num_events = f.root.Event_Info.nrows

        f.close()

        logger.info("{} events read in file".format(event_count))
        logger.info("{} total events in output file.".format(total_num_events))
        logger.info("Done!")

