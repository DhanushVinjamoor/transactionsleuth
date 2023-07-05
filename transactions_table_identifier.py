import os
import sys

# Get the current directory path
current_path = os.getcwd()

# Add the current directory to the system path
sys.path.append(current_path)


# print(sys.path)

class handle_by_filetype:

    def __init__(self, filepath):

        import os

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        extension = os.path.splitext(filepath)[-1].lower()

        if extension == ".csv":
            identification_threshold = 0.75
            fuzzy_pass_threshold = 80
            while identification_threshold >= 0.50:
                output = self.csv_handler(filepath,identification_threshold,fuzzy_pass_threshold)
                if output:
                    break
                identification_threshold -= 0.825
                fuzzy_pass_threshold -= 5
        elif extension == ".xlsx" or extension == ".xls":
            identification_threshold = 0.75
            fuzzy_pass_threshold = 80
            while identification_threshold >= 0.50:
                output = self.excel_handler(filepath,identification_threshold,fuzzy_pass_threshold)
                if output:
                    break
                identification_threshold -= 0.825
                fuzzy_pass_threshold -= 5
        elif extension == ".pdf":
            pass
        else:
            raise TypeError

    def excel_handler(self, excel_file_path, overall_identification_threshold=0.75, fuzz_algo_threshold=80):
        import pandas as pd

        # Specify the path to your Excel file

        # Read the Excel file and get the sheet names
        xls = pd.ExcelFile(excel_file_path)
        sheet_names = xls.sheet_names

        pass_value = overall_identification_threshold

        # The import statements are handled here as a compromise to ensure that they are not called before they are
        # required, and to ensure that import statements do not occur within the loop.

        from fuzzywuzzy import fuzz
        from fuzzywuzzy import process

        # Iterate over each sheet and print the table data
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

            # get the list of columns that will be used in inner loop below
            column_names = df.columns

            # Identify tables based on some criteria
            tables = []
            table_start = None
            table_end = None

            for index, row in df.iterrows():
                if row.isnull().all() and table_start is not None:
                    # Found the end of the table
                    table_end = index
                    tables.append((table_start, table_end))
                    table_start = None
                    table_end = None
                elif not row.isnull().all() and table_start is None:
                    # code to check the column values against a list of common titles

                    passed_cells_counter = 0

                    tested_cells_counter = 0

                    empty_cells_counter = 0

                    # setting up variables that are used as part of the table identification algorithm the values are
                    # split into different lists based on nature of field to be searched for. This is done as once
                    # one field array has a match to a row value, that array will be popped to ensure that same array
                    # will not trigger multiple times. The variable is set here, as for each row that is iterated
                    # through the array will need to be refreshed (due to the popping of values in previous instances)

                    # todo consider implementing a way to populate the below listings using pyDictionary

                    possible_column_names = [[
                        'description', 'transaction description', 'details', 'transaction details', 'description',
                        'memo', 'transaction details',
                        'remarks', "narration",
                        'explanation', 'comment', 'note', 'purpose', 'message'], ['amount',
                                                                                  'transaction amount', 'currency'],
                        ['account', 'account number', 'account name', 'counterparty'], ['reference',
                                                                                        'transaction reference', 'UTR',
                                                                                        'chq.', 'cheque', 'ref no.','ref chq no.'],
                        ['category', 'type'],
                        ['balance', 'opening balance'], [
                            'closing balance', "balance",
                            'running balance', 'available balance'], ["withdrawal", 'debit'],
                        ['deposit',
                         'credit'],
                        ["date", "day", "time", 'transaction date', 'posting date', 'account activity date',
                         'statement date', 'entry date', 'record date', 'event date',
                         'transaction timestamp', 'financial activity date', 'recorded date','dt.','dt','txn dt']
                    ]

                    # index - 0:Narration,1:Amount,3:counterpart,4:reference,5:Category,6:Op.Bal,7.cl.bal,8.dr,8.cr,
                    # 9.date

                    # This is an array to hold any indices that have been popped, so that while any columns which
                    # have been identified are not repeated while iterating through the columns. This index is
                    # refreshed every row loop.

                    popped_indices = []

                    for names in column_names:
                        # todo consider adding a split value for the value being considered

                        # in this nested loop, the value of the cell in the row in the  iter rows in the outer loop
                        # is selected based on the column names list created, and that is tested for similarity
                        # to the possible names array.

                        # added a check for if the value is null, both to prevent false positives and to save
                        # execution time.

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
                                    popped_indices.append(index_of_main_possible_column_names_array)
                                    possible_column_names.pop(index_of_main_possible_column_names_array)
                                    break

                                for testvalues in outer_loop_values:
                                    # the immediate outerloop is for iterating through column values for each row,
                                    # and each value is tested against the possible column values array

                                    if fuzz.partial_ratio(current_value.lower(), testvalues) >= fuzz_algo_threshold:
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
                                    table_start = index
                                    break

            # Print the sheet name
            print("Sheet Name:", sheet_name)

            if not len(tables) == 0:
                # Print each table
                for table in tables:
                    start, end = table
                    table_data = df[start:end]
                    print(table_data)
                    print('\n')  # Add a newline for better readability
                return True
            else:
                return False

    def csv_handler(self, csv_file_path, overall_identification_threshold=0.75, fuzz_algo_threshold=80):
        import pandas as pd

        # Specify the path to your Excel file

        # Read the Excel file and get the sheet names

        pass_value = overall_identification_threshold

        # The import statements are handled here as a compromise to ensure that they are not called before they are
        # required, and to ensure that import statements do not occur within the loop.

        from fuzzywuzzy import fuzz
        from fuzzywuzzy import process

        # Iterate over each sheet and print the table data

        df = pd.read_csv(csv_file_path)

        # get the list of columns that will be used in inner loop below
        column_names = df.columns

        # Identify tables based on some criteria
        tables = []
        table_start = None
        table_end = None

        for index, row in df.iterrows():
            if row.isnull().all() and table_start is not None:
                # Found the end of the table
                table_end = index
                tables.append((table_start, table_end))
                table_start = None
                table_end = None
            elif not row.isnull().all() and table_start is None:
                # code to check the column values against a list of common titles

                passed_cells_counter = 0

                tested_cells_counter = 0

                empty_cells_counter = 0

                # setting up variables that are used as part of the table identification algorithm the values are
                # split into different lists based on nature of field to be searched for. This is done as once
                # one field array has a match to a row value, that array will be popped to ensure that same array
                # will not trigger multiple times. The variable is set here, as for each row that is iterated
                # through the array will need to be refreshed (due to the popping of values in previous instances)

                # todo consider implementing a way to populate the below listings using pyDictionary

                possible_column_names = [[
                    'description', 'transaction description', 'details', 'transaction details', 'description',
                    'memo', 'transaction details',
                    'remarks', "narration",
                    'explanation', 'comment', 'note', 'purpose', 'message'], ['amount',
                                                                              'transaction amount', 'currency'],
                    ['account', 'account number', 'account name', 'counterparty'], ['reference',
                                                                                    'transaction reference', 'UTR',
                                                                                    'chq.', 'cheque', 'ref no.'],
                    ['category', 'type'],
                    ['balance', 'opening balance'], [
                        'closing balance', "balance",
                        'running balance', 'available balance'], ["withdrawal", 'debit'],
                    ['deposit',
                     'credit'],
                    ["date", "day", "time", 'transaction date', 'posting date', 'account activity date',
                     'statement date', 'entry date', 'record date', 'event date',
                     'transaction timestamp', 'financial activity date', 'recorded date']
                ]

                # index - 0:Narration,1:Amount,3:counterpart,4:reference,5:Category,6:Op.Bal,7.cl.bal,8.dr,8.cr,
                # 9.date

                # This is an array to hold any indices that have been popped, so that while any columns which
                # have been identified are not repeated while iterating through the columns. This index is
                # refreshed every row loop.

                popped_indices = []

                for names in column_names:
                    # todo consider adding a split value for the value being considered

                    # in this nested loop, the value of the cell in the row in the  iter rows in the outer loop
                    # is selected based on the column names list created, and that is tested for similarity
                    # to the possible names array.

                    # added a check for if the value is null, both to prevent false positives and to save
                    # execution time.

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
                                popped_indices.append(index_of_main_possible_column_names_array)
                                possible_column_names.pop(index_of_main_possible_column_names_array)
                                break

                            for testvalues in outer_loop_values:
                                # the immediate outerloop is for iterating through column values for each row,
                                # and each value is tested against the possible column values array

                                if fuzz.partial_ratio(current_value.lower(), testvalues) >= fuzz_algo_threshold:
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
                                table_start = index
                                break

        # Print the sheet name

        if not len(tables) == 0:
            # Print each table
            for table in tables:
                start, end = table
                table_data = df[start:end]
                print(table_data)
                print('\n')  # Add a newline for better readability
            return True
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


test_path = "HDFC_personal.xls"

"""
"""

test_handler = handle_by_filetype(test_path)
