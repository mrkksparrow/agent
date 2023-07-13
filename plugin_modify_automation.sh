#!/bin/bash

# exporting path for pip upgrade
export LD_LIBRARY_PATH=/lib64/:${LD_LIBRARY_PATH}
pip3 install --upgrade pip

#install pip module oracledb
pip3 install oracledb

# loop through all plugins in if file ends with .py change content 
for f in /opt/site24x7/monagent/plugins/*/*
do
	if [[ $f == *.py ]]; then
		sed -i "s/\bimport cx_Oracle\b/import oracledb/" $f
		sed -i 's/\bimport os\b/import os,warnings;warnings.filterwarnings("ignore")/' $f
		if [[ $f == *oracle_temp_tablespaces.py ]]; then
			sed -i "s/\bconn = cx_Oracle.connect(self.username,self.password,\b/conn = oracledb.connect(user=self.username, password=self.password, dsn=/" $f
		else
			sed -i "s/\bconn = cx_Oracle.connect\b/conn = oracledb.connect/" $f
		fi
		echo $f
	fi
done
