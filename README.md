
# Project Title

Development of code to find bank transactions within files




## Documentation

Code to take in a file, identify the table containing bank transactions in it, and then return those transactions as a dataframe. Currently, csv, xlsx, xls, pdfs and images(jpg,png) are supported. Warning! - Note that reading images is very experimental, and will not provide the best results. This is because it is built on top of tesseract ocr, which while excellent, is pretty old. Replace references to tesseract with a newer ocr model to provide better results.

The tabula-py, re, pandas, numpy, cv, and pytesseract modules are required to be installed for this program to run.Tesseract ocr from Google also needs to be installed. I have used the default installation path of tesseract ocr in my code, modify the code to account for any changes in the installation paths.

The ocr programs uses code developed by livefiredev as a base.

The transactions_table_identifier.py is the main file, which contains the class to be called to utilise the program.

Call the mainHandler method with the path of the file and the password. If there are no passwords,do not provide the password argument. Note that passwords only work with pdf files. if you have csv or excel files with passwords, use the encryption module of Excel to remove the encryption, or alternatively,use one of the online solutions available.

For output, you can pass the results of the mainHandler method to the output_handler method. set output flag to print to print out the results, spreadsheet to get it in spreadsheet format. The filetype under spreadsheet flag depends on the number of tables identified, if there is one, it will be csv, if more than one, it will be in xlsx. if the output is False, it means no tables were identified.

## Known bugs

1. While cropping columns, sometimes pressing 'c' is required to be done twice before the crop takes effect.
2. Saving the base image anywhere else apart from the root of the executing files causes errors.
3. Images with thinner borders and thin letters may cause errors in automatic detection of tables, cince dilating and eroding the image 5 times causes contours to loose sharpness.


## sample usage

test_path = "your_file_name.pdf"

test_handler = handle_by_filetype()

result=test_handler.mainHandler(test_path)

test_handler.output_handler(flag="spreadsheet",dataframes=result)







## License

=============================================== 
          COMMERCIAL REPOSITORY                     
================================================ 

repository name: transactionsleuth
repository version: 1.0 
repository link: https://github.com/DhanushVinjamoor/transactionsleuth.git
author: Dhanush Vinjamoor
author contact: dhanushvinjamoor@gmail.com 
description: code to find bank transactions within files 
license category: commercial 
license: trade secret 
organization name: Arvi Solutions. 
location: Chennai, Tamil Nadu 
release date: 06-07-2023 

This code (commercial) is hereby released under a trade secret license. 

For more information, check out the license terms below. 

================================================ 
                LICENSE TERMS                      
================================================ 

Copyright (C) Arvi Solutions. - All Rights Reserved 
* Unauthorized copying of this file, via any medium is strictly prohibited 
* Proprietary and confidential 
* Written by Dhanush Vinjamoor <dhanushvinjamoor@gmail.com>, 06-07-2023

================================================ 
                SERVICE STATEMENT                    
================================================ 

If you are using the code written for a larger project, we are 
happy to consult with you and help you with deployment.

We have helped a wide variety of enterprises - small businesses, 
researchers, enterprises, and/or independent developers.  
