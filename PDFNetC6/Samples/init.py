#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2021 by PDFTron Systems Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------
import sys
import platform
try:
    from apryse_sdk import *
except ImportError as e:
    py3 = "python"if platform.system().lower() == "windows" else "python3"
    print('')
    print(e)
    print("--------------------------------------------------------------------------------------------------------------------")
    print("  You need to install apryse-sdk via pip from Apryse's S3 private repository before you could run the samples [$%s -m pip install apryse-sdk --extra-index-url=https://pypi.apryse.com]." % py3)
    print("  Please refer to  'https://docs.apryse.com/documentation/python/get-started/' for more information!")
    print("--------------------------------------------------------------------------------------------------------------------")
    exit(1)
except Exception as e:
    print(e)
    exit(1)
exit(0)
