
import re

module_name = ""
ports = []

def createVHDLtemplate(filename):
    global module_name
    global ports

    with open(filename, "w") as my_file:

        my_file.write("COMPONENT " + module_name + " IS\n")
        my_file.write("\tPORT (\n")

        # port["name"] = name
        # port["dir"] = direction
        # port["type"] = type
        # port["width"] = width

        for port in ports:
            my_file.write("\t\t"+port["name"]+" : ")
            if port["dir"] == "input":
                my_file.write( "IN " )
            elif port["dir"] == "output":
                my_file.write( "IN " )
            elif port["dir"] == "inout":
                my_file.write( "INOUT " )
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


def parseVerilogFile(filename):

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
    filename = "../../modules/Ethernet/build/gateware/liteeth_core.v"
    parseVerilogFile(filename)
    createVHDLtemplate(filename.replace(".v", ".vhdl"))