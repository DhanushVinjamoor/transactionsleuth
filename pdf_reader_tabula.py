import pandas as pd
from fuzzywuzzy import fuzz

class pdf_reader:

    def get_tables(self,path,password=None):
        import tabula

        full_data=tabula.read_pdf(path,pages="all",multiple_tables=True, password=password)

        return full_data

    def clean_results(self,full_data):

        for identified_elements in full_data:

            try:
                updated_dataframe=pd.DataFrame(identified_elements)

                tested_elements=self.identifyTableDimensions(updated_dataframe)

                print("first attempt result is:"+str(tested_elements[0]))

                if tested_elements[0]:
                    for tables in tested_elements[1]:
                        print(tables)
                else:

                    identification_threshold = 0.67
                    fuzzy_pass_threshold = 80
                    while identification_threshold >= 0.50:
                        print("First attempt failed, trying again")
                        output = self.identifyTableDimensions(updated_dataframe,fuzzy_pass_threshold,identification_threshold)
                        print(output[0])
                        if output[0]:
                            print("Table identified!")
                            for tables in output[1]:
                                print(tables)
                                break
                        identification_threshold -= 0.525
                        fuzzy_pass_threshold -= 5
            except ValueError:
                print("Unable to convert to dataframe")

    def identifyTableDimensions(self, df,fuzz_algo=90,pass_value=0.75):

        column_names = df.columns

        # Identify tables based on some criteria
        tables = []
        table_start = None
        table_end = None

        table_found_flag=False

        for index, row in df.iterrows():
            print("Starting row: "+str(index))
            if table_start is not None:
                pass
                # todo is null is not the way to go, as that is usually cleaned up by the library. consider using the
                #  same same for headings to identify debris? consider adding a check to see if there are no numbers
                #  in a specific row to identify the last row

                #end_flag=False

                num_flag=False

                for names in column_names:
                    if isinstance(row[names], (int, float)):
                        num_flag=True
                        break
                    elif self.is_number(row[names]):
                        num_flag = True
                        break

                if num_flag:
                    table_end = index
                    tables.append((table_start, table_end))
                    table_start = None
                    table_end = None

            elif not row.isnull().all() and table_start is None:
                if self.identify_header(row,column_names,fuzz_algo,pass_value):
                    table_start=index
                    table_found_flag=True

        return (table_found_flag,tables)



    def identify_header(self,row,column_names,fuzz_algo_threshold=90,pass_value=0.75):

        # the identification algorithm used here is similar to the one used for .xlsx files, please refer there for
        # detailed documentation

        passed_cells_counter = 0

        tested_cells_counter = 0

        empty_cells_counter = 0

        possible_column_names = [[
            'description', 'transaction description', 'details', 'transaction details', 'description',
            'memo', 'transaction details',
            'remarks', "narration",
            'explanation', 'comment', 'note', 'purpose', 'message'], ['amount',
                                                                      'transaction amount', 'currency'],
            ['account', 'account number', 'account name', 'counterparty'], ['reference',
                                                                            'transaction reference', 'UTR',
                                                                            'chq.', 'cheque', 'ref no.', 'ref chq no.'],
            ['category', 'type'],
            ['balance', 'opening balance'], [
                'closing balance', "balance",
                'running balance', 'available balance'], ["withdrawal", 'debit'],
            ['deposit',
             'credit'],
            ["date", "day", "time", 'transaction date', 'posting date', 'account activity date',
             'statement date', 'entry date', 'record date', 'event date',
             'transaction timestamp', 'financial activity date', 'recorded date', 'dt.', 'dt', 'txn dt']
        ]

        popped_indices = []

        for names in column_names:
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
                        print("Passed value"+current_value)
                        popped_indices.append(index_of_main_possible_column_names_array)
                        possible_column_names.pop(index_of_main_possible_column_names_array)
                        break

                    for testvalues in outer_loop_values:
                        # the immediate outerloop is for iterating through column values for each row,
                        # and each value is tested against the possible column values array

                        if fuzz.partial_ratio(current_value.lower(), testvalues) >= fuzz_algo_threshold:
                            print("Passed value" + current_value)
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
                        print(" Cells tested: " + str(tested_cells_counter) + " Cells passed: " + str(passed_cells_counter))
                        return True
                    else:
                        print(" Cells tested: " + str(tested_cells_counter) + " Cells passed: " + str(passed_cells_counter))
                        return False
                else:
                    print(" Cells tested: " + str(tested_cells_counter) + " Cells passed: " + str(passed_cells_counter))
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

    def is_number(self,string_test):
        try:
            float(string_test)  # or int(string) for integer check
            return True
        except ValueError:
            return False


if __name__=="__main__":
    classhandle=pdf_reader()

    tables_list=classhandle.get_tables('canara.pdf')

    print(tables_list)

    classhandle.clean_results(tables_list)