
# Project Title

Development of code to find bank transactions within files




## Documentation

code to take in a file, identify the table containing bank transactions in it, and then return those transactions as a dataframe. Currently, csv, xlsx, xls and pdfs are supported. Note that readings pdfs is very experimental.

The tabula-py, re and pandas modules are required to be installed for this program to run.

call the mainHandler method with the path of the file and the password. If there are no passwords,do not provide the password argument. Note that passwords only work with pdf files. if you have csv or excel files with passwords, use the encryption module of Excel to remove the encryption, or alternatively,use one of the online solutions available.

for output, you can pass the results of the mainHandler method to the output_handler method. set output flag to print to print out the results, spreadsheet to get it in spreadsheet format. The filetype under spreadsheet flag depends on the number of tables identified, if there is one, it will be csv, if more than one, it will be in xlsx. if the output is False, it means no tables were identified.



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
