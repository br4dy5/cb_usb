#! python2

'''
Provide one, or a list of, hostname(s) and this script will identify the most recent usb activity, including 
the time of use, user account, and brand/product/serial of usb device. A csv report will be written and subsequent 
executions of the script will append to the initial report.

Brands/serials can be included and/or excluded (currently limited to one of each) using -i, -e
'''

from cbapi.response import *
import argparse
import csv
from datetime import datetime
import re


c = open('report.csv', 'ab')
now = datetime.now().replace(tzinfo=None, microsecond=0)
fields = ['hostname', 'user account', 'time of use', 'device', 'serial']
writer = csv.writer(c, dialect='excel')
writer.writerow(fields)

global cb
cb = CbEnterpriseResponseAPI()


def parse():
    '''
    Parses cmd line arguments for either one host, a list of hosts, or both
    '''
    parser = argparse.ArgumentParser(description='Identifies usb activity, the time of use, user account, and brand/product/serial of usb device')
    parser.add_argument('-m', '--host', help='hostname to query for USB activity')
    parser.add_argument('-l', '--list', help='file of list of hostnames, one per line, e.g. hosts.txt')
    parser.add_argument('-e', '--exclude', default="bydefaultwillnotexcludeanydevice", help='USB brand or serial to exclude, e.g. "samsung"')
    parser.add_argument('-i', '--include', default="*", help='USB brand or serial to query')
    parser.add_argument('-r', '--results', type=int, default=1, help='number of results returned per host. default=1')

    args = parser.parse_args()

    host = args.host
    bulk_list = args.list

    global include
    global exclude
    global results
    exclude = args.exclude
    include = args.include
    results = args.results

    global hosts
    hosts = []

    if bulk_list != None:
        with open(bulk_list, 'r') as f:
            hosts = [line.strip() for line in f]

    if host != None:

        hosts.append(host)


def create_record(hostname):
    '''
    Writes record of USB activity for provided hostname
    '''

    user = find_user(hostname)
    usb = find_usb(hostname)

    record = usb['date'], user['hostname'], user['account'], usb['device'], usb['serial'], usb['url']
    writer.writerow(record)
    print record


def find_usb(hostname):
    '''
    Finds process where regmods indicate USB activity     
    '''
    try:
        query = cb.select(Process)
        query = query.where("hostname:" + hostname).and_(
            "regmod:registry\machine\system\currentcontrolset\control\deviceclasses\{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\*").and_(
            "-regmod:registry\machine\system\currentcontrolset\control\deviceclasses\{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\*" + exclude + "*").and_(
            "regmod:registry\machine\system\currentcontrolset\control\deviceclasses\{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\*" + include + "*").and_(
            "-regmod:registry\machine\system\currentcontrolset\control\deviceclasses\{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\*snapshot*")

        query = query[:results]
        print "{0} processes found.".format(len(query))
        user = find_user(hostname)

        for proc in query:

            regmods = proc.regmods
            url = proc.webui_link
            usb_reg_mods = []

            for r in regmods:
                if "53f5630d-b6bf-11d0-94f2-00a0c91efb8b" in r.path:
                    event = r.timestamp, r.type, r.path
                    usb_reg_mods.append(event)

            regmod_path = usb_reg_mods[0][2]

            # regex to extract vendor of usb
            b = re.search('ven_(.*)&prod', regmod_path)
            brand = b.group(1)

            # regex to extract product name of usb
            p = re.search('prod_(.*)&rev', regmod_path)
            product = p.group(1)

            # regex to extract uniq ID (serial #) of usb
            s = re.search('rev_(.*)#', regmod_path)
            serial = s.group(1).split('#')[1]

            access_date = usb_reg_mods[0][0].replace(microsecond=0).isoformat()
            device = ("{0} {1}".format(brand, product)).lstrip()

            # compile and write record of activity details
            record = access_date, hostname, user, device, serial, url
            writer.writerow(record)
            print record

    except AttributeError:
        print "Process not found."


def find_user(hostname):
    '''
    Returns user account associated with most recent process on host 
    '''
    user_proc = cb.select(Process).where("hostname:" + hostname).and_(
        '-username:system AND -username:"network service" AND -username:"local service"').and_(
        "filemod_count:[1 TO *]").first()

    return user_proc.username


def main():
    parse()
    print "Checking {0} host(s)".format(len(hosts))
    print "Limiting to {0} results per host".format(results)
    while len(hosts) != 0:
        for host in hosts:
            print "Processing %s" % host
            find_usb(host)
            hosts.remove(host)
    print "All hosts have been processed."
    c.close()


if __name__ == "__main__":
    main()
