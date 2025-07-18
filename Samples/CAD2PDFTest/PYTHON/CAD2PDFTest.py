#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

# Relative path to the folder containing test files.
input_path = "../../TestFiles/CAD/"
output_path = "../../TestFiles/Output/"

# ---------------------------------------------------------------------------------------
# The following sample illustrates how to use CAD module
# --------------------------------------------------------------------------------------

def main():

    # The first step in every application using PDFNet is to initialize the
    # library and set the path to common PDF resources. The library is usually
    # initialized only once, but calling Initialize() multiple times is also fine.
    PDFNet.Initialize(LicenseKey)
    
    # The location of the CAD Module
    PDFNet.AddResourceSearchPath("../../../PDFNetC/Lib/")

    if not CADModule.IsModuleAvailable():

        print("""
        Unable to run CAD2PDFTest: PDFTron SDK CAD module not available.
        ---------------------------------------------------------------
        The CAD module is an optional add-on, available for download
        at https://dev.apryse.com/. If you have already downloaded this
        module, ensure that the SDK is able to find the required files
        using the PDFNet::AddResourceSearchPath() function.""")

    else:

        inputFileName = "construction drawings color-28.05.18.dwg"
        outputFileName = inputFileName + ".pdf"
        doc = PDFDoc()
        Convert.FromCAD(doc, input_path + inputFileName, None)
        doc.Save(output_path + outputFileName, 0)

    PDFNet.Terminate()
    print("CAD2PDF conversion example")


if __name__ == '__main__':
    main()