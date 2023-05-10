from io import TextIOWrapper
import psutil
import gpustat
import time 
from time import sleep

def print_device_inf():
    print("------------- Info [RAM]-------------")
    print(ram_data())
    print("------------- Info [CPU]-------------")
    print(cpu_data())
    print("------------- Info [GPU]-------------")
    print(gpu_data())
    print("------------- Info [DISK]-------------")
    print(disk_data())


def ram_data() -> str:
    memoryinfo = psutil.virtual_memory()
    totalMem = memoryinfo.total/(1024*1024*1024)
    return "Total RAM : "+"{:.2f}".format(totalMem)+" Gb"


def cpu_data() -> str:
    freq = psutil.cpu_freq(percpu=True)
    cpufreq = ""
    for id,fr in enumerate(freq):
        cpufreq += "[{}] {} MHz \n".format(id,fr.max)
    return cpufreq

def gpu_data() -> str:
    gpus = gpustat.GPUStatCollection[0].new_query().jsonify().get("gpus")
    res = ""
    for gp in gpus:
        res += "[{}] {} {} Mb".format(gp["index"],gp["name"],gp["memory.total"])
    return res    

def disk_data() -> str:
    totalDisk = psutil.disk_usage("/").total/(1024*1024*1024)
    return "Total DISK : {:.2f} Gb".format(totalDisk)

def available_ram() -> str:
    memoryinfo = psutil.virtual_memory()
    availInGb = memoryinfo.available/(1024*1024*1024)
    res = "{:.2f} Gb - {}%".format(availInGb,memoryinfo.percent)
    return res

    
def gpu_load() -> str:
    info = gpustat.GPUStatCollection[0].new_query().jsonify()["gpus"]
    res = ""
    for gpu in info:
        res += "{} : {}Mb - {}% - {}C".format(gpu["name"],gpu["memory.used"],gpu["utilization.gpu"],gpu["temperature.gpu"])
    return res


def cpu_load() -> str:
    percs = psutil.cpu_percent(percpu=True)
    res = "CPU Util : "
    for (i,p) in enumerate(percs):
        res += "[CORE({}) {}%]\t".format(i,p)
    temps = psutil.sensors_temperatures()["coretemp"]
    res += "\nCPU Temps : "
    for (i,t) in enumerate(temps):
        res += "[UNIT({}) {}C]\t".format(i,t.current)
    return res



def create_open_file(file) -> TextIOWrapper:
    unix = time.time()
    rfile = open("{}/{}.csv".format(file,unix),mode="w")
    rfile.write("timestamp,unit,detail\n")
    return rfile

def write(file:TextIOWrapper):
    cpu = cpu_load()
    ram = available_ram()
    gpu =gpu_load()
    date = time.time()
    file.write("{},{},{}\n".format(date,"cpu",cpu))
    file.write("{},{},{}\n".format(date,"gpu",gpu))
    file.write("{},{},{}\n".format(date,"ram",ram))

print_device_inf()

update_interval = -1

while True:
    try:
        update_interval = int(input("enter updating interval in seconds [1-5] : "))
    except:
        print("--> Enter Valid Number!")
        continue;   
    if not(0 <= update_interval <= 5):
        print("--> enter between 1-5")
        continue
    break

print("--> Interval has been set on "+str(update_interval)+"s")

file = None

while True:
    try:
        fileName = input("Enter export file folder : ")
        file = create_open_file(fileName)
    except:
        print("--> Folder not found or permission denied!")
        continue;  
    break;

while True:
    sleep(update_interval)
    print("\033c", end="")
    print(cpu_load())
    print(available_ram())
    print(gpu_load())
    write(file)