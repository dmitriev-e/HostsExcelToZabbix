1. Rename .env.sample to .env
2. Edit .env with your parameters
3. Fill Excel file hosts_to_zbx.xlsx with your data
4. Run create_hosts_from_excel.py

Script will create host in Zabbix with one SNMP interface:
- snmp port - 161
- snmp community - {$SNMP_COMMUNITY}