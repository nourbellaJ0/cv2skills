#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
import platform
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

#---------------------------------------------------------------------------------------
# The following sample illustrates how to convert PDF, XPS, image, MS Office, and 
# other image document formats to XOD format.
#
# Certain file formats such as PDF, generic XPS, EMF, and raster image formats can 
# be directly converted to XOD. Other formats such as MS Office 
# (Word, Excel, Publisher, Powerpoint, etc) can be directly converted via interop. 
# These types of conversions guarantee optimal output, while preserving important 
# information such as document metadata, intra document links and hyper-links, 
# bookmarks etc. 
#
# In case there is no direct conversion available, PDFNet can still convert from 
# any printable document to XOD using a virtual printer driver. To check 
# if a virtual printer is required use Convert::RequiresPrinter(filename). In this 
# case the installing application must be run as administrator. The manifest for this 
# sample specifies appropriate the UAC elevation. The administrator privileges are 
# not required for direct or interop conversions. 
#
# Please note that PDFNet Publisher (i.e. 'pdftron.PDF.Convert.ToXod') is an
# optionally licensable add-on to PDFNet Core SDK. For details, please see
# https://apryse.com/pricing.
#---------------------------------------------------------------------------------------

# Relative path to the folder containing the test files.
inputPath = "../../TestFiles/"
outputPath = "../../TestFiles/Output/"

def main():
    PDFNet.Initialize(LicenseKey)

    # Sample 1:
    # Directly convert from PDF to XOD.
    Convert.ToXod(inputPath + "newsletter.pdf", outputPath + "from_pdf.xod")

    # Sample 2:
    # Directly convert from generic XPS to XOD.
    Convert.ToXod(inputPath + "simple-xps.xps", outputPath + "from_xps.xod")

    # Sample 3:
    # Directly convert from PNG to XOD.
    print("Converting: " + inputPath + "butterfly.png" + " to: " + outputPath + "butterfly.xod")
    Convert.ToXod(inputPath + "butterfly.png", outputPath + "butterfly.xod")

    # Sample 4:
    print("Converting: " + inputPath + "numbered.pdf" + " to: " + outputPath + "numbered.xod")
    Convert.ToXod(inputPath + "numbered.pdf", outputPath + "numbered.xod")

    # Sample 5:
    # Directly convert from JPG to XOD.
    print("Converting: " + inputPath + "dice.jpg" + " to: " + outputPath + "dice.xod")
    Convert.ToXod(inputPath + "dice.jpg", outputPath + "dice.xod")

    # Sample 6:
    # Directly convert from generic XPS to XOD.
    print("Converting: " + inputPath + "simple-xps.xps" + " to: " + outputPath + "simple-xps.xod")
    Convert.ToXod(inputPath + "simple-xps.xps", outputPath + "simple-xps.xod")

    PDFNet.Terminate()
    print("Done.")

if __name__ == '__main__':
    main()