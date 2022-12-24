#/bin/bash

# Export the current dbeaver creds into creds/dbeaver_data-sources.json
# cp .local/share/DBeaverData/workspace6/General/.dbeaver/data-sources.json creds/dbeaver_data-sources.json
# cp .local/share/DBeaverData/workspace6/General/.dbeaver/credentials-config.json ./creds/dbeaver_credentials-config.json

# Export the current MongoDB Data Sources into creds/mongo_db_compass_connections
# cp -r $HOME/.config/MongoDB\ Compass/Connections/ $HOME/creds/mongo_db_compass_connections

echo "Loading DBeaver data-source and credentials-config into DBeaver application 🔒 . . ."
cp $HOME/creds/dbeaver_data-sources.json $HOME/.local/share/DBeaverData/workspace6/General/.dbeaver/data-sources.json 
cp $HOME/creds/dbeaver_credentials-config.json $HOME/.local/share/DBeaverData/workspace6/General/.dbeaver/credentials-config.json 
echo "Succesfully loaded data. Please check if it's working properly directly on DBeaver application"

echo "Loading MongoDB Compass data-source  into MongoDB Compass application 🔒 . . ."
cp -r $HOME/creds/mongo_db_compass_connections $HOME/.config/MongoDB\ Compass/Connections/ 
echo "Succesfully loaded data. Please check if it's working properly directly on MongoDB Compass application"

