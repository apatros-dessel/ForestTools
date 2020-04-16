import os, math, time, subprocess, sys
import osr, ogr, gdal
from gdalconst import GA_ReadOnly, GRA_Cubic, GDT_Byte, GDT_UInt16, GDT_Float32
import numpy as np
from PIL import Image
import cv2
import vector_lib


start_image = 'c:\\CHANGE\\20140724_30m_L8_6b.TIF'
fin_image = 'c:\\CHANGE\\20150823_30m_L8_6b.TIF'
min_countur_area= 1
min_change= 10
output_shapefile=''
output_cirfile=''

def ImageMetadata(filename):
    metadata={'date':'','year':'','month':'','day':'','ps':'','sensor':'','numbands':''}
    temp=filename.split('_')
    metadata['date']=temp[0]
    metadata['year']=metadata['date'][:4]
    metadata['month']=metadata['date'][4:6]
    metadata['day']=metadata['date'][6:]
    metadata['ps']=temp[1]
    metadata['sensor']=temp[2]
    metadata['numbands']=temp[3].replace('b','')
    return metadata

def ChangeMask(start_image, fin_image, min_countur_area= 1, min_change= 10, output_shapefile='', output_cirfile=''):
    min_change = float(min_change)/100
    start_ds=gdal.Open ( start_image, GA_ReadOnly )
    fin_ds=gdal.Open ( fin_image, GA_ReadOnly )
    if (start_ds is not None) and (start_ds is not None):
        if start_ds.RasterCount < 3:
            print 'Start_ds must be 3 or bigger'
        elif start_ds.RasterCount != start_ds.RasterCount:
            print 'Start and Fin datasets must be equal'
        elif start_ds.GetGeoTransform() != fin_ds.GetGeoTransform():
            print 'Raster sizes must be the same'
        else:
            start_dir_name, start_name=os.path.split(start_image)
            start_name=start_name.split('.')[0]
            start_metadata=ImageMetadata(start_name)
            fin_dir_name, fin_name=os.path.split(fin_image)
            fin_name=fin_name.split('.')[0]
            fin_metadata=ImageMetadata(fin_name)
            if output_shapefile=='':output_shapefile=os.path.join(fin_dir_name, '%s_%s_change_mask.shp' % (start_name, fin_name))
            if output_cirfile=='':output_cirfile=os.path.join(fin_dir_name, '%s_%s_TCP.tif' % (start_name, fin_name))
            fieldnames=["DATA_1", "SENSOR_1", "IMG_FILE_1", "DATA_2", "SENSOR_2", "IMG_FILE_2", "AREA"]
            fields={"DATA_1":('string',8), "SENSOR_1":('string',5), "IMG_FILE_1":('string',64),\
                    "DATA_2":('string',8), "SENSOR_2":('string',5), "IMG_FILE_2":('string',64), "AREA":('float',6,2)}
            fields_value={"DATA_1":start_metadata['date'], "SENSOR_1":start_metadata['sensor'], "IMG_FILE_1":start_image,\
                          "DATA_2":fin_metadata['date'], "SENSOR_2":fin_metadata['sensor'], "IMG_FILE_2":fin_image, "AREA":None,}
            change_mask=np.ones((start_ds.RasterYSize, start_ds.RasterXSize), dtype=np.int8)

            for bandnum in range(1, start_ds.RasterCount+1):
                start_band = start_ds.GetRasterBand(bandnum).ReadAsArray().astype(np.float)
                fin_band = fin_ds.GetRasterBand(bandnum).ReadAsArray().astype(np.float)
                change_mask[abs(fin_band/start_band-1)<min_change] = 0
                change_mask[start_band==0] = 0
                change_mask[fin_band==0] = 0
            change_mask = cv2.GaussianBlur(change_mask.astype(np.uint8),(5,5),0)
            print start_metadata, fin_metadata
            cir_image_ds = gdal.GetDriverByName("GTiff").Create( output_cirfile , start_ds.RasterXSize, start_ds.RasterYSize,  3, GDT_UInt16)
            cir_image_ds.SetGeoTransform( start_ds.GetGeoTransform() )
            cir_image_ds.SetProjection( start_ds.GetProjection() )
            cir_image_ds.GetRasterBand(1).WriteArray(fin_ds.GetRasterBand(3).ReadAsArray().astype(np.int16))
            cir_image_ds.GetRasterBand(2).WriteArray(start_ds.GetRasterBand(3).ReadAsArray().astype(np.int16))
            cir_image_ds.GetRasterBand(3).WriteArray(fin_ds.GetRasterBand(2).ReadAsArray().astype(np.int16))
            for i in (1,2,3): cir_image_ds.GetRasterBand(i).SetNoDataValue(0)
            cir_image_ds=None
            min_area=min_countur_area*start_ds.GetGeoTransform()[1]*start_ds.GetGeoTransform()[1]
            vector_lib.Raster2VectorP(start_ds, change_mask, output_shapefile+'_p.shp', fieldnames, fields, fields_value, min_area)
            vector_lib.Raster2VectorM(start_ds, change_mask, output_shapefile+'_m.shp', fieldnames, fields, fields_value, min_area)
            if os.path.exists(output_cirfile) and os.path.exists(output_shapefile):
                return {'status':'OK', 'shp':output_shapefile, 'cir_img':output_cirfile}
            else: return {'status':'ERROR', 'shp':'', 'cir_img':''}
    else:
        return {'status':'ERROR', 'shp':'', 'cir_img':''}

#result = ForestMask(start_image, fin_image, min_countur_area, min_change, output_shapefile, output_cirfile)
#print result
