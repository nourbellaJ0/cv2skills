#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

#---------------------------------------------------------------------------------------
# The following sample illustrates how to convert HTML pages to PDF format using
# the HTML2PDF class.
# 
# 'pdftron.PDF.HTML2PDF' is an optional PDFNet Add-On utility class that can be 
# used to convert HTML web pages into PDF documents by using an external module (html2pdf).
#
# html2pdf modules can be downloaded from https://dev.apryse.com.
#
# Users can convert HTML pages to PDF using the following operations:
# - Simple one line static method to convert a single web page to PDF. 
# - Convert HTML pages from URL or string, plus optional table of contents, in user defined order. 
# - Optionally configure settings for proxy, images, java script, and more for each HTML page. 
# - Optionally configure the PDF output, including page size, margins, orientation, and more. 
# - Optionally add table of contents, including setting the depth and appearance.
#---------------------------------------------------------------------------------------

def main():
    output_path = "../../TestFiles/Output/html2pdf_example"
    host = "https://docs.apryse.com"
    page0 = "/"
    page1 = "/all-products/"
    page2 = "/documentation/web/faq"

    # The first step in every application using PDFNet is to initialize the 
    # library and set the path to common PDF resources. The library is usually 
    # initialized only once, but calling Initialize() multiple times is also fine.
    PDFNet.Initialize(LicenseKey)
    
    # For HTML2PDF we need to locate the html2pdf module. If placed with the 
    # PDFNet library, or in the current working directory, it will be loaded
    # automatically. Otherwise, it must be set manually using HTML2PDF.SetModulePath.
    HTML2PDF.SetModulePath("../../../PDFNetC/Lib/")
    if not HTML2PDF.IsModuleAvailable():
        print("""
        Unable to run HTML2PDFTest: PDFTron SDK HTML2PDF module not available.
        ---------------------------------------------------------------
        The HTML2PDF module is an optional add-on, available for download
        at https://www.pdftron.com/. If you have already downloaded this
        module, ensure that the SDK is able to find the required files
        using the HTML2PDF.SetModulePath() function.""")
        return

    #--------------------------------------------------------------------------------
    # Example 1) Simple conversion of a web page to a PDF doc. 

    doc = PDFDoc()
    # now convert a web page, sending generated PDF pages to doc
    converter = HTML2PDF()
    converter.InsertFromURL(host + page0)
    converter.Convert(doc)
    doc.Save(output_path + "_01.pdf", SDFDoc.e_linearized)

    #--------------------------------------------------------------------------------
    # Example 2) Modify the settings of the generated PDF pages and attach to an
    # existing PDF document. 
    
    # open the existing PDF, and initialize the security handler
    doc = PDFDoc("../../TestFiles/numbered.pdf")
    doc.InitSecurityHandler()
    
    # create the HTML2PDF converter object and modify the output of the PDF pages
    converter = HTML2PDF()
    converter.SetPaperSize(PrinterMode.e_11x17)
    
    # insert the web page to convert
    converter.InsertFromURL(host + page0)
    
    # convert the web page, appending generated PDF pages to doc
    converter.Convert(doc)
    doc.Save(output_path + "_02.pdf", SDFDoc.e_linearized)
    #--------------------------------------------------------------------------------
    # Example 3) Convert multiple web pages
    
    doc = PDFDoc()
    converter = HTML2PDF()
    
    header = "<div style='width:15%;margin-left:0.5cm;text-align:left;font-size:10px;color:#0000FF'><span class='date'></span></div><div style='width:70%;direction:rtl;white-space:nowrap;overflow:hidden;text-overflow:clip;text-align:center;font-size:10px;color:#0000FF'><span>PDFTRON HEADER EXAMPLE</span></div><div style='width:15%;margin-right:0.5cm;text-align:right;font-size:10px;color:#0000FF'><span class='pageNumber'></span> of <span class='totalPages'></span></div>"
    footer = "<div style='width:15%;margin-left:0.5cm;text-align:left;font-size:7px;color:#FF00FF'><span class='date'></span></div><div style='width:70%;direction:rtl;white-space:nowrap;overflow:hidden;text-overflow:clip;text-align:center;font-size:7px;color:#FF00FF'><span>PDFTRON FOOTER EXAMPLE</span></div><div style='width:15%;margin-right:0.5cm;text-align:right;font-size:7px;color:#FF00FF'><span class='pageNumber'></span> of <span class='totalPages'></span></div>"
    converter.SetHeader(header)
    converter.SetFooter(footer)
    converter.SetMargins("1cm", "2cm", ".5cm", "1.5cm")
    
    settings = WebPageSettings()
    settings.SetZoom(0.5)
    converter.InsertFromURL(host + page0)
    converter.Convert(doc)

    # convert page 1 with the same settings, appending generated PDF pages to doc
    converter.InsertFromURL(host + page1, settings)
    converter.Convert(doc)

    # convert page 2 with different settings, appending generated PDF pages to doc
    another_converter = HTML2PDF()
    another_converter.SetLandscape(True)
    another_settings = WebPageSettings()
    another_settings.SetPrintBackground(False)
    another_converter.InsertFromURL(host + page2, another_settings)
    another_converter.Convert(doc)
    
    doc.Save(output_path + "_03.pdf", SDFDoc.e_linearized)
    
    #--------------------------------------------------------------------------------
    # Example 4) Convert HTML string to PDF. 
    
    doc = PDFDoc()
    converter = HTML2PDF()
    
    # Our HTML data
    html = "<html><body><h1>Heading</h1><p>Paragraph.</p></body></html>"
    
    # Add html data
    converter.InsertFromHtmlString(html)
    # Note, InsertFromHtmlString can be mixed with the other Insert methods.
    
    converter.Convert(doc)
    doc.Save(output_path + "_04.pdf", SDFDoc.e_linearized)

    #--------------------------------------------------------------------------------
    # Example 5) Set the location of the log file to be used during conversion. 

    doc = PDFDoc()
    # now convert a web page, sending generated PDF pages to doc
    converter = HTML2PDF()
    converter.SetLogFilePath("../../TestFiles/Output/html2pdf.log")
    converter.InsertFromURL(host + page0)
    converter.Convert(doc)
    doc.Save(output_path + "_05.pdf", SDFDoc.e_linearized)

    PDFNet.Terminate()
        
if __name__ == '__main__':
    main()
