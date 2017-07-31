from netmiko import ConnectHandler
import re
import os
import threading
import datetime


def control(count, records):
    while count <= records:
        if router_info[count][1] == 'cisco':
            device_name = 'cisco_ios'
        else:
            count += 1
            continue
        device = {'device_type': device_name, 'ip': router_info[count][0], 'username': u_name, 'password': pwd}
        try:
            net_connect = ConnectHandler(**device)
        except:
            print ('Connection refused to ' + router_info[count][0])
            count += 1
            continue
# Cisco NCS router
        if device_name == 'cisco_ios' and router_info[count][0][0].lower() == 'c':
            try:
                cmd_output = net_connect.send_command("admin show environment power")
                file_generation_core(cmd_output, router_info[count][0])
            except:
                print ('Command cant be executed on ' + router_info[count][0])
                count += 1
                continue
# Cisco ASR series router
        elif device_name == 'cisco_ios' and router_info[count][0][0].lower() == 'p':
            try:
                cmd_output = net_connect.send_command("admin show environment power-supply")
                file_generation_pe(cmd_output, router_info[count][0])
            except:
                print ('Command cant be executed on ' + router_info[count][0])
                count += 1
                continue
        else:
            count += 1
            continue
        count += 1


def router_list():
# file which conatin the router names
    fo = open("test.txt", 'r')
    temp_list = []
    str = fo.readline()
    while str:
        temp_list += re.findall("(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", str)
        str = fo.readline()
    fo.close()
    length = len(temp_list)
    return (temp_list, length)


def file_generation_core(output, router_name):
    filename = router_name+'.txt'
    fo = open(filename, 'w')
    fo.write (output)
    fo.close()
    return()


def file_generation_pe(output, router_name):
    filename = router_name+'.txt'
    fo = open(filename, 'w')
    rec_count = 0
    data_header = re.findall(r'(\S+)\n\s+(\w+)\s+(\w+)\s+(\d+)\s+(\w+)',output)
    fo.write('R/S/I           Modules\t\t' + 'Capacity\t\t' + 'Status\n')
    for elements in data_header:
        rec_count += 1
        fo.write(elements[0] + '\t')
        fo.write(elements[1] + '\t')
        fo.write(elements[2] + '\t\t')
        fo.write(elements[3] + '\t\t\t')
        fo.write(elements[4] + '\n')
    fo.write('-----------------\n')
    data = re.findall(r'(\d+\/\w+\/\d+\/\*)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', output)
    fo.write('R/S/I\t\t\t' + 'Power Supply\t\t' + 'Voltage\t\t' + 'Current\n')
    for elements in data:
        rec_count += 1
        fo.write(elements[0] + '\t\t')
        fo.write(elements[1] + '\t\t\t')
        fo.write(elements[2] + '\t\t')
        fo.write(elements[3] + '\n')
    fo.write('-----------------\n')
    total = re.search('Total:\s+(\S+)',output)
    return()


router_info, records = router_list()
current_date_time = datetime.datetime.now()
string_current_date_time = str(current_date_time.year)+'_'+str(current_date_time.month)+'_'+str(current_date_time.day)+'_power_level'
try:
    os.makedirs(string_current_date_time)
    os.chdir(string_current_date_time)
except:
    os.chdir(string_current_date_time)
u_name = input('Enter the user name: ')
while u_name == '':
    print ('Enter a valid username')
    u_name = input("Enter the username: ")
pwd = input("Enter the password: ")
while pwd == '':
    print ('Enter a valid password')
    pwd = input("Enter the password: ")
threadcount = int(round(records**(0.5), 0))
no_of_elements = int(round(records/threadcount))
thread_call = 0
start_index = 0
end_index = no_of_elements - 1
obj = [None]*threadcount
while thread_call < threadcount:
    obj[thread_call] = threading.Thread(target=control, args=(start_index, end_index,), daemon=True)
    thread_call += 1
    start_index = end_index + 1
    if thread_call + 1 == threadcount:
        end_index = records-1
    else:
        end_index = start_index + no_of_elements - 1
thread_call = 0
while thread_call < threadcount:
    obj[thread_call].start()
    thread_call += 1
