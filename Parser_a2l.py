import os
import re


class FileA2L:
    def __init__(self, path):
        self.path = path
        self.current_position = 0
        self.obligatory_lines_number = 5

        if not os.path.exists(self.path):
            print("File does not exist")

    def write(self, content):
        with open(self.path, 'w') as f:
            return f.write(content)

    def read(self):
        with open(self.path, 'r') as f:
            return f.read()

    def __search_string_in_file(self, string_to_search):
        """search for the given string in file and return list of variables,
        which belong to the provided value (string)"""
        list_of_results = []
        string_measurement_begin = "/begin MEASUREMENT"
        string_measurement_end = "/end MEASUREMENT"
        # Open the file in read only mode
        with open(self.path, 'r') as read_obj:
            # Read the file line by line till the EOF
            while True:
                line = read_obj.readline()
                if len(line) == 0:
                    break
                # If the beginning of MEASUREMENT was found read the next
                # line and compare it to the input string
                if string_measurement_begin in line:
                    line = read_obj.readline()
                    if string_to_search in line:
                        # Read and save to list till the string of the end MEASUREMENT appears
                        while True:
                            list_of_results.append(line.strip())
                            line = read_obj.readline()
                            if string_measurement_end in line:
                                break
        # Check if all obligatory lines present
        try:
            if len(list_of_results) < self.obligatory_lines_number:
                raise Exception("Minimal data structure of the variable {} was not provided".format(string_to_search))
        except Exception as err:
            print("Exception: " + err.message)
        return list_of_results

    def dictionary_measurement_create(self, string_to_search):
        """fill dictionary with data from file according to specified measure variables"""
        cursor = 0
        data_type = ["UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG",
                     "SLONG", "A_UINT64", "A_INT64"]
        secondary_keywords = ["IF_DATA", "BIT_MASK", "FUNCTION_LIST"]

        # Create common string of all elements of list
        lines_list = self.__search_string_in_file(string_to_search)
        data_string = ""
        for i in lines_list:
            data_string = data_string + " " + i

        # Check if the first string has more than 1 element
        data_string_name = data_string.partition('\"')[0].strip()
        if data_string_name != "":
            variable_name = data_string_name

        data_string_values = data_string.partition('\"')[2].partition('\"')[2].strip()
        final_values_string = data_string_values.split(" ")

        # Extract Long identifier
        long_identifier = re.findall('"([^"]*)"', data_string)

        possible_key = data_type + secondary_keywords
        key = []
        # Create and fill 2 first elements of dictionary
        dictionary_measurement = dict()
        dictionary_measurement["Variable name"] = variable_name.strip()
        dictionary_measurement["Long identifier"] = long_identifier[0]
        # Parse the string till the last word
        while cursor < len(final_values_string):
            try:
                if final_values_string[cursor] in possible_key:
                    if final_values_string[cursor] in data_type:
                        # Write obligatory elements into dictionary
                        dictionary_measurement["Data type"] = final_values_string[cursor]
                        dictionary_measurement["Type"] = final_values_string[cursor + 1]
                        dictionary_measurement["Value_1"] = (
                            int(final_values_string[cursor + 2]), int(final_values_string[cursor + 3]))
                        dictionary_measurement["Value_2"] = (
                            float(final_values_string[cursor + 4]), float(final_values_string[cursor + 5]))

                        cursor += 6
                        # Catch additional elements that start with a secondary keyword
                    elif final_values_string[cursor] in secondary_keywords:
                        key = final_values_string[cursor]
                        dictionary_measurement[key] = []
                        cursor += 1
                # Write additional elements into dictionary
                elif key:
                    # Parse HEX values
                    if "0x" in final_values_string[cursor]:
                        hex_value = hex(int(final_values_string[cursor], 16))
                        dictionary_measurement[key] = dictionary_measurement[key] + [hex_value]
                    else:
                        dictionary_measurement[key] = dictionary_measurement[key] + [final_values_string[cursor]]
                    cursor += 1
                else:
                    raise IndexError

            except IndexError:
                break
                print("Exception: Not enough elements were provided")
        return dictionary_measurement


def parser(measure_variable):
    path = "Demo03.a2l"
    file1 = FileA2L(path)
    return file1.dictionary_measurement_create(measure_variable)


# Get measurements of the specified value
print(parser("B_YELLOW"))
