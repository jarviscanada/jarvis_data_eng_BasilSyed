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

# Saving Machine State Variables
vmstat_mb=$(vmstat --unit M)
hostname=$(hostname -f)

# Hardware specification variables
memory_free=$(echo "$vmstat_mb" | tail -1 | awk -v col="4" '{print $col}')
cpu_idle=$(echo "$vmstat_mb" | tail -1 | awk '{print $15}')
cpu_kernel=$(echo "$vmstat_mb" | tail -1 | awk '{print $14}')
disk_io=$(vmstat -d | tail -1 | awk -v col="10" '{print $col}')
disk_available=$(df -BM | grep /dev/sda2 | awk '{print $4}' | tr -d 'M') #the tr -d drops the trailing M

# Current time in `2019-11-26 14:40:19` UTC format
timestamp=$(vmstat -t | tail -1 | awk '{print $18,$19}')

# Subquery to find matching id in host_info table
host_id="(SELECT id FROM host_info WHERE hostname='$hostname')"

insert_stmt="INSERT INTO host_usage(timestamp,host_id,memory_free,cpu_idle,cpu_kernel,disk_io,disk_available) VALUES ('$timestamp',$host_id,'$memory_free','$cpu_idle','$cpu_kernel','$disk_io','$disk_available');"

# env setup and psql command
export PGPASSWORD=$psql_password

psql -h $psql_host -p $psql_port -d $db_name -U $psql_user -c "$insert_stmt"
exit $?

