#!/bin/bash

# CLI arguments
cmd=$1
db_username=$2
db_password=$3

# Start docker
sudo systemctl status docker || sudo systemctl start docker

# Check status
docker container inspect jrvs-psql
container_status=$?

# Switch cases to handle create|stop|start
case $cmd in
	create)
	
	# Check container existence
	if [ $container_status -eq 0 ]; then 
		echo 'Container already exists'
		exit 1
	fi

	# Check number of CLI
	if [ $# -ne 3 ]; then
		echo 'Create requires username & password'
		exit 1
	fi

	# Create container
	docker volume create pgdata
	docker run --name jrvs-psql -e POSTGRES_USER=$db_username -e POSTGRES_PASSWORD=$db_password -d -v pgdata:/var/lib/postgresql/data -p 5432:5432 postgres:9.6-alpine
	exit $?
	;;

	start|stop)
	
	# Check container existence
        if [ $container_status -ne 0 ]; then 
                echo 'Container has not been created'
                exit 1
        fi

	# Start or stop the container
	docker container $cmd jrvs-psql
	exit $?
	;;

	*) 
	echo 'Illegal command'
	echo 'Commands: start|stop|create'	
	exit 1
	;;
esac

