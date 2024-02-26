import sys
from datetime import datetime
import re

module_name = ""
ports = []

def createVHDLtemplate(filename):
    global module_name
    global ports
    # port["name"] = name
    # port["dir"] = direction
    # port["type"] = type
    # port["width"] = width

    max_name_length = 0
    for port in ports:
        max_name_length = max( max_name_length, len(port["name"]))

    with open(filename, "w") as my_file:
        my_file.write("-"*80+"\n")
        my_file.write("-- automatic generated file\n")
        now = datetime.now() # current date and time
        date_time = now.strftime("%d.%m.%Y %H:%M:%S")
        my_file.write("-- generated on " + str(date_time) + "\n")
        my_file.write("-"*80+"\n\n\n")

        my_file.write("COMPONENT " + module_name + " IS\n")
        my_file.write("\tPORT (\n")

        for port in ports:
            my_file.write(("\t\t{:%d} : "%(max_name_length+1)).format(port["name"]))
            if "input" in port["dir"]:
                my_file.write( "{:6}".format("IN") )
            elif "output" in port["dir"]:
                my_file.write( "{:6}".format("OUT") )
            elif "inout" in port["dir"]:
                my_file.write( "{:6}".format("INOUT") )
            else:
                print(port["dir"])

            if  not port["width"]:
                my_file.write(" STD_LOGIC")
            else:
                width = port["width"].replace("[","(")
                width = width.replace("]",")")
                width = width.replace(":"," downto ")
                my_file.write(" STD_LOGIC_VECTOR " + width)

            if port["name"] == ports[-1]["name"]:   # last port does not get a ;
                my_file.write("\n")
            else:
                my_file.write(";\n")

        my_file.write("\t);\n")
        my_file.write("END COMPONENT; -- " + module_name + "\n")

        my_file.write("\n\n\n")

        my_file.write("-"*80+"\n")
        my_file.write("-- SIGNAL templates \n");
        my_file.write("-"*80+"\n")

        for port in ports:
            my_file.write( ("SIGNAL {:%d} : "%(max_name_length+1)).format(port["name"]))
            if  not port["width"]:
                my_file.write("{:29}".format("STD_LOGIC"));
                my_file.write(" := '0'");
            else:
                width = port["width"].replace("[","(")
                width = width.replace("]",")")
                width = width.replace(":"," downto ")
                my_file.write("{:16}".format("STD_LOGIC_VECTOR") + width)
                my_file.write(" := (others => '0')");

            my_file.write(";\n")

        my_file.write("\n\n\n")
        my_file.write("-"*80+"\n")
        my_file.write("-- Instantiation template \n");
        my_file.write("-"*80+"\n")

        my_file.write(module_name + "_0 : " + module_name + "\n")
        my_file.write("\tPORT MAP (\n")

        for port in ports:
            my_file.write(("\t\t{:%d}"%(max_name_length+1)).format(port["name"]))
            my_file.write(("=> {:}").format(port["name"]))

            if port["name"] == ports[-1]["name"]:   # last port does not get a ;
                my_file.write("\n")
            else:
                my_file.write(",\n")

        my_file.write("\t);\n")

def parseVerilogFile(filename):
    """extract the ports and their properties from the given Verilog file

    Args:
        filename (str): filename of the verilog file to be parsed
    """
    global module_name
    global ports

    isModule = False
    with open(filename) as my_file:
        for line in my_file:
            if "module" in line:
                if not "endmodule" in line:
                    isModule = True
                    module_name = line.split()[1]
                else: # module line
                    continue

            elif ";" in line:
                isModule = False

            if isModule:
                line = re.sub(r"\(\*(\s|.)*?\*\)", "", line)
                line = re.sub(r"\/\*(\s|.)*?\*\/", "", line)    # replace multiline comments
                                                                # single line comments

                line = line.replace("(","")
                line = line.replace(")","")
                line = line.replace(",","\n")
                #print(line, end="")

                line_split = line.split()

                if len(line_split) == 4:
                    direction = line_split[0]
                    type = line_split[1]
                    width = line_split[2]
                    name = line_split[3]
                elif len(line_split) == 3:
                    direction = line_split[0]
                    type = line_split[1]
                    width = None
                    name = line_split[2]
                else:
                    continue

                #print(direction, type, width, name)

                port = {}
                port["name"] = name
                port["dir"] = direction
                port["type"] = type
                port["width"] = width

                ports.append(port)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = str(sys.argv[1])

        print("#"*80)
        print("Convert " + filename + " to VHDL")
        print()

        parseVerilogFile(filename)

        print("found ports:")
        print('------------')
        for port in ports:
            #print(port)
            print('\t{:25}  {:8}  {:>5} '.format(port['name'], port['dir'], port['type']), end='')

            if port['width']:
                print('{:>8}'.format(port['width']))
            else:
                print()

        createVHDLtemplate(filename.replace(".v", ".vhdl"))