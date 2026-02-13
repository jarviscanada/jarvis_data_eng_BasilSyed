#!/bin/bash

# Arguments
psql_host=$1
psql_port=$2
db_name=$3
psql_user=$4
psql_password=$5

# Validating Args
if [ "$#" -ne 5 ]; then
      	echo "Illegal number of parameters"
	exit 1
fi

hostname=$(hostname -f)
lscpu_out=$(lscpu)
cpu_number=$(echo "$lscpu_out" | egrep "^CPU\(s\):" | awk '{print $2}' | xargs)
cpu_architecture=$(echo "$lscpu_out" | egrep "^Architecture:" | awk '{print $2}' | xargs)
cpu_model=$(echo "$lscpu_out" | egrep "^Model name:" | awk '{for (i=3; i<=NF; i++) print $i}' | xargs) #NF=last token of line
cpu_mhz=$(cat /proc/cpuinfo | grep -m 1 "MHz" | awk '{print $4}' | xargs)
l2_cache=$(echo "$lscpu_out" | grep "L2" | awk '{print $3}' | xargs)
total_mem=$(vmstat --unit M | tail -1 | awk '{print $4}')
timestamp=$(date '+%F %T')

insert_stmt="INSERT INTO host_info (hostname,cpu_number,cpu_architecture,cpu_model,cpu_mhz,l2_cache,timestamp,total_mem) VALUES  ('$hostname','$cpu_number','$cpu_architecture','$cpu_model','$cpu_mhz','$l2_cache','$timestamp','$total_mem') ON CONFLICT (hostname) DO NOTHING;"

export PGPASSWORD=$psql_password
psql -h "$psql_host" -p "$psql_port" -U "$psql_user" -d "$db_name" -c "$insert_stmt" 

exit $?
