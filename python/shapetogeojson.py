import os
import urllib.request
import zipfile
import shapefile
import datetime
from json import dumps


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
    atr = dict(zip(field_names, sr.record))
    m = sr.record[3].strftime('%Y%m')
    geom = sr.shape.__geo_interface__
    monthsdict[m].append(dict(type="Feature", \
        geometry=geom, properties=atr))

  # write a GeoJSON file for each month
  for key in monthsdict:
    geojson = open(filename + "-" + key + ".geojson", "w")
    geojson.write(dumps({"type": "FeatureCollection",\
      "features": monthsdict[key]}, indent=2, default=myconverter) + "\n")
    geojson.close()
    # End of processing.


def getunzipped(theurl, thedir):
  """
  Download a file from a url and unzip it
  """

  name = os.path.join(thedir, 'temp.zip')
  try:
    name, hdrs = urllib.request.urlretrieve(theurl, name)
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
  """Main - program execute"""
  getunzipped('http://terrabrasilis.dpi.inpe.br/download/deter-amz/deter-amz_all.zip', '../data') 
  shape2geojson("../data/deter_all.shp")


if __name__ == '__main__':
  main()

