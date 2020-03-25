import glob
from datetime import datetime


def find_indexOfFirstNull(bytes):
    count = 0
    for byte in bytes:
        if byte == 0:
            return count
        count += 1
    return count

class C_FILE:
    size = 32

    def __init__(self, raw_data):
        self.raw = raw_data

        self.size_of_element = int.from_bytes(self.raw[0:4], byteorder='little', signed=True)
        temp = self.raw[4:4 + find_indexOfFirstNull(self.raw[4:19])]
        self.name = temp.decode("utf-8")
        self.creation_time = int.from_bytes(self.raw[20:24], byteorder='little', signed=False)
        self.last_time_modified = int.from_bytes(self.raw[24:28], byteorder='little', signed=False)
        self.num_of_files = int.from_bytes(self.raw[28:32], byteorder='little', signed=True)

    def convert_str(self):
        ret_str = ""
        #ret_str += "raw: " + str(self.raw) + "\n"
        ret_str += "size_of_element: " + str(self.size_of_element) + "\n"
        ret_str += "name: " + self.name + "\n"
        ret_str += "creation_time: " + str(self.creation_time) + "\n"
        ret_str += "last_time_modified: " + str(self.last_time_modified) + "\n"
        ret_str += "num_of_files: " + str(self.num_of_files) + "\n"
        return ret_str

class FS_data:

    def __init__(self, raw_data):
        self.raw = raw_data
        
        self.numberOfFiles = int.from_bytes(self.raw[0:4], byteorder='little', signed=True)
        SD = int.from_bytes(self.raw[4:8], byteorder='little', signed=True)

        if SD == 2:
            self.SD = "B"
        elif SD == 1:
            self.SD = "A"
        else:
            self.SD = "corrupted"

        count = 8
        self.files = []
        while (count < len(self.raw) - (len(self.raw) % C_FILE.size)):
            #print("count: " + str(count))
            try:
                var = C_FILE(self.raw[count: count + C_FILE.size])
            except:
                count += C_FILE.size
                continue
            self.files.append(var)
            #print(self.files[-1].name)
            count += C_FILE.size
    
    def convert_str(self):
        ret_str = ""
        ret_str += "numberOfFiles: " + str(self.numberOfFiles) + "\n"
        ret_str += "used SD: " + self.SD + "\n"
        ret_str += "files: \n"
        for file in self.files:
            temp = file.convert_str()
            temp = temp.split("\n")
            ret_str += "    -" + temp[0] + "\n"
            for line in temp[1::]:
                ret_str += "     " + line + "\n"
        
        return ret_str

        

def get_dataFromCSVFile(file_handler):
    return file_handler.readlines()[6].split(",", 10)[2]

def get_CSVNames(dir_path):
    return glob.glob(dir_path + "/*.csv")
    
def get_rawData_CSVfiles(dir_path):
    ret_str = ""
    file_path_list = get_CSVNames(dir_path)
    file_path_list.sort(key=lambda x: x.split("-")[-11][0:x.split("-")[-11].find(" GTIME")] + ": ")
    for file_path in file_path_list:
        with open(file_path, newline='') as csvfile:
            ret_str += get_dataFromCSVFile(csvfile) + "-"
            #print(file_path.split("-")[-11][0:file_path.split("-")[-11].find(" GTIME")] + ": ")
            #print(get_dataFromCSVFile(csvfile))
            #print()
    return ret_str[0:-1]


print("Location of CSV files to parse: ")
path = input()
FRAM_data = get_rawData_CSVfiles(path)
#print(FRAM_data)
#print()
IdidIt = FS_data(bytearray.fromhex(FRAM_data.replace('-', '')))
print(IdidIt.convert_str())
