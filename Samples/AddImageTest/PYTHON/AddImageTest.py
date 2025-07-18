#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

#-----------------------------------------------------------------------------------
# This sample illustrates how to embed various raster image formats
# (e.g. TIFF, JPEG, JPEG2000, JBIG2, GIF, PNG, BMP, etc.) in a PDF document.
#
# Note: On Windows platform this sample utilizes GDI+ and requires GDIPLUS.DLL to
# be present in the system path.
#-----------------------------------------------------------------------------------

def main():
    PDFNet.Initialize(LicenseKey)
    
    # Relative path to the folder containing test files.
    input_path = "../../TestFiles/"
    output_path = "../../TestFiles/Output/"
    
    doc = PDFDoc()
    
    f = ElementBuilder()            # Used to build new Element objects
    writer = ElementWriter()        # Used to write Elements to the page
    
    page = doc.PageCreate()         # Start a new page
    writer.Begin(page)              # Begin writing to this page

    # ----------------------------------------------------------
    # Add JPEG image to the output file
    img = Image.Create(doc.GetSDFDoc(), input_path + "peppers.jpg")
    element = f.CreateImage(img, 50, 500, img.GetImageWidth()/2, img.GetImageHeight()/2)
    writer.WritePlacedElement(element)
    
    # ----------------------------------------------------------
    # Add a PNG image to the output file    
    img = Image.Create(doc.GetSDFDoc(), input_path + "butterfly.png")
    element = f.CreateImage(img, Matrix2D(100, 0, 0, 100, 300, 500))
    writer.WritePlacedElement(element)
    
    # ----------------------------------------------------------
    # Add a GIF image to the output file
    img = Image.Create(doc.GetSDFDoc(), input_path + "pdfnet.gif")
    element = f.CreateImage(img, Matrix2D(img.GetImageWidth(), 0, 0, img.GetImageHeight(), 50, 350))
    writer.WritePlacedElement(element)
    
    # ----------------------------------------------------------
    # Add a TIFF image to the output file
    
    img = Image.Create(doc.GetSDFDoc(), (input_path + "grayscale.tif"))
    element = f.CreateImage(img, Matrix2D(img.GetImageWidth(), 0, 0, img.GetImageHeight(), 10, 50))
    writer.WritePlacedElement(element)
    
    writer.End()                # Save the page
    doc.PagePushBack(page)      # Add the page to the document page sequence

    # ----------------------------------------------------------
    # Embed a monochrome TIFF. Compress the image using lossy JBIG2 filter.

    page = doc.PageCreate(Rect(0, 0, 612, 794))
    writer.Begin(page)          # begin writing to this page

    # Note: encoder hints can be used to select between different compression methods. 
    # For example to instruct PDFNet to compress a monochrome image using JBIG2 compression.
    hint_set = ObjSet();
    enc = hint_set.CreateArray();  # Initilaize encoder 'hint' parameter 
    enc.PushBackName("JBIG2");
    enc.PushBackName("Lossy");

    img = Image.Create(doc.GetSDFDoc(), input_path + "multipage.tif");
    element = f.CreateImage(img, Matrix2D(612, 0, 0, 794, 0, 0));
    writer.WritePlacedElement(element);

    writer.End()                   # Save the page
    doc.PagePushBack(page)         # Add the page to the document page sequence
    
    # ----------------------------------------------------------
    # Add a JPEG2000 (JP2) image to the output file
    
    # Create a new page
    page = doc.PageCreate()
    writer.Begin(page)             # Begin writing to the page
    
    # Embed the image
    img = Image.Create(doc.GetSDFDoc(), input_path + "palm.jp2")
    
    # Position the image on the page
    element = f.CreateImage(img, Matrix2D(img.GetImageWidth(), 0, 0, img.GetImageHeight(), 96, 80))
    writer.WritePlacedElement(element)
    
    # Write 'JPEG2000 Sample' text string under the image
    writer.WriteElement(f.CreateTextBegin(Font.Create(doc.GetSDFDoc(), Font.e_times_roman), 32))
    element = f.CreateTextRun("JPEG2000 Sample")
    element.SetTextMatrix(1, 0, 0, 1, 190, 30)
    writer.WriteElement(element)
    writer.WriteElement(f.CreateTextEnd())
    
    writer.End()                    # Finish writing to the page
    doc.PagePushBack(page)
    
    doc.Save((output_path + "addimage.pdf"), SDFDoc.e_linearized);
    doc.Close()
    PDFNet.Terminate()

    print("Done. Result saved in addimage.pdf...")

if __name__ == '__main__':
    main()
