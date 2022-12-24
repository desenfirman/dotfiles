#!/bin/bash
docker container stop mysql-55 && docker container rm mysql-55 & docker run --name mysql-55 \
	-v /opt/mysql5.5-data/:/var/lib/mysql \
	--network="host"\
	-e MYSQL_ROOT_PASSWORD=Secret999 \
	-e MYSQL_USER=desenfirman \
	-e MYSQL_PASSWORD=27121997 \
	-d mysql:5.5 \
	--server-id=1 \
  	--log-bin=/var/lib/mysql/mysql-bin.log
