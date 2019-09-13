import os
from urllib import request, parse
import zipfile
import shapefile
import datetime
from json import dumps, loads
from mapbox import Uploader
from dotenv import load_dotenv
from time import sleep
from random import randint
load_dotenv()

import os

"""
Make sure you have a .env file in the directory where this script is containing the following:

  MAPBOX_TOKEN=sk.somelongstringswithadot.anotherstring-mend
  MAPBOX_USER=yourusername

"""

mapbox_user = os.getenv("MAPBOX_USER")
mapbox_access_token = os.getenv("MAPBOX_TOKEN")

def uploadToMapbox(datadir):
  """
  Upload all the geojson files from a given directory to mapbox as tilesets
  """
  for file in os.listdir(datadir):
    filename = os.fsdecode(file)
    if filename.endswith(".geojson"): 
      print(os.path.splitext(file)[0])
      mapboxUpload(os.path.join(datadir, file), os.path.splitext(file)[0])
      continue
    else:
      continue

def mapboxUpload(filename):
  """
  See: https://mapbox-mapbox.readthedocs-hosted.com/en/latest/uploads.html#uploads
  """

  #raise NotImplementedError("MapboxUpload is not implemented yet")

  service = Uploader()
  service.session.params['access_token'] = mapbox_access_token
  mapid = 'uploads-test' # 'uploads-test'
  with open(filename, 'rb') as src:
    upload_resp = service.upload(src, mapid)

    if upload_resp.status_code == 422:
      for i in range(5):
        sleep(5)
        with open(filename, 'rb') as src:
          upload_resp = service.upload(src, mapid)
        if upload_resp.status_code != 422:
          break
    
    upload_id = upload_resp.json()['id']
    for i in range(5):
      status_resp = service.status(upload_id).json()
      if status_resp['complete']:
        print(status_resp)
        print("Finished uploading tileset " + mapid)
        break
      sleep(5)

def writegeojson(filename, key, dict):
  geojson = open(filename + "-" + key + ".geojson", "w")
  geojson.write(dumps({"type": "FeatureCollection",\
    "features": dict[key]}, indent=2, default=myconverter) + "\n")
  geojson.close()

def writecsv(filename, key, dict):
  csv = open(filename + "-" + key + ".csv", "w")
  print (";".join(dict[key][0]['properties'].keys()), file=csv)
  for item in dict[key]:
    itemvaluelist = list(item['properties'].values())
    itemvaluelist[0] = str(itemvaluelist[0])
    itemvaluelist[4] = itemvaluelist[4].strftime('%Y-%m-%d')
    itemvaluelist[8] = ('%.16f' % itemvaluelist[8]).rstrip('0').rstrip('.')
    itemvaluelist[9] = ('%.16f' % itemvaluelist[9]).rstrip('0').rstrip('.')
    itemvaluelist[10] = ('%.16f' % itemvaluelist[10]).rstrip('0').rstrip('.')
    print (";".join(itemvaluelist), file=csv)
  csv.close()

def myconverter(o):
  """
  DateTime objects need to be converted otherwise json will throw an error 
  See: https://code-maven.com/serialize-datetime-object-as-json-in-python
  """

  if isinstance(o, datetime.date):
        return o.strftime('%Y-%m-%d')


def shape2geojson(filename):
  """
  When the zip is downloaded and converted to shape, 
  we pass the filename to shape2geojson
  to create a geojson file.
  We can do a lot of extra's here, like split the geojson to multiple files.
  """

  # read the shapefile
  reader = shapefile.Reader(filename)
  fields = reader.fields[1:]
  field_names = [field[0] for field in fields]
  field_names.insert(0,"ROW_NUMBER")
  months = []
  
  # We gather all the unique months..
  for sr in reader.shapeRecords():
    try:
      i = months.index(sr.record[3].strftime('%Y%m'))
    except ValueError:
      months.append(sr.record[3].strftime('%Y%m'))

  # Then turn it into a dictionary with empty arrays..
  monthsdict = dict()
  months.sort() 
  for m in months:
    monthsdict.update({m: []})

  # Add the features to the dictionary for the given months..
  for sr in reader.shapeRecords():
    rawatt = sr.record
    rawatt.insert(0,sr.record.oid)
    atr = dict(zip(field_names, rawatt))
    m = sr.record[4].strftime('%Y%m')
    geom = sr.shape.__geo_interface__
    monthsdict[m].append(dict(type="Feature", \
        geometry=geom, properties=atr))

  # write a GeoJSON file for each month
  for key in monthsdict:
    writegeojson(filename, key, monthsdict)
    writecsv(filename, key, monthsdict)
    # End of processing.


def getunzipped(theurl, thedir):
  """
  Download a file from a url and unzip it
  """

  name = os.path.join(thedir, 'temp.zip')
  try:
    name, hdrs = request.urlretrieve(theurl, name)
  except IOError as e:
    print ("Can't retrieve %r to %r: %s" % (theurl, thedir, e))
    return
  try:
    z = zipfile.ZipFile(name)
  except zipfile.error as e:
    print ("Bad zipfile (from %r): %s" % (theurl, e))
    return
  z.extractall(thedir)
  z.close()
  os.unlink(name)


def main():
  """
  Main - program execute
  """

  datadir = '../data/'
  getunzipped('http://terrabrasilis.dpi.inpe.br/download/deter-amz/deter-amz_all.zip', datadir) 
  shape2geojson("../data/deter_all.shp")
  uploadToMapbox(datadir)
  exit()

if __name__ == '__main__':
  main()

