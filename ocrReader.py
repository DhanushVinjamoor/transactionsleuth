import os

import pandas as pd
import pytesseract
from fuzzywuzzy import fuzz
import cv2


# user_flag = False

class fileHandle:

    def pdfTestingHandler(self,pdf_path,mode="self"):
        # todo add a method to split pages of pdfs without poppler
        pass

    def imagesTestingHandler(self, image_path: str, mode="self"):
        if mode == "self":
            autoRecognitionHandler = findTable()
            outputvalue = autoRecognitionHandler.fullTableExtractionAlgo(image_path)
            print(outputvalue)
            if outputvalue[0]:
                return outputvalue
            else:
                import UserImageCrop as UIC

                userRecognitionHandler = UIC.userCropTable(image_path)

                if userRecognitionHandler.output_path is None or userRecognitionHandler.column_counter is None:
                    return [False]
                else:
                    testingClassHandler = testTables()
                    output = autoRecognitionHandler.columnReader("temp_directory", userRecognitionHandler.column_counter)
                    return output


        else:
            import UserImageCrop as UIC

            userRecognitionHandler = UIC.userCropTable(image_path)

            if userRecognitionHandler.output_path is None or userRecognitionHandler.column_counter is None:
                return [False]
            else:
                autoRecognitionHandler = findTable()
                testingClassHandler = testTables()
                output = autoRecognitionHandler.crop_and_process_image(userRecognitionHandler.output_path, 0, 0, 0, 0,
                                                                       testingClassHandler,"7737")
                return output


class findTable:

    def fullTableExtractionAlgo(self,path_to_image):
        import OcrToTableTool as ottt
        import TableExtractor as te
        import TableLinesRemover as tlr
        import cv2

        table_extractor = te.TableExtractor(path_to_image)
        perspective_corrected_image = table_extractor.execute()
        #cv2.imshow("perspective_corrected_image", perspective_corrected_image)

        lines_remover = tlr.TableLinesRemover(perspective_corrected_image)
        image_without_lines = lines_remover.execute()
        #cv2.imshow("image_without_lines", image_without_lines)

        ocr_tool = ottt.OcrToTableTool(image_without_lines, perspective_corrected_image)
        self_identification_protocol_output_filename=ocr_tool.execute()

        ### Loop the data lines
        with open(self_identification_protocol_output_filename, 'r') as temp_f:
            # get No of columns in each line
            col_count = [len(l.split(",")) for l in temp_f.readlines()]

        ### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
        column_names = [i for i in range(0, max(col_count))]

        with open(self_identification_protocol_output_filename,"r") as self_ocr_file:
            possible_df=pd.read_csv(self_ocr_file,header=None, delimiter=",", names=column_names)

        testing_class = testTables()

        output_of_testingclass = testing_class.identifyTableDimensions(possible_df)

        # The output is in the form of a list, with the index 0 always being a boolean value, which is set to True if
        # a match has been reached, and False if not. The index 1 is a list, with the start and ending roiw values of
        # identified dataframes

        if output_of_testingclass[0]:
            # Delete the cropped image
            for start, end in output_of_testingclass[1]:
                # todo add a function to output the dataframe and get confirmation from the user
                print(possible_df[start:end])
                self.displayOutputToUser(possible_df[start:end])

                if self.user_flag:
                    # os.remove('processed_image.jpg')
                    return [True, possible_df[start:end]]
            # if none of the identified tables in the above function satisfy user requirements, return false
            return [False]
        else:
            # Delete the cropped image
            # os.remove('processed_image.jpg')
            return [False]


    def columnReader(self, output_directory, column_counter):
        # This is the function to open each of the cropped columns identified by the user, convert it into a dataframe, and merge them into a single dataframe.



        all_columns_list=[]

        # todo make sure the column iteration logic is sound
        for current_column in range(1,column_counter):

            # The string variable needs to be within the loop so that it can be reset
            cropped_image_path = ''

            if not output_directory is None:
                cropped_image_path=cropped_image_path+output_directory+'\\'

            cropped_image_path=cropped_image_path+str(current_column)+'.jpg'

            column_image=cv2.imread(cropped_image_path)

            column_raw_string=pytesseract.image_to_string(column_image)

            #print(column_raw_string)

            column_raw_string=column_raw_string.split("\n")

            column_raw_string=pd.DataFrame(column_raw_string)

            #print(column_raw_string)

            all_columns_list.append(column_raw_string)

        self.columnAnalyser(all_columns_list)

    def columnAnalyser(self,dataframes:list):

        full_dataframe = pd.DataFrame()

        col_num=0
        # Iterate over the list of DataFrames
        for df in dataframes:
            # Check the column count and row count of the DataFrame
            num_columns = len(df.columns)
            num_rows = len(df)

            # Append DataFrame to new DataFrame if it has only one column
            if num_columns == 1:
                column_name = df.columns[0]
                full_dataframe[str(col_num)] = df[column_name]
                col_num+=1

        self.output_handler(flag="spreadsheet", dataframes=[full_dataframe])



    def findTablesInImageCV(self, image_path):
        # This is the main function within this class to hook onto. Hook onto this function if you have a image
        # that you would like to analyse for tables

        import numpy as np

        # Load the image
        image = cv2.imread(image_path)

        # The below are a set of processes to attempt to identify any tables in the image. Once one table is
        # identified, that table is displayed to the user for confirmation, and if rejected, the image is croppped
        # and processed again.

        # Convert the image to grayscale, as color information is unnecessary for our use case.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to obtain a binary image. The output is required to be unpacked, as the output
        # is the threshold utilised and the processed imaged
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Since almost all bank statements will be black text on a white background, this is inverted in order to
        # identify contours more easily
        inverted_image = cv2.bitwise_not(binary)

        dilated_image = cv2.dilate(inverted_image, None, iterations=5)

        # Find contours in the binary image in cv2, contours are basically an outline of an object, which all have
        # the same 'intensity'. Finding contours are best applied on binary images, hence the above change
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area and aspect ratio
        tables = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h

            # Adjust the area and aspect ratio thresholds according to your requirements
            if cv2.contourArea(contour) > 5000 and aspect_ratio > 1.5:
                tables.append((x, y, x + w, y + h))

        # Draw bounding rectangles around the detected tables
        result = image.copy()
        testing_class = testTables()
        for count,(x1, y1, x2, y2) in enumerate(tables):
            # print("started testing loop")
            cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
            self.user_flag = False
            output_of_processed_image = self.crop_and_process_image(image_path, x1, y1, x2, y2, testing_class,count)
            if output_of_processed_image[0]:
                # Display the result
                return output_of_processed_image
            else:
                continue
        # Display the result
        # cv2.imshow('Detected Tables', result)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return [False]

    def scan_image(self, image_path,count):
        import pytesseract
        # import pandas as pd

        print(image_path)

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(image_path)

        # print(text)

        # Split the extracted text into lines
        lines = text.split("\n")

        # Create a list of dictionaries to hold line data
        data = []

        # Iterate over the lines and create dictionary entries
        for line in lines:
            # Split each line into individual elements (e.g., using whitespace)
            elements = line.split()

            # Create a dictionary for the line
            line_data = {}
            for i, element in enumerate(elements):
                line_data[f"Column_{i + 1}"] = element

            # Append the line dictionary to the data list
            data.append(line_data)

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)

        self.output_handler(flag="spreadsheet",outputpath=("ocrtest"+str(count)),dataframes=[df])

        return df

    def crop_and_process_image(self, file_path, x1, y1, x2, y2, testing_class,count):
        # this is an intermediary function to crop an image to the defined thresholds, convert it into a dataframe
        # with scan_image method of this class, and then print out the results

        # Read the original image
        original_image = cv2.imread(file_path)

        if not x1 == y1 == x2 == y2 == 0:
            # Create a copy of the original image
            copied_image = original_image.copy()

            # Define the cropping coordinates
            # x1, y1 = x1, y1  # Top-left corner of the cropped region
            # x2, y2 = x1 + 100, y1 + 100  # Bottom-right corner of the cropped region

            # Crop the copied image using the defined coordinates
            cropped_image = copied_image[y1:y2, x1:x2]
            possible_df = self.scan_image(cropped_image,count)
        else:
            possible_df=self.scan_image(original_image,count)


        # The tests are very similar to the tests performed on pdfs and csvs, please refer the same for detailed
        # documentation

        output_of_testingclass = testing_class.identifyTableDimensions(possible_df)

        # The output is in the form of a list, with the index 0 always being a boolean value, which is set to True if
        # a match has been reached, and False if not. The index 1 is a list, with the start and ending roiw values of
        # identified dataframes

        if output_of_testingclass[0]:
            # Delete the cropped image
            for start, end in output_of_testingclass[1]:
                # todo add a function to output the dataframne and get confirmation from the user
                print(possible_df[start:end])
                self.displayOutputToUser(possible_df[start:end])

                if self.user_flag:
                    # os.remove('processed_image.jpg')
                    return [True, possible_df[start:end]]
            # if none of the identified tables in the above function satisfy user requirements, return false
            return [False]
        else:
            # Delete the cropped image
            # os.remove('processed_image.jpg')
            return [False]

    def displayOutputToUser(self, df):
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()

        # user_flag=False

        # Function to handle button click
        def button_click_confirm():
            messagebox.showinfo("Confirmation", "User is OK with the dataframe!")
            self.user_flag = True
            root.destroy()

        def button_click_reject():
            messagebox.showinfo("Rejected", "User is not OK with the dataframe!")
            self.user_flag = True
            root.destroy()

        # Display the dataframe
        text_widget = tk.Text(root, height=10, width=30)
        text_widget.insert(tk.END, df)
        text_widget.pack()

        # Create a button for confirming the dataframe
        button_confirm = tk.Button(root, text="Confirm", command=button_click_confirm)
        button_confirm.pack()

        # Create a button for rejecting the dataframe
        button_reject = tk.Button(root, text="Reject", command=button_click_reject)
        button_reject.pack()

        # Start the Tkinter main loop
        root.mainloop()

        # return user_flag

    def output_handler(self,flag:str,dataframes:list,outputpath="final_output"):
        if flag.lower()=="print":
            for dataframe in dataframes:
                print(dataframe)
        elif flag.lower()=="spreadsheet":
            if isinstance(dataframes, bool):
                filename = outputpath + ".csv"
                with open(filename, 'w') as file:
                    # Use 'to_csv' to write the DataFrame to the file
                    file.write(str(dataframes))
            elif len(dataframes)>1:
                filename = outputpath + ".xlsx"
                with pd.ExcelWriter(filename) as writer:
                    # Iterate over each DataFrame in the list and write it to a separate sheet
                    for i, df in enumerate(dataframes):
                        df.to_excel(writer, sheet_name=f'Sheet{i + 1}', index=False)
            elif len(dataframes)==1:
                filename = outputpath + ".csv"
                with open(filename, 'w') as file:
                    # Use 'to_csv' to write the DataFrame to the file
                    dataframes[0].to_csv(file, index=False)
        elif flag.lower()=="return":
            return dataframes



class testTables:

    def identifyTableDimensions(self, df, fuzz_algo=90, pass_value=0.60):

        column_names = df.columns

        # Identify tables based on some criteria
        tables = []
        table_start = None
        table_end = None

        table_found_flag = False

        from definitions_library import columnsHolder

        classHandler = columnsHolder()

        for index, row in df.iterrows():
            # print("Starting row: "+str(index))
            if table_start is not None:

                # end_flag=False

                num_flag = False

                for names in column_names:
                    if isinstance(row[names], (int, float)):
                        num_flag = True
                        break
                    elif self.is_number(row[names]):
                        num_flag = True
                        break

                if not num_flag:
                    table_end = index - 1
                    tables.append((table_start, table_end))
                    table_start = None
                    table_end = None
                elif index == (len(df) - 1) and table_start is not None:
                    table_end = index
                    tables.append((table_start, table_end))
                    table_start = None
                    table_end = None

            elif not row.isnull().all() and table_start is None:
                if self.identify_header(row, column_names, classHandler, fuzz_algo, pass_value):
                    table_start = index
                    table_found_flag = True

        return (table_found_flag, tables)

    def identify_header(self, row, column_names, classHandler, fuzz_algo_threshold=90, pass_value=0.75):

        # the identification algorithm used here is similar to the one used for .xlsx files, please refer there for
        # detailed documentation

        passed_cells_counter = 0

        tested_cells_counter = 0

        empty_cells_counter = 0

        possible_column_names = classHandler.possible_column_names

        popped_indices = []

        # print("row length is: " + str(len(column_names)))

        for iteration, names in enumerate(column_names):

            if (pd.isna(row[names]) or pd.isnull(row[names])):
                empty_cells_counter += 1
            else:

                tested_cells_counter += 1

                # a boolean flag is used here in order to break the loop in case the value passes the tests

                value_passed = False

                current_value = str(row[names]).strip()

                # a while statement is utilised here instead of an if statement, as if the value passes
                # the test, the outer loop value(the array with the array) will be popped. To ensure that
                # an index does not get skipped, the index is incremented only if no values are popped

                index_of_main_possible_column_names_array = 0

                while index_of_main_possible_column_names_array < len(possible_column_names):

                    outer_loop_values = possible_column_names[index_of_main_possible_column_names_array]

                    if current_value in outer_loop_values:
                        passed_cells_counter += 1
                        # print("Passed value"+current_value)
                        popped_indices.append(index_of_main_possible_column_names_array)
                        possible_column_names.pop(index_of_main_possible_column_names_array)
                        break

                    for testvalues in outer_loop_values:
                        # the immediate outerloop is for iterating through column values for each row,
                        # and each value is tested against the possible column values array

                        if fuzz.partial_ratio(current_value.lower(), testvalues) >= fuzz_algo_threshold:
                            # print("Passed value" + current_value)
                            passed_cells_counter += 1
                            value_passed = True
                            break

                    # if the value_passed flag is set to True, it means the tests have passed, and so the
                    # value is popped, added to the indices popped list

                    if value_passed:

                        popped_indices.append(index_of_main_possible_column_names_array)

                        possible_column_names.pop(index_of_main_possible_column_names_array)
                        break
                    else:
                        index_of_main_possible_column_names_array += 1
                # todo add a check to make sure this test occurs only at end of series
                if ((
                            passed_cells_counter / tested_cells_counter) >= pass_value) and tested_cells_counter >= 4:

                    heading_pattern_flag = True

                    expected_headings_flag = True

                    if empty_cells_counter > 0:
                        import re
                        pattern = r'^\W*$'
                        heading_list = row.replace(to_replace=pattern, value="empty", regex=True)
                        heading_list = row.fillna("empty")
                        heading_list = row.values.tolist()
                        heading_pattern_flag = self.identify_empty_space_pattern(heading_list)

                    if len(popped_indices) > 0:
                        if (0 in popped_indices) or (2 in popped_indices) or (3 in popped_indices):
                            expected_headings_flag = True
                        else:
                            expected_headings_flag = False

                    if heading_pattern_flag and expected_headings_flag:
                        # print(" Cells tested: " + str(tested_cells_counter) + " Cells passed: " + str(
                        #   passed_cells_counter) + " Cells empty: " + str(empty_cells_counter))
                        return True
                    else:
                        # print(" Cells tested: " + str(tested_cells_counter) + " Cells passed: " + str(
                        #    passed_cells_counter) + " Cells empty: " + str(empty_cells_counter))
                        return False
        return False

    def check_compatibility(self, first_row, second_row):
        # This is a function which will take two rows, iterate through the values of both, and if the datatypes of
        # both values match for at least 75% of tested columns, will return True.

        # removing any set column names, as the rows will be iterated together in the same loop

        first_row.columns = None
        second_row.columns = None

        # creating a loop, where the datatypes of the values will be tested against each other. empty cells in both
        # are not considered for testing, however if only one row has an empty cell that will be considered as tested

        empty_cells_count = 0
        tested_cells_count = 0
        passed_cells_count = 0

        if len(first_row) == len(second_row):
            # check to ensure that both series have the same length

            for index in range(len(first_row)):

                # the count of tested cells is updated before any checks

                tested_cells_count += 1
                if type(first_row[index]) == type(second_row[index]):
                    passed_cells_count += 1

            if tested_cells_count >= 4 and (passed_cells_count / tested_cells_count) >= 0.5:
                return True
            else:
                return False
        else:
            return False

    def identify_empty_space_pattern(self, full_row):
        previous_cell_is_empty = False
        current_cell_is_empty = False
        strikes = 0

        # this function works on a 3 strike policy, if both the cells are the same for 3 times, the function returns
        # false

        for index, value in enumerate(full_row):
            if index == 0:
                if value == "empty":
                    previous_cell_is_empty = True
                    continue
            else:
                if value == "empty":
                    current_cell_is_empty = True
                else:
                    current_cell_is_empty = False
                if current_cell_is_empty == previous_cell_is_empty:
                    strikes += 1
                if strikes >= 3:
                    return False

        if strikes >= 3:
            return False
        return True

    def is_number(self, string_test):
        try:
            float(string_test)  # or int(string) for integer check
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    testerHandler = fileHandle()
    outputvalue = testerHandler.imagesTestingHandler("hdfc.jpg")
    print(outputvalue)

# todo ensure temp directory is removed at end of execution