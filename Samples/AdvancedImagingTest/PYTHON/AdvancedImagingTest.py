#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

# Relative path to the folder containing test files.
input_path = "../../TestFiles/AdvancedImaging/"
output_path = "../../TestFiles/Output/"

# ---------------------------------------------------------------------------------------
# The following sample illustrates how to use Advanced Imaging module
# --------------------------------------------------------------------------------------

def main():

    # The first step in every application using PDFNet is to initialize the
    # library and set the path to common PDF resources. The library is usually
    # initialized only once, but calling Initialize() multiple times is also fine.
    PDFNet.Initialize(LicenseKey)

    # The location of the Advanced Imaging Module
    PDFNet.AddResourceSearchPath("../../../PDFNetC/Lib/")

    if not AdvancedImagingModule.IsModuleAvailable():

        print("""
        Unable to run AdvancedImagingTest: Apryse SDK Advanced Imaging module not available.
        -----------------------------------------------------------------------------
        The Advanced Imaging module is an optional add-on, available for download
        at https://docs.apryse.com/documentation/core/info/modules/. If you have already
        downloaded this module, ensure that the SDK is able to find the required files
        using the PDFNet.AddResourceSearchPath() function.""")

    else:
        try:
            inputFileName1 = "xray.dcm"
            outputFileName1 = inputFileName1 + ".pdf"
            doc1 = PDFDoc()
            Convert.FromDICOM(doc1, input_path + inputFileName1, None)
            doc1.Save(output_path + outputFileName1, SDFDoc.e_linearized)
        except Exception as e:
            print("Unable to convert DICOM test file, error: " + str(e))

        try:
            inputFileName2 = "jasper.heic"
            outputFileName2 = inputFileName2 + ".pdf"
            doc2 = PDFDoc()
            Convert.ToPdf(doc2, input_path + inputFileName2)
            doc2.Save(output_path + outputFileName2, SDFDoc.e_linearized)
        except Exception as e:
            print("Unable to convert the HEIC test file, error: " + str(e))

        try:
            inputFileName3 = "tiger.psd"
            outputFileName3 = inputFileName3 + ".pdf"
            doc3 = PDFDoc()
            Convert.ToPdf(doc3, input_path + inputFileName3)
            doc3.Save(output_path + outputFileName3, SDFDoc.e_linearized)
        except Exception as e:
            print("Unable to convert the PSD test file, error: " + str(e))

        print("Done.")

    PDFNet.Terminate()


if __name__ == '__main__':
    main()