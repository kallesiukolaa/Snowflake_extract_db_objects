import shutil
import os
import unicodedata
import re

#Returns a list of all occurences of given char in the given string.
def __get_char_positions_from_string(char, string):
    return [pos for pos, ch in enumerate(string) if ch == char]

#Returns commented chars positions
def __commented_positions(string):
    starts = __get_char_positions_from_string('/*', string)
    ends = __get_char_positions_from_string('*/', string)
    commented = []
    for start, end in zip(starts, ends):
        commented = commented + range(start, end + 1)
    #Check if is in oneline comment
    comment_chars = ["--", "//"]
    for comment_char in comment_chars:
        comments = __get_char_positions_from_string(comment_char, string)
        for comment in comments:
            while string[comment] != '\n' and comment < len(string):
                commented.append(comment)
                comment = comment + 1
    return commented

#Return occurences except adjacent ones. This is used for handling escape cases like "my""table"""
def __get_char_positions_from_string_non_adj(char, string):
    res = __get_char_positions_from_string(char, string)
    res_to_return = res.copy()
    for i in range(1, len(res)):
        if res[i] - res[1 - 1] == 1:
            res_to_return.remove(res[i])
            res_to_return.remove(res[i - 1])
    return res_to_return

#Returns true if char is between "start" and "end" letters. For example in letter abcd*efg*hijk*lmn* efg, lmn are "between" *
def __is_between_chars(position, char_positions):
    for i in range(len(char_positions) - 1):
        if position < char_positions[i + 1] and position > char_positions[i] and i % 2 == 0:
            return True
    return False

#Returns a list of substrings of given list. List is splitted from the given positions. Position is included to first list.
def __split_string_positions(string, positions):
    remain = string
    strings = []
    for pos in positions:
        diff = len(string) - len(remain)
        strings.append(remain[:(pos + 1 - diff)])
        remain = remain[(pos + 1 - diff):]
    return strings

#Removes all occurences fro another list that are in another list
def __remove_from_list(list, sublist):
    for value in sublist:
        try:
            list.remove(value)
        except ValueError:
            1==1
    return list

#Removes quotas that are inside duoble quota and vice versa
def __remove_chars_inside(chars_1, chars_2):
    open_1 = False #Example if we have dfdsfssdfsdf'dfsffd.. its open for '
    open_2 = False
    all_values = sorted(chars_1 + chars_2)
    for value in all_values:
        if value in chars_1:
            if not open_2 and not open_1:
                open_1 = True
                continue
            if not open_2 and open_1:
                open_1 = False
                continue
            if open_2:
                chars_1.remove(value)
        if value in chars_2:
            if not open_1 and not open_2:
                open_2 = True
                continue
            if not open_1 and open_2:
                open_2 = False
                continue
            if open_1:
                chars_2.remove(value)
    return [chars_1, chars_2]

#Returns all semicolons from db create script that actually ends statements. For example procedures may contain semicolons that don't separate objects.
def __find_real_semicols(string):
    is_quotes = __get_char_positions_from_string('\'', string)
    is_dquotes = __get_char_positions_from_string('\"', string)
    is_scolons = __get_char_positions_from_string(';', string)
    commented = __commented_positions(string)
    is_quotes = __remove_from_list(is_quotes, commented)
    is_dquotes = __remove_from_list(is_dquotes, commented)
    is_scolons = __remove_from_list(is_scolons, commented)
    #We need to check which quotes and duoble quotes are part of some name etc.
    [is_quotes, is_dquotes] = __remove_chars_inside(is_quotes, is_dquotes)
    scols = []
    for pos in is_scolons:
        if not (__is_between_chars(pos, is_quotes) or __is_between_chars(pos, is_dquotes)):
            scols.append(pos)
    return scols

#Removes given string from the beginnng of  the string
def __remove_from_start(string, string_to_remove):
    index = string.upper().find(string_to_remove.upper())
    return string[(index + len(string_to_remove)):]

#Returns object type of given creation script.
def __derive_object_type(obj_str):
    obj_str = obj_str.upper().replace('\n', '')
    if obj_str.startswith("CREATE OR REPLACE "):
        obj_str = __remove_from_start(obj_str, "CREATE OR REPLACE ")
    elif obj_str.startswith("CREATE "):
        obj_str = __remove_from_start(obj_str, "CREATE ")
    index=obj_str.find(' ')
    return  obj_str[:index]

#Returns name of the object.
def __derive_object_name(obj_str):
    obj_str = obj_str.strip()
    obj_type = __derive_object_type(obj_str)
    if obj_str.upper().startswith("CREATE OR REPLACE "):
        obj_str = obj_str[len("CREATE OR REPLACE "):]
    else:
        obj_str = obj_str[len("CREATE "):]
    obj_str = __remove_from_start(obj_str, obj_type).strip()
    #Remove database from the beginning.
    quotes = __get_char_positions_from_string_non_adj('\"', obj_str)
    database_name = ""
    if len(quotes) > 0 and quotes[0] == 0:
        database_name = obj_str[:(quotes[1] + 1)]
    else:
        index=obj_str.find('.')
        database_name = obj_str[:index]
    obj_str = __remove_from_start(obj_str, database_name + ".")
    quotes = __get_char_positions_from_string_non_adj('\"', obj_str)
    schema_name = ""
    name = ""
    if len(quotes) > 0 and quotes[0] == 0:
        schema_name = obj_str[:(quotes[1] + 1)]
    else:
        index=obj_str.find('.')
        schema_name = obj_str[:index]
    obj_str = __remove_from_start(obj_str, schema_name + ".")
    quotes = __get_char_positions_from_string_non_adj('\"', obj_str)
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
    pair = []
    if schema_name == '':
        return ['', database_name]
    if name == '':
        return [schema_name, schema_name]
    return [schema_name, name]

"""Returns a list of tuples of objects. Please note that you must set use_fully_qualified_names_for_recreated_objects as true."""
def snowflake_ddl_to_list(database_ddl):
    return_list = []
    objs = __split_string_positions(database_ddl, __find_real_semicols(database_ddl))
    for obj in objs:
        entire_object = __derive_object_name(obj)
        return_list.append((__derive_object_type(obj), entire_object[0], entire_object[1], obj))
    return return_list
