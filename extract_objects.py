
#Returns a list of all occurences of given char in the given string.
def get_char_positions_from_string(char, string):
    return [pos for pos, ch in enumerate(string) if ch == char]

#Return occurences except adjacent ones. This is used for handling escape cases like "my""table"""
def get_char_positions_from_string_non_adj(char, string):
    res = get_char_positions_from_string(char, string)
    res_to_return = res
    for i in range(1, len(res)):
        if res[i] - res[1 - 1] == 1:
            res_to_return.remove(res[i])
            res_to_return.remove(res[i - 1])
    return res_to_return

#Returns true if char is between "start" and "end" letters. For example in letter abcd*efg*hijk*lmn* efg, lmn are "between" *
def is_between_chars(position, char_positions):
    for i in range(len(char_positions) - 1):
        if position < char_positions[i + 1] and position > char_positions[i] and i % 2 == 0:
            return True
    return False

#Returns a list of substrings of given list. List is splitted from the given positions. Position is included to first list.
def split_string_positions(string, positions):
    remain = string
    strings = []
    for pos in positions:
        diff = len(string) - len(remain)
        strings.append(remain[:(pos + 1 - diff)])
        remain = remain[(pos + 1 - diff):]
    return strings

#Returns all semicolons from db create script that actually ends statements. For example procedures may contain semicolons that don't separate objects.
def find_real_semicols(string):
    is_quotes = get_char_positions_from_string('\'', string)
    is_dquotes = get_char_positions_from_string('\"', string)
    is_scolons = get_char_positions_from_string(';', string)

    scols = []
    for pos in is_scolons:
        if not (is_between_chars(pos, is_quotes) or is_between_chars(pos, is_dquotes)):
            scols.append(pos)
    return scols

#Removes given string from the beginnng of  the string
def remove_from_start(string, string_to_remove):
    index = string.upper().find(string_to_remove.upper())
    return string[(index + len(string_to_remove)):] 

#Returns object type of given creation script. 
def derive_object_type(obj_str):
    obj_str = obj_str.upper().replace('\n', '')
    if obj_str.startswith("CREATE OR REPLACE "):
        obj_str = remove_from_start(obj_str, "CREATE OR REPLACE ")
    elif obj_str.startswith("CREATE "):
        obj_str = remove_from_start(obj_str, "CREATE ")
    index=obj_str.find(' ')
    return  obj_str[:index]

#Returns name of the object.
def derive_object_name(obj_str):
    obj_str = obj_str.strip()
    obj_type = derive_object_type(obj_str)
    if obj_str.upper().startswith("CREATE OR REPLACE "):
        obj_str = obj_str[len("CREATE OR REPLACE "):]
    else:
        obj_str = obj_str[len("CREATE "):]
    obj_str = remove_from_start(obj_str, obj_type).strip()
    quotes = get_char_positions_from_string_non_adj('\"', obj_str)
    schema_name = ""
    name = ""
    if len(quotes) > 0 and quotes[0] == 0:
        schema_name = obj_str[:(quotes[1] + 1)]
    else:
        index=obj_str.find('.')
        schema_name = obj_str[:index]
    obj_str = remove_from_start(obj_str, schema_name + ".")
    quotes = get_char_positions_from_string_non_adj('\"', obj_str)
    if len(quotes) > 0 and quotes[0] == 0:
        name = obj_str[:(quotes[1] + 1)]
    else:
        index_space = obj_str.find(' ')
        index_br = obj_str.find('(')
        if index_br >= 0 and index_space > index_br:
            index = index_br
        else:
            index = index_space
        name = obj_str[:index]
    return [schema_name, name]

with open('mydb.sql', 'r') as file:
    data = file.read()
folder = "C:\Temp\Objects"

print(get_char_positions_from_string(';', data))
print(find_real_semicols(data))
for str in split_string_positions(data, find_real_semicols(data)):
    print("---Definition ---")
    print(str.strip()) 
    print("---Type ---")
    print(derive_object_type(str))
    print("---Schema ---")
    print(derive_object_name(str)[0])
    print("---Name ---")
    print(derive_object_name(str)[1])