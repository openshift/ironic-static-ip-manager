#!/usr/bin/env python

import os
import sys
import subprocess
import json
import ipaddress

# a cheap why of getting structured info without importing extra modules.
ip_addr = json.loads(subprocess.check_output(['ip', '-j', 'address']))

provisioning_ip = ipaddress.ip_address(os.environ['PROVISIONING_IP'])
provisioning_macs = os.environ['PROVISIONING_MACS'].split(',')
potential_interfaces = [iface for iface in ip_addr
                        if iface.get('address', '') in provisioning_macs]

# first look for an interface that is already configured.
for iface in potential_interfaces:
    for addr in iface.get('addr_info'):
        ip = ipaddress.ip_interface('{local}/{prefixlen}'.format(**addr))
        if provisioning_ip in ip.network:
            print(iface['ifname'])
            sys.exit(0)

# next look for unconfigured interfaces
for iface in potential_interfaces:
    if iface.get('operstate', '') == 'DOWN' or 'addr_info' not in iface:
        print(iface['ifname'])
        sys.exit(0)

# can't find a suitable interface
# just don't print anything and the calling script will error out.
