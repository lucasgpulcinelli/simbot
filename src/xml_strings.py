#!/usr/bin/env python3
from xml.etree import ElementTree

import consts

#gets all strings and commands with descriptions
def xml_get_all(file):
    #parse the document
    doc = ElementTree.parse(file)
    root = doc.getroot()

    #get all simple strings
    strings_dict = {}
    for elem in root.iterfind("string"):
        key = elem.attrib["name"]
        strings_dict[key] = read_xml_string(elem)

    #get commands, arguments and descriptions
    commands_elem = None
    for elem in root.iterfind("array"):
        if elem.attrib["name"] == consts.commands_xml:
            commands_elem = elem
            break
    
    if commands_elem is None:
        raise IndexError("commands xml not found")
    
    commands_dict = read_xml_array(commands_elem)

    return strings_dict, commands_dict


#reads a string from the xml element
#the string can be either: a simple text node in a single line,
#in that case it does not include an ending newline,
#or many <l> tags, each with a line
def read_xml_string(elem):
    ret = ""

    for line in elem.iterfind("l"):
        if line.text is not None:
            ret += line.text + '\n'
        else:
            ret += '\n'
    
    if ret == "":
        ret = elem.text

    return ret

#reads an xml array, containg either strings or other arrays,
#returns a dictionary with the keys being the name attribute and 
#the values being strings or other dictionaries
def read_xml_array(elem):
    ret = {}

    for e in elem.iter():
        if e is elem:
            continue
        
        for e in elem.iterfind("string"):
            ret[e.attrib["name"]] = read_xml_string(e)

        for e in elem.iterfind("array"):
            ret[e.attrib["name"]] = read_xml_array(e)

    return ret

#creates the help string from all commands, arguments and descriptions
def gen_help(cmds_dict):
    ret = strs_dict[consts.usage_xml] + '\n'

    for cmd_all in cmds_dict.values():
        ret += f"`{strs_dict[consts.bot_cmd_xml]} {cmd_all[consts.help_fmt_xml[0]]}`:\n"
        ret += cmd_all[consts.help_fmt_xml[2]] + '\n'
        
        try:
            args = cmd_all[consts.help_fmt_xml[1]]
        except KeyError:
            continue
            
        ret += f"**{strs_dict[consts.usage_args_xml]}**:\n"

        for arg in args.values():
            ret += f"`{arg[consts.help_args_fmt_xml[0]]}`:\n"
            ret += arg[consts.help_args_fmt_xml[1]] + '\n'

    return ret


strs_dict, cmds_dict = xml_get_all(consts.strings_file)

help_str = gen_help(cmds_dict)


if __name__ == "__main__":
    print(strs_dict)
    print("\n\n\n")
    print(cmds_dict)
    print("\n\n\n")

    for value in strs_dict.values():
        print(value)

    print()
    
    for value in cmds_dict.values():
        print(value[consts.help_fmt_xml[0]])
        try:
            for arg in value[consts.help_fmt_xml[1]].values():
                print(arg[consts.help_args_fmt_xml[0]])
                print(arg[consts.help_args_fmt_xml[1]])
        except KeyError:
            pass
        print(value[consts.help_fmt_xml[2]])

