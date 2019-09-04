using System;
using System.Net;
using System.IO;
using System.IO.Compression;

namespace shape2geojson
{
    class Program
    {
        /*
        When the zip is downloaded and converted to shape, 
        we pass the filename to shape2geojson
        to create a geojson file.
        We can do a lot of extra's here, like split the geojson to multiple files.
        */
        static void shape2geojson(string filename)
        {
            throw new NotImplementedException();
        }

        /*
        Download a file from a url and unzip it
        */
        static void getunzipped(string theurl, string thedir)
        {
            string name = Path.Combine(thedir, "temp2.zip");
            WebClient myWebClient = new WebClient();
            try
            {
                myWebClient.DownloadFile(theurl, name);
            } catch (Exception e)
            {
                Console.WriteLine($"Can't retrieve {theurl} to {thedir}: {e.Message}");
            }
            try
            {
                ZipFile.ExtractToDirectory(name, "../data/");
            } catch (Exception e)
            {
                Console.WriteLine($"Bad zipfile (from {theurl}): {e.Message}");
            }
            
        }

        /* Main - Program execute */
        static void Main(string[] args)
        {
            getunzipped("http://terrabrasilis.dpi.inpe.br/download/deter-amz/deter-amz_all.zip", "../data");
            shape2geojson("../data/deter_all.shp");
        }

    }
}
