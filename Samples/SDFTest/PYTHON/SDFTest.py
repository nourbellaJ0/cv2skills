#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *


# This sample illustrates how to use basic SDF API (also known as Cos) to edit an 
# existing document.

def main():
    PDFNet.Initialize(LicenseKey)
    
    # Relative path to the folder containing the test files.
    input_path = "../../TestFiles/"
    output_path = "../../TestFiles/Output/"
    
    print("Opening the test file...")
    
    # Here we create a SDF/Cos document directly from PDF file. In case you have 
    # PDFDoc you can always access SDF/Cos document using PDFDoc.GetSDFDoc() method.
    doc = SDFDoc(input_path + "fish.pdf")
    doc.InitSecurityHandler()
    
    print("Modifying info dictionary, adding custom properties, embedding a stream...")
    trailer = doc.GetTrailer()  # Get the trailer
    
    # Now we will change PDF document information properties using SDF API
    
    # Get the Info dictionary
    itr = trailer.Find("Info")
    info = Obj()
    if itr.HasCurrent():
        info = itr.Value()
        # Modify 'Producer' entry
        info.PutString("Producer", "PDFTron PDFNet")
        
        # Read title entry (if it is present)
        itr = info.Find("Author")
        if itr.HasCurrent():
            oldstr = itr.Value().GetAsPDFTest()
            info.PutText("Author", oldstr + "- Modified")
        else:
            info.PutString("Author", "Me, myself, and I")
    else:
        # Info dict is missing.
        info = trailer.PutDict("Info")
        info.PutString("Producer", "PDFTron PDFNet")
        info.PutString("Title", "My document")
        
    # Create a custom inline dictionary within Info dictionary
    custom_dict = info.PutDict("My Direct Dict")
    custom_dict.PutNumber("My Number", 100)     # Add some key/value pairs
    custom_dict.PutArray("My Array")
    
    # Create a custom indirect array within Info dictionary
    custom_array = doc.CreateIndirectArray()
    info.Put("My Indirect Array", custom_array)    # Add some entries
    
    # Create indirect link to root
    custom_array.PushBack(trailer.Get("Root").Value())
    
    # Embed a custom stream (file mystream.txt).
    embed_file = MappedFile(input_path + "my_stream.txt")
    mystm = FilterReader(embed_file)
    custom_array.PushBack( doc.CreateIndirectStream(mystm) )
    
    # Save the changes.
    print("Saving modified test file...")
    doc.Save(output_path + "sdftest_out.pdf", 0, "%PDF-1.4")
    doc.Close()
    
    PDFNet.Terminate()
    print("Test Completed")
    
if __name__ == '__main__':
    main()