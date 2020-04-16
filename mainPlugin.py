# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
import resources
from Project import SovzondABTOMainWindow
from Project import SovzondCMRMainWindow
from Project import SovzondCMR2MainWindow
from Project import SovzondLandsatMainWindow
from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtSql import *
from PyQt4 import QtCore, QtGui
from osgeo import ogr
import sys
import cv2
import numpy as np
import pickle
import os
import os, math, time, subprocess, sys
import osr, ogr, gdal
from gdalconst import GA_ReadOnly, GRA_Cubic, GDT_Byte, GDT_UInt16, GDT_Float32
import numpy as np
from PIL import Image
import cv2
import vector_lib
import os, math, time, sys
import osr, ogr, gdal
from gdalconst import GA_ReadOnly, GRA_Cubic, GDT_Byte, GDT_UInt16, GDT_Float32
import numpy as np
import cv2
import vector_lib
import ForestMask, ChangeMask
# initialize Qt resources from file resources.py
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
class TestPlugin:
  def __init__(self, iface):
    # save reference to the QGIS interface
    self.iface = iface
  def initGui(self):
    try:
       self.toolbar = self.iface.addToolBar(u"Лесное хозяйство")
       # create action that will start plugin configuration
       #action 1
       icons = ["autovector.png","forest.png","forestfire.png","layerstacking.png"]
       pathToIcons = ":/plugins/ForestTools/icons/"
       icons = [pathToIcons + x for x in icons]
       methods = ["runABTO","runCMR","runCMR2","runLandsat"]
       names = [u"Векторизация изменений",u"Выявление территорий",
                u"Выявление гарей",u"Создание синтезов и композитов"]
       methods = ["self." + x for x in methods]
       for i in range(len(methods)):
          self.action = QAction(QIcon(icons[i]), names[i], self.iface.mainWindow())
          QObject.connect(self.action,SIGNAL("triggered()"),eval(methods[i]))
          self.toolbar.addAction(self.action)
       QObject.connect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)
    except Exception as inst:
       print inst.args
       x, y = inst.args
       QtGui.QMessageBox.critical(None,x,y)
  def unload(self):
    # remove the plugin menu item and icon
    self.iface.removePluginMenu("&Test plugins", self.action)
    self.iface.removeToolBarIcon(self.action)
    # disconnect form signal of the canvas
    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)
  def justShowMeWindow(self,window):
      ui = window()
      ui.show()
      return ui

  ''' ABTO '''
  def runABTO(self):
      self.uiABTO = self.justShowMeWindow(SovzondABTOMainWindow)
      QObject.connect(self.uiABTO.pushButton,SIGNAL("clicked()"),self.pushButtonABTOUi)
      QObject.connect(self.uiABTO.pushButton_2,SIGNAL("clicked()"),self.uiABTO.deleteLater)
      map(self.uiABTO.comboBox.addItem,self.getRasterPaths())
      map(self.uiABTO.comboBox_2.addItem,self.getRasterPaths())
      QObject.connect(self.uiABTO.toolButton,SIGNAL("clicked()"),self.openDirectorShpABTOUi)
      QObject.connect(self.uiABTO.toolButton_2,SIGNAL("clicked()"),self.openDirectorTifABTOUi)
      pass
  def openDirectorShpABTOUi(self):
      self.uiABTO.lineEdit.setText(self.openDirectoryDialog(self.uiABTO) + '_outputChange.shp')
      pass
  def openDirectorTifABTOUi(self):
      self.uiABTO.lineEdit_2.setText(self.openDirectoryDialog(self.uiABTO) + '_outputChange.tif')
      pass
  def pushButtonABTOUi(self):
      start_image = self.uiABTO.comboBox.currentText()
      fin_image = self.uiABTO.comboBox_2.currentText()
      min_countur_area= int(self.uiABTO.spinBox_2.text())
      min_change= int(self.uiABTO.spinBox.text())
      output_shapefile= self.uiABTO.lineEdit.text()
      output_cirfile= self.uiABTO.lineEdit_2.text()
      if output_shapefile == "":
          self.errorMessage(u"Задайте shp-файл")
          return
      if output_cirfile == "":
          self.errorMessage(u"Задайте tif-файл")
          return
      ChangeMask.ChangeMask(start_image, fin_image, min_countur_area, min_change, output_shapefile, output_cirfile)

  ''' forest '''
  def runCMR(self):
      self.uiCMR = self.justShowMeWindow(SovzondCMRMainWindow)
      self.getNamesToCombobox(self.uiCMR.comboBox)
      QObject.connect(self.uiCMR.pushButton,SIGNAL("clicked()"),self.pushButtonForestUi)
      QObject.connect(self.uiCMR.toolButton,SIGNAL("clicked()"),self.openDirectorShpForestUi)
      QObject.connect(self.uiCMR.toolButton_2,SIGNAL("clicked()"),self.openDirectorTifForestUi)
      QObject.connect(self.uiCMR.pushButton_2,SIGNAL("clicked()"),self.uiCMR.deleteLater)
  def openDirectorShpForestUi(self):
      self.uiCMR.lineEdit.setText(self.openDirectoryDialog(self.uiCMR) + '_753outputForest.shp')
      pass
  def openDirectorTifForestUi(self):
      self.uiCMR.lineEdit_6.setText(self.openDirectoryDialog(self.uiCMR) + '_542outputForest.tif')
      pass
  def pushButtonForestUi(self):
      input_image = self.uiCMR.comboBox.currentText()
      min_countur_area= int(self.uiCMR.lineEdit_7.text())
      red=[int(self.uiCMR.lineEdit_2.text()),int(self.uiCMR.lineEdit_3.text())]
      nir=[int(self.uiCMR.lineEdit_4.text()),int(self.uiCMR.lineEdit_5.text())]
      output_shapefile= self.uiCMR.lineEdit.text()
      output_cirfile= self.uiCMR.lineEdit_6.text()
      if output_shapefile == "":
          self.errorMessage(u"Задайте shp-файл")
          return
      if output_cirfile == "":
          self.errorMessage(u"Задайте tif-файл")
          return
      # self.informationMessage("Nir: " + str(red[0]) + str(red[1]))
      # self.informationMessage("Red: " + str(nir[0]) + str(nir[1]))
      #self.informationMessage(input_image + " tut " + str(min_countur_area) + " " + output_shapefile + " " + output_cirfile)
      ForestMask.min_countur_area = min_countur_area
      ForestMask.input_image = input_image
      ForestMask.output_shapefile = output_shapefile
      ForestMask.output_cirfile = output_cirfile
      ForestMask.ForestMask(input_image,red,nir,output_shapefile,output_cirfile)

  ''' burned  '''
  def runCMR2(self):
      self.uiCMR2 = self.justShowMeWindow(SovzondCMR2MainWindow)
      self.getNamesToCombobox(self.uiCMR2.comboBox)
      QObject.connect(self.uiCMR2.pushButton,SIGNAL("clicked()"),self.pushButtonBurnedUi)
      QObject.connect(self.uiCMR2.toolButton,SIGNAL("clicked()"),self.openDirectorShpBurnedUi)
      QObject.connect(self.uiCMR2.toolButton_2,SIGNAL("clicked()"),self.openDirectorTifBurnedUi)
      QObject.connect(self.uiCMR2.pushButton_2,SIGNAL("clicked()"),self.uiCMR2.deleteLater)
  def openDirectorShpBurnedUi(self):
      self.uiCMR2.lineEdit.setText(self.openDirectoryDialog(self.uiCMR2) + '_753outputForest.shp')
      pass
  def openDirectorTifBurnedUi(self):
      self.uiCMR2.lineEdit_2.setText(self.openDirectoryDialog(self.uiCMR2) + '_542outputForest.tif')
      pass
  def pushButtonBurnedUi(self):
      input_image = self.uiCMR2.comboBox.currentText()
      min_area= self.uiCMR2.spinBox.value()
      index_value= self.uiCMR2.doubleSpinBox.value()
      output_shapefile= self.uiCMR2.lineEdit.text()
      output_cirfile= self.uiCMR2.lineEdit_2.text()
      if output_shapefile == "":
          self.errorMessage(u"Задайте shp-файл")
          return
      if output_cirfile == "":
          self.errorMessage(u"Задайте tif-файл")
          return
      self.burnedMask(input_image,min_area,index_value,output_shapefile,output_cirfile)
      pass
  def burnedMask(self,input_image,min_area,index_value,output_shapefile,output_imagefile):
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

      def BurnedMask(input_image, index_value, min_area, output_shapefile='', output_imagefile=''):
          np.seterr(divide='ignore', invalid='ignore')
          image_ds=gdal.Open ( input_image, GA_ReadOnly )
          if image_ds is not None:
              if image_ds.RasterCount<6:
                  print 'Need image with more than 5 bands '
                  print 'Need GREEN, NIR, SWIR1 and  SWIR2'
              else:
                  dir_name=os.path.dirname(input_image)
                  file_name=os.path.basename(input_image).split('.')[0]
                  image_metadata=ImageMetadata(file_name)
                  if image_metadata['sensor'] in ['L5','L7','L8']:
                      if output_shapefile=='':output_shapefile=os.path.join(dir_name, file_name+'_burned_mask.SHP')
                      if output_imagefile=='':output_imagefile=os.path.join(dir_name, file_name+'_%s.TIF')
                      fieldnames=["DATA", "SENSOR", "IMG_FILE", "AREA"]
                      fields={"DATA":('string',8), "SENSOR":('string',5), "IMG_FILE":('string',64), "AREA":('float',6,2)}
                      fields_value={"DATA":image_metadata['date'], "SENSOR":image_metadata['sensor'], "IMG_FILE":input_image, "AREA":None}
                      band_data_green=image_ds.GetRasterBand(2).ReadAsArray().astype(np.int16)
                      band_data_red=image_ds.GetRasterBand(3).ReadAsArray().astype(np.int16)
                      band_data_swir1=image_ds.GetRasterBand(5).ReadAsArray().astype(np.int16)
                      band_data_nir=image_ds.GetRasterBand(4).ReadAsArray().astype(np.float32)
                      band_data_swir2=image_ds.GetRasterBand(6).ReadAsArray().astype(np.float32)
                      nbr1=band_data_nir-band_data_swir2
                      nbr2=band_data_nir+band_data_swir2
                      indxZeros=np.where(nbr2==0)
                      indxNonZeros=np.where(nbr2!=0)
                      nbr=np.empty(nbr2.shape)
                      nbr[indxZeros]=0
                      nbr[indxNonZeros]=nbr1[indxNonZeros]/nbr2[indxNonZeros]
                      indxZeros=np.where(nbr>=index_value)
                      indxNonZeros=np.where(nbr<index_value)
                      nbr[indxZeros]=0
                      nbr[indxNonZeros]=255
                      indxZeros=np.where(nbr2==0)
                      nbr = cv2.GaussianBlur(nbr.astype(np.uint8),(5,5),0)
                      nbr[nbr<60]=0
                      nbr[nbr>=60]=255
                      indxZeros=np.where(band_data_green==0)
                      nbr[indxZeros]=0
                      indxZeros=np.where(band_data_red==0)
                      nbr[indxZeros]=0
                      if min_area=='':min_area=60*image_ds.GetGeoTransform()[1]*image_ds.GetGeoTransform()[1]
                      image753_ds = gdal.GetDriverByName("GTiff").Create( output_imagefile % ('753') , image_ds.RasterXSize, image_ds.RasterYSize,  3, GDT_UInt16)
                      image542_ds = gdal.GetDriverByName("GTiff").Create( output_imagefile % ('542') , image_ds.RasterXSize, image_ds.RasterYSize,  3, GDT_UInt16)
                      image753_ds.SetGeoTransform( image_ds.GetGeoTransform() )
                      image753_ds.SetProjection( image_ds.GetProjection() )
                      image753_ds.GetRasterBand(1).WriteArray(band_data_swir2.astype(np.int16))
                      image753_ds.GetRasterBand(2).WriteArray(band_data_swir1.astype(np.int16))
                      image753_ds.GetRasterBand(3).WriteArray(band_data_red.astype(np.int16))
                      image753_ds=None
                      image542_ds.SetGeoTransform( image_ds.GetGeoTransform() )
                      image542_ds.SetProjection( image_ds.GetProjection() )
                      image542_ds.GetRasterBand(1).WriteArray(band_data_swir1.astype(np.int16))
                      image542_ds.GetRasterBand(2).WriteArray(band_data_nir.astype(np.int16))
                      image542_ds.GetRasterBand(3).WriteArray(band_data_green.astype(np.int16))
                      image542_ds=None
                      vector_lib.Raster2VectorP(image_ds, nbr, output_shapefile+'_p.shp', fieldnames, fields, fields_value, min_area)
                      vector_lib.Raster2VectorM(image_ds, nbr, output_shapefile+'_m.shp', fieldnames, fields, fields_value, min_area)
                      if os.path.exists(output_shapefile):
                          return {'status':'OK', 'shp':output_shapefile}
                      else: return {'status':'ERROR', 'shp':''}
          else:
              return {'status':'ERROR', 'shp':''}

      result = BurnedMask(input_image, index_value, min_area, output_shapefile, output_imagefile)
      print result
  ''' Landsat '''
  def runLandsat(self):
      self.uiLandsat = self.justShowMeWindow(SovzondLandsatMainWindow)
      QObject.connect(self.uiLandsat.pushButton_2,SIGNAL("clicked()"),self.uiLandsat.deleteLater)
      layers = self.getLayersObject()
      for layer in layers:
          if layer.type() != QgsMapLayer.RasterLayer:
              continue
          # if not layer.source().endswith(".shp"):
          #     continue
          checkBox = self.addNewCheckBoxToScrollArea (layer.name(),self.uiLandsat,self.uiLandsat.scrollAreaWidgetContents,self.uiLandsat.verticalLayout_4)
  # ''' Satelite '''
  def renderTest(self, painter):
    # use painter for drawing to map canvas
    pass
  ''' work with layers '''
  def getLayersObject(self):
      return self.iface.legendInterface().layers()
  def getRasterPaths(self):
      res = []
      layers = self.getLayersObject()
      for layer in layers:
        layerType = layer.type()
        if layerType == QgsMapLayer.RasterLayer:
            res.append(layer.source())
      return res
  ''' messages '''
  def errorMessage(self,msg):
      QtGui.QMessageBox.critical(None,u"Ошибка",msg)
  def informationMessage(self,msg):
      QtGui.QMessageBox.information(None,u"Внимание",msg)
  def debugMessage(self,msg):
      debugFlag = True
      if debugFlag == True:
          QtGui.QMessageBox.information(None,u"Отладочная информация",msg)
  ''' interface features '''
  def getNamesToCombobox(self,comboBox):
      layers = self.getLayersObject()
      for layer in layers:
        layerType = layer.type()
        if layerType == QgsMapLayer.RasterLayer:
            comboBox.addItem(layer.source())
  def addNewCheckBoxToScrollArea(self,name,ui,scrollArea,layout):
    ui.checkBox = QtGui.QCheckBox(scrollArea)
    ui.checkBox.setText(_translate("m", name, None))
    layout.addWidget(ui.checkBox) # first scroll area
    return ui.checkBox
  def openDirectoryDialog(self,ui):
    dir = QtGui.QFileDialog.getExistingDirectory(ui,u"Открыть директорию")
    dir += '/'
    return dir
  def openFileDialog(self,ui,msg,filter, folder = "/"):
      '''
      :param ui:
      :param msg:
      :param filter: "Video Files (*.avi *.mp4 *.mov)"
      :return:
      '''
      fileName = QtGui.QFileDialog.getOpenFileName(ui,msg,folder,filter)
      return fileName
