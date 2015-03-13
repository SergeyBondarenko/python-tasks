#!/usr/bin/python

import os, sys, time, smtplib, subprocess


warnings_list = ['GigabitEthernet6/1, changed state to', 'GigabitEthernet6/2, changed state to',
                'GigabitEthernet5/1, changed state to', 'GigabitEthernet5/2, changed state to', 'udld error']
script_log_file = '/var/log/remotesyslog/CiscoDWDM.log'
switch_dict = {'iwbg-bb01':'10.254.128.1', 'iwbg-bb02':'10.254.128.2', 'iwbs-bb01':'10.221.0.1', 'iwbs-bb02':'10.221.0.2'}
switch_names = switch_dict.keys()
switch_warn_count = {'iwbg-bb01':0, 'iwbg-bb02':0, 'iwbs-bb01':0, 'iwbs-bb02':0}
today_file = time.strftime('%Y.%m.%d.messages.log')
now_time = time.strftime('%Y.%m.%d %H:%M')
email_sender = 'check_cisco_dwdm_script@sorint.it'
email_receivers = ['onsite-iwbank@sorint.it']
email_receivers_udld = ['onsite-iwbank@sorint.it', 'sd-iwbank@sorint.it']
cisco_log_path = '/var/log/remotesyslog/'
ref_var_path = '/private/home/toor/tmp/'
link_status = 'LINK-3-UPDOWN'
udld_error = 'udld error'
udld_status = 'PM-SP-4-ERR_DISABLE'

def func_Create_Script_Log(file):
        file = open(file, "a+")
        file.close()


def func_Read_File(file):
        file = open(file, "r")
        num = int(file.read())
        file.close()
        return num

def func_Write_File(file, num):
        file = open(file, "w+")
        file.write(str(num))
        file.close()

# Check status of DWDM ports
def func_Find_Switch_Conn(error, switch):
        if switch == 'iwbg-bb01':
                if error == warnings_list[3]:
                        return "iwbg-bb01(Gi5/2) -> iwbs-bb01(Gi5/2)"
                if error == warnings_list[1]:
                        return "iwbg-bb01(Gi6/2) -> iwbs-bb01(Gi6/2)"
                if error == warnings_list[2]:
                        return "iwbg-bb01(Gi5/1) -> iwmi-in01a(Gi1/0/49)"
                if error == warnings_list[0]:
                        return "iwbg-bb01(Gi6/1) -> iwmi-in01a(Gi1/0/50)"
                if error == warnings_list[4]:
                        return "UDLD Error detected"
        if switch == 'iwbs-bb01':
                if error == warnings_list[3]:
                        return "iwbs-bb01(Gi5/2) -> iwbg-bb01(Gi5/2)"
                if error == warnings_list[1]:
                        return "iwbs-bb01(Gi6/2) -> iwbg-bb01(Gi6/2)"
                if error == warnings_list[2]:
                        return "iwbs-bb01(Gi5/1) -> iwmi-in01b(Gi1/0/51)"
                if error == warnings_list[0]:
                        return "iwbs-bb01(Gi6/1) -> iwmi-in01b(Gi1/0/52)"
                if error == warnings_list[4]:
                        return "UDLD Error detected"
        if switch == 'iwbg-bb02':
                if error == warnings_list[3]:
                        return "iwbg-bb02(Gi5/2) -> iwbs-bb02(Gi5/2)"
                if error == warnings_list[1]:
                        return "iwbg-bb02(Gi6/2) -> iwbs-bb02(Gi6/2)"
                if error == warnings_list[2]:
                        return "iwbg-bb02(Gi5/1) -> iwmi-in01b(Gi1/0/49)"
                if error == warnings_list[0]:
                        return "iwbg-bb02(Gi6/1) -> iwmi-in01b(Gi1/0/50)"
                if error == warnings_list[4]:
                        return "UDLD Error detected"
        if switch == 'iwbs-bb02':
                if error == warnings_list[3]:
                        return "iwbs-bb02(Gi5/2) -> iwbg-bb02(Gi5/2)"
                if error == warnings_list[1]:
                        return "iwbs-bb02(Gi6/2) -> iwbg-bb02(Gi6/2)"
                if error == warnings_list[2]:
                        return "iwbs-bb02(Gi5/1) -> iwmi-in01a(Gi1/0/51)"
                if error == warnings_list[0]:
                        return "iwbs-bb02(Gi6/1) -> iwmi-in01a(Gi1/0/52)"
                if error == warnings_list[4]:
                        return "UDLD Error detected"


# Write into script log file
def func_Write_Script_Log(switch, connect, file, msg, time, refvalue):
        swCon = connect
        file = open(file, "a")
        file.write('Time:' + ' ' + time + ' ' +'Switch:' + ' ' + switch + ' ' + 'Connection:' + ' ' + swCon  +'\n')
        file.write('Ref value: ' + str(refvalue) + '\n')
        file.write(msg + '\n')
        file.write('\n')
        file.close()

# Send email msg
def func_Email_Warning(msg, sw, time, connect):
        he0 = "Se ricevete questa mail significa che un link dwdm e andato down"
        he1 = " perche' e stato messo in stato 'error-disable' dal protocollo UDLD che si occupa"
        he2 = " di monitorare il link stesso. In calce il syslog per intero indicante la precisa"
        he3 = " interfaccia che e' andata down, cosi' come l'ip dell'apparato a cui quell'interfaccia appartiene."
        msg_header = he0 + he1 + he2 + he3
        fo0 = "In questo caso va seguita il CASO 1 della procedura IWBANK - link DWDM che trovate su"
        fo1 = " sapientino che prevede di chiamare il reperibile NETWORK SORINT."
        fo2 = " Sulla procedura trovate tutti i passi da seguire."
        msg_footer = fo0 + fo1 + fo2
        swCon = connect
        if swCon == "UDLD Error detected":
                emailSubj = 'IWBANK - LINK DWDM - "%s" - UDLD error' % (sw)
                msg = 'Subject: %s\n\n%s\n\n\n%s\n%s\n%s\n\n%s\n\n\n%s' % (emailSubj, msg_header, time, sw, swCon, msg, msg_footer)
        else:
                emailSubj = 'IWBANK - LINK DWDM - "%s" - port down/up' % (sw)
                msg = 'Subject: %s\n\n%s\n%s\n%s\n\n%s\n' % (emailSubj, time, sw, swCon, msg)

        smtpObj = smtplib.SMTP('localhost')

        if swCon == "UDLD Error detected":
                smtpObj.sendmail(email_sender, email_receivers_udld, msg)
        else:
                smtpObj.sendmail(email_sender, email_receivers, msg)

# Look for warnings in Cisco log files
def func_Look_for_Warnings(nowtime, switch, switchlog, count, refcount, scriptlog):
        warn_count = 0
        cisco_log_file = open(switchlog, "r")
        for line in cisco_log_file:
                for warning in warnings_list:
                        if (warning in line) and ((link_status in line) or (udld_status in line)):
                                warn_count += 1
                                if warn_count > refcount:
                                        switch_connect = func_Find_Switch_Conn(warning, switch)
                                        func_Write_Script_Log(switch, switch_connect, script_log_file, line, nowtime, refcount)
                                        func_Email_Warning(line, switch, nowtime, switch_connect)
        cisco_log_file.close()
        return warn_count


for switch in switch_dict:
        switch_dict[switch] = cisco_log_path + switch_dict[switch] + '/' + today_file
#print(switch_dict)

func_Create_Script_Log(script_log_file)

for switch in switch_dict:
        #print(switch_dict[switch])
        if os.path.isfile(switch_dict[switch]):
                num_of_warnings = func_Look_for_Warnings(now_time, switch, switch_dict[switch], switch_warn_count[switch], func_Read_File(ref_var_path + switch), script_log_file)
#               print(num_of_warnings)
                func_Write_File(ref_var_path + switch, num_of_warnings)
        else:
                func_Write_File(ref_var_path + switch, 0)

