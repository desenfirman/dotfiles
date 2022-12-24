MYSQL_MASTER_HOST=10.88.1.1
MYSQL_SLAVE_HOST=10.88.1.12
MYSQL_MASTER_USER=root
MYSQL_MASTER_PASS=Secure999
MYSQL_SLAVE_USER=root
MYSQL_SLAVE_PASS=P4ssw0rD

MYSQL_MASTER_CONN="-u${MYSQL_MASTER_USER} -p${MYSQL_MASTER_PASS}"
MYSQL_SLAVE_CONN="-u${MYSQL_SLAVE_USER} -p${MYSQL_SLAVE_PASS}" 
MYSQL_MASTER_CONN="-h${MYSQL_MASTER_HOST} ${MYSQL_MASTER_CONN} -P 83306"
MYSQL_SLAVE_CONN="-h${MYSQL_SLAVE_HOST} ${MYSQL_SLAVE_CONN}"

MYSQLDUMP_OPTIONS="--source-data=1"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS} --single-transaction"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS} --routines"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS} --triggers"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS} --flush-privileges"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS} --all-databases"

# CREATE_REPL_USER="GRANT REPLICATION SLAVE ON *.* TO repluser@'%' IDENTIFIED BY 'replpass'"
# mysql ${MYSQL_MASTER_CONN} -AN -e"${CREATE_REPL_USER}"

RELOAD_FILE=MySQLData.sql
echo "STOP SLAVE;" > ${RELOAD_FILE}
echo "CHANGE MASTER TO master_host='${MYSQL_MASTER_HOST}'," >> ${RELOAD_FILE}
echo "master_port=83306," >> ${RELOAD_FILE}
echo "master_user='${MYSQL_MASTER_USER}'," >> ${RELOAD_FILE}
echo "master_password='${MYSQL_MASTER_PASS}'," >> ${RELOAD_FILE}
echo "master_log_file='dummy-file'," >> ${RELOAD_FILE}
echo "master_log_pos=1;" >> ${RELOAD_FILE}
# mysqldump ${MYSQL_MASTER_CONN} ${MYSQLDUMP_OPTIONS} >> ${RELOAD_FILE}
echo "START SLAVE;" >> ${RELOAD_FILE}
