import logging
import pandas as pd
from pyzabbix import ZabbixAPI
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)

# Load configuration from .env file
load_dotenv()

ZABBIX_SERVER = os.getenv('ZABBIX_SERVER')
ZABBIX_API_KEY = os.getenv('ZABBIX_API_KEY')
EXCEL_FILE = os.getenv('EXCEL_FILE')

# Authenticate to Zabbix API using the API key
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(api_token=ZABBIX_API_KEY)

# Read the Excel file
df = pd.read_excel(EXCEL_FILE)

# Iterate over each row and add the switch to Zabbix
for index, row in df.iterrows():
    ip = row['IP']
    host_name = row['Zabbix Host name']
    group1 = row['Zabbix Group1']
    group2 = row['Zabbix Group2']
    template = row['Zabbix Template']

    # Find or create host groups
    group_ids = []
    for group in [group1, group2]:
        if pd.notna(group):
            group_obj = zapi.hostgroup.get(filter={"name": group})
            if group_obj:
                group_ids.append(group_obj[0]['groupid'])
            else:
                logging.warning(f"Group {group} not found")
                # new_group = zapi.hostgroup.create(name=group)
                # group_ids.append(new_group['groupids'][0])

    # Find the template ID
    template_id = None
    if pd.notna(template):
        template_obj = zapi.template.get(filter={"host": template})
        if template_obj:
            template_id = template_obj[0]['templateid']
        else:
            logging.warning(f"Template {template} not found, skipping host {host_name}.")
            continue

    # Create the host in Zabbix
    try:
        zapi.host.create({
            "host": host_name,
            "interfaces": [{
                "type": 2,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "161",
                "details": {
                    "version": 2,
                    "community": "{$SNMP_COMMUNITY}"
                }
            }],
            "groups": [{"groupid": gid} for gid in group_ids],
            "templates": [{"templateid": template_id}]
        })
        logging.info(f"Host {host_name} added successfully.")
    except Exception as e:
        logging.error(f"Failed to add host {host_name}: {e}")
