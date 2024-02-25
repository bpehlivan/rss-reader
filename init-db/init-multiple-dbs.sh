#!/bin/bash

# see: https://github.com/mrts/docker-postgresql-multiple-databases
set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "  Creating user and database '$database'"

    # Check if the role exists
    if psql -t -c "SELECT 1 FROM pg_roles WHERE rolname='$database'" | grep -q 1; then
        echo "    Role '$database' already exists, skipping creation"
    else
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
            CREATE USER $database;
EOSQL
    fi

    # Check if the database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw $database; then
        echo "    Database '$database' already exists, skipping creation"
    else
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
            CREATE DATABASE $database;
            GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
    fi
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done
    echo "Multiple databases created"
fi
