#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2025 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------



import sys
from apryse_sdk import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

#-----------------------------------------------------------------------------------------
# The sample code illustrates how to read and edit existing outline items and create 
# new bookmarks using the high-level API.
#-----------------------------------------------------------------------------------------

# Relattive path to the folder containing the test files.
input_path = "../../TestFiles/"
output_path = "../../TestFiles/Output/"

def PrintIndent(item):
    indent = item.GetIndent() - 1
    i = 0
    while i < indent:
        sys.stdout.write("  ")
        i = i + 1

# Prints out the outline tree to the standard output
def PrintOutlineTree (item):
    while item.IsValid():
        PrintIndent(item)
        if item.IsOpen():
            sys.stdout.write("- " + item.GetTitle() + " ACTION -> ")
        else:
            sys.stdout.write("+ " + item.GetTitle() + " ACTION -> ")
    
        # Print Action
        action = item.GetAction()
        if action.IsValid():
            if action.GetType() == Action.e_GoTo:
                dest = action.GetDest()
                if dest.IsValid():
                    page = dest.GetPage()
                    print("GoTo Page #" + str(page.GetIndex()))
            else:
                print("Not a 'GoTo' action")
        else:
            print("NULL")
    
        # Recursively print children sub-trees   
        if item.HasChildren():        
            PrintOutlineTree(item.GetFirstChild())
        item = item.GetNext()
            

def main():
    PDFNet.Initialize(LicenseKey)

    # The following example illustrates how to create and edit the outline tree
    # using high-level Bookmark methods.
    
    doc = PDFDoc(input_path + "numbered.pdf")
    doc.InitSecurityHandler()
    
    # Lets first create the root bookmark items. 
    red = Bookmark.Create(doc, "Red")
    green = Bookmark.Create(doc, "Green")
    blue = Bookmark.Create(doc, "Blue")
    
    doc.AddRootBookmark(red)
    doc.AddRootBookmark(green)
    doc.AddRootBookmark(blue)
    
    # You can also add new root bookmarks using Bookmark.AddNext("...")
    blue.AddNext("foo")
    blue.AddNext("bar")

    # We can now associate new bookmarks with page destinations:
    
    # The following example creates an 'explicit' destination (see 
    # section '8.2.1 Destinations' in PDF Reference for more details)
    itr = doc.GetPageIterator()
    red_dest = Destination.CreateFit(itr.Current())
    red.SetAction(Action.CreateGoto(red_dest))

    # Create an explicit destination to the first green page in the document
    green.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(10))))

    # The following example creates a 'named' destination (see 
    # section '8.2.1 Destinations' in PDF Reference for more details)
    # Named destinations have certain advantages over explicit destinations.
    key = bytearray(b"blue1")    
    blue_action = Action.CreateGoto(key, len(key), Destination.CreateFit(doc.GetPage(19)))
    
    blue.SetAction(blue_action)
    
    # We can now add children Bookmarks
    sub_red1 = red.AddChild("Red - Page 1")
    sub_red1.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(1))))
    sub_red2 = red.AddChild("Red - Page 2")
    sub_red2.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(2))))
    sub_red3 = red.AddChild("Red - Page 3")
    sub_red3.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(3))))
    sub_red4 = sub_red3.AddChild("Red - Page 4")
    sub_red4.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(4))))
    sub_red5 = sub_red3.AddChild("Red - Page 5")
    sub_red5.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(5))))
    sub_red6 = sub_red3.AddChild("Red - Page 6")
    sub_red6.SetAction(Action.CreateGoto(Destination.CreateFit(doc.GetPage(6))))
    
    # Example of how to find and delete a bookmark by title text.
    foo = doc.GetFirstBookmark().Find("foo")
    if foo.IsValid():
        foo.Delete()
    else:
        raise Exception("Foo is not Valid")
    
    bar = doc.GetFirstBookmark().Find("bar")
    if bar.IsValid():
        bar.Delete()
    else:
        raise Exception("Bar is not Valid")
    
    # Adding color to Bookmarks. Color and other formatting can help readers 
    # get around more easily in large PDF documents.
    red.SetColor(1, 0, 0);
    green.SetColor(0, 1, 0);
    green.SetFlags(2);            # set bold font
    blue.SetColor(0, 0, 1);
    blue.SetFlags(3);             # set bold and itallic
    
    doc.Save(output_path + "bookmark.pdf", 0)
    doc.Close()
    print("Done. Result saved in bookmark.pdf")

    # The following example illustrates how to traverse the outline tree using 
    # Bookmark navigation methods: Bookmark.GetNext(), Bookmark.GetPrev(), 
    # Bookmark.GetFirstChild () and Bookmark.GetLastChild ().
    
    # Open the document that was saved in the previous code sample
    doc = PDFDoc(output_path + "bookmark.pdf")
    doc.InitSecurityHandler()
    
    root = doc.GetFirstBookmark()
    PrintOutlineTree(root)
    
    doc.Close()
    print("Done.")
    
    # The following example illustrates how to create a Bookmark to a page 
    # in a remote document. A remote go-to action is similar to an ordinary 
    # go-to action, but jumps to a destination in another PDF file instead 
    # of the current file. See Section 8.5.3 'Remote Go-To Actions' in PDF 
    # Reference Manual for details.
    
    doc = PDFDoc(output_path + "bookmark.pdf")
    doc.InitSecurityHandler()
    
    # Create file specification (the file reffered to by the remote bookmark)
    file_spec = doc.CreateIndirectDict()
    file_spec.PutName("Type", "Filespec")
    file_spec.PutString("F", "bookmark.pdf")
    spec = FileSpec(file_spec)
    goto_remote = Action.CreateGotoRemote(spec, 5, True)
    
    remoteBookmark1 = Bookmark.Create(doc, "REMOTE BOOKMARK 1")
    remoteBookmark1.SetAction(goto_remote)
    doc.AddRootBookmark(remoteBookmark1)
    
    # Create another remote bookmark, but this time using the low-level SDF/Cos API.
    # Create a remote action
    remoteBookmark2 = Bookmark.Create(doc, "REMOTE BOOKMARK 2")
    doc.AddRootBookmark(remoteBookmark2)
    
    gotoR = remoteBookmark2.GetSDFObj().PutDict("A")
    gotoR.PutName("S","GoToR")  # Set action type
    gotoR.PutBool("NewWindow", True)
    
    # Set the file specification
    gotoR.Put("F", file_spec)
    
    # jump to the first page. Note that pages are indexed from 0.
    dest = gotoR.PutArray("D")  # Set the destination
    dest.PushBackNumber(9); 
    dest.PushBackName("Fit");
    
    doc.Save(output_path + "bookmark_remote.pdf", SDFDoc.e_linearized)
    doc.Close()
    PDFNet.Terminate()
    print("Done. Result saved in bookmark_remote.pdf")
    
if __name__ == '__main__':
    main()