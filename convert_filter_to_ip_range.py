import re
from ipaddress import *
import argparse

parser = argparse.ArgumentParser(description='convert filter/list_original to filter/list_ip_with_star and filter/list_ip_range')

# 添加三個檔案路徑的參數
parser.add_argument('-io', '--ip_original', dest='ip_original', type=str, help='path to filter/list_original')
parser.add_argument('-iws', '--ip_with_star', dest='ip_with_star', type=str, help='path to filter/list_ip_with_star')
parser.add_argument('-ir', '--ip_range', dest='ip_range', type=str, help='path to filter/list_ip_range')


# 解析命令列參數
args = parser.parse_args()

ips = open(args.ip_original, 'r').read().splitlines()
ips_with_star = open(args.ip_with_star, 'w')
new_ips_f = open(args.ip_range, 'w')


domain_pattern = r'(\*.)?([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})(/\S*)?'
domain = ""
ip_solo = []
new_ip_ranges = [] # 儲存已經整理好的IP
ip_range = {}
ip_range["*"] = []
ip_section = [] # 儲存172.16.*中172這個section，如果是139.175.54.*，就儲存139.175

startIP_dec = []
endIP_dec = []

def split_continuous_numbers(numbers):
    # 切分連續的數列
    result = []
    current_group = []

    for i in range(len(numbers)):
        if i > 0 and numbers[i] != numbers[i - 1] + 1:
            # 如果當前數字不是前一個數字的後續，表示數列不連續，將目前的 group 加入結果中
            result.append(current_group)
            current_group = [numbers[i]]
        else:
            # 如果數字是連續的，將其添加到當前 group 中
            current_group.append(numbers[i])

    # 將最後一個 group 加入結果中
    if current_group:
        result.append(current_group)

    return result

def classify_all_ips():
    # 把IP分類，單獨的/有星號的/IP range的各一類，之後在合併
    global domain
    for ip in ips:
        if not bool(re.search(domain_pattern, ip)):
            if '*' not in ip and '-' not in ip:
                ip_solo.append(ip)
            elif "-" in ip:
                # new_ip_ranges.append(ip)
                startIP_dec.append(int(IPv4Address(ip.split('-')[0])))
                endIP_dec.append(int(IPv4Address(ip.split('-')[1])))
            else:
                ip_split = ip.split('.')
                ip_len = len(ip_split)
                if ip_len == 2:
                    ip_range["*"].append(int(ip_split[0]))

                elif ip_len == 3:
                    if ip_split[0] not in ip_section:
                        ip_section.append(ip_split[0])
                        ip_range[ip_split[0]] = []
                    ip_range[ip_split[0]].append(int(ip_split[1]))
                
                else:
                    tmp = ip_split[0]+"."+ip_split[1]
                    if tmp not in ip_section:
                        ip_section.append(tmp)
                        ip_range[ip_split[0]+"."+ip_split[1]] = []
                    ip_range[ip_split[0]+"."+ip_split[1]].append(int(ip_split[2]))

        else:
            domain += ip + '\n'

def sort_and_split_ip_section():
    # Sorting and Splitting Continuous Numbers
    for ip in ip_section:
        ip_range[ip].sort()
        ip_range[ip] = split_continuous_numbers(ip_range[ip])

    for ip in ip_section:
        for i in ip_range[ip]:
            if len(ip.split('.')) > 1:
                startIP_dec.append(int(IPv4Address(ip + "." + str(i[0]) + ".0")))
                endIP_dec.append(int(IPv4Address(ip + "." + str(i[-1]) + ".255")))
            else:
                startIP_dec.append(int(IPv4Address(ip + "." + str(i[0]) + ".0.0")))
                endIP_dec.append(int(IPv4Address(ip + "." + str(i[-1]) + ".255.255")))
    # print(startIP_dec, endIP_dec)

def merge_ip_range():
    # Merge the IP Range
    ip_range_len = len(startIP_dec)
    for i in range(ip_range_len):
        startIP = startIP_dec.pop()
        endIP = endIP_dec.pop()
        insert_or_not = True
        for j in range(len(startIP_dec)):
            if endIP >= startIP_dec[j] and endIP < endIP_dec[j]:
                startIP_dec[j] = startIP
                insert_or_not = False
                break
        if insert_or_not:
            startIP_dec.insert(0, startIP)
            endIP_dec.insert(0, endIP)

    for i in range(len(startIP_dec)):
        new_ip_ranges.append(str(IPv4Address(startIP_dec[i])) + "-" + str(IPv4Address(endIP_dec[i])))

def parse_ip_range(ip_list_with_star, range):
    section = str(range).split('/')[-1]
    if section not in ['24', '16', '8']:
        for subnet in list(ip_network(range).subnets()):
            if int(section) < 24:
                parse_ip_range(ip_list_with_star, subnet)
            else:
                for i in IPv4Network(subnet):
                    ip_list_with_star.append(str(i))
            
    elif section == '24':
        ip_list_with_star.append(".".join(str(range).split('/')[0].split('.')[:-1]) + ".*")
    elif section == "16":
        ip_list_with_star.append(".".join(str(range).split('/')[0].split('.')[:-2]) + ".*.*")
    elif section == "8":
        ip_list_with_star.append(".".join(str(range).split('/')[0].split('.')[:-3]) + ".*.*.*")

def transfer_ip_range_2_star(startip, endip):
    startip = IPv4Address(startip)
    endip = IPv4Address(endip)
    ranges = [ipaddr for ipaddr in summarize_address_range(startip, endip)]
    ip_list_with_star = []
    for range in ranges:
        parse_ip_range(ip_list_with_star, range)
    
    return "\n".join(ip_list_with_star) + "\n"

classify_all_ips()
sort_and_split_ip_section()
merge_ip_range()
ip_list_with_star = ""
for new_ip_range in new_ip_ranges:
    start, end = new_ip_range.split('-')
    ip_list_with_star += transfer_ip_range_2_star(start, end)


new_ip_ranges.sort()
ip_solo.sort()

new_ips_f.write(domain + "\n".join(new_ip_ranges) + "\n" + "\n".join(ip_solo))
new_ips_f.close()
ips_with_star.write(domain + ip_list_with_star + "\n".join(ip_solo))