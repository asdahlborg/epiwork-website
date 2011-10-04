#!/bin/bash
#
# Bootstraps everything installing Django and all required eggs, configuring
# the database and making sure a consistent Mono development environment is
# installed.

# Here we customize src/epiweb/settings.py by setting the user preferred
# database, language and country. Note that the database and the user used
# to connect should already exist.

DB_ENGINE=""
DB_NAME=""
DB_HOST=""
DB_PORT=""
DB_USERNAME=""
DB_USERNAME=""
DJANGO_ENGINE="unconfigured"
TIMEZONE=""
LANGUAGE=""
COUNTRY=""

echo ""
echo -n "Checking for pre-requisites: python ... "
exe_python="$(which python)"
if [ -n "$exe_python" ] ; then
    echo "$exe_python"
else
    echo "no found; place make sure Python 2.6 is installed"
    echo ""
    exit 1
fi

echo ""
echo -n "Checking for pre-requisites: easy_install ... "
exe_easy_install="$(which easy_install)"
if [ -n "$exe_easy_install" ] ; then
    echo "$exe_easy_install"
else
    echo "no found; place make sure setuptools are installed"
    echo ""
    exit 1
fi

echo ""
echo -n "Checking for pre-requisites: pip ... "
exe_pip="$(which pip)"
if [ -n "$exe_pip" ] ; then
    echo "$exe_pip"
else
    echo "no found; place make sure pip is installed (sudo easy_install pip)"
    echo ""
    exit 1
fi

echo ""
echo -n "Checking for pre-requisites: virtualenv ... "
exe_virtualenv="$(which virtualenv)"
if [ -n "$exe_virtualenv" ] ; then
    echo "$exe_virtualenv"
else
    echo "no found; place make sure virtualenv is installed (sudo pip install --upgrade virtualenv)"
    echo ""
    exit 1
fi

echo -n "Checking for pre-requisites: mysql ...  "
exe_mysql="$(which mysql)"
if [ -n "$exe_mysql" ] ; then
    echo "$exe_mysql"
else
    echo "not found; automatic MySQL configuration disabled"
fi

echo -n "Checking for pre-requisites: mysql_config ...  "
exe_mysql_config="$(which mysql_config)"
if [ -n "$exe_mysql_config" ] ; then
    echo "$exe_mysql_config"
else
    unset exe_mysql
    echo "not found; automatic MySQL configuration disabled (please install the libmysqlclient-dev package)"
fi

echo -n "Checking for pre-requisites: psql ...  "
exe_psql="$(which psql)"
if [ -n "$exe_psql" ] ; then
    echo "$exe_psql"
else
    echo "not found; automatic PostgreSQL configuration disabled"
fi

# Can we keep access to mapnik module and still use --no-site-packages?
# virtualenv --no-site-packages .
virtualenv .

source ./bin/activate

pip install -r requirements.txt

if [ -n "$exe_mysql" ] ; then
    pip install MySQL-python
fi
if [ -n "$exe_psql" ] ; then
    pip install psycopg2
fi

echo ""
while [ -z "$LANGUAGE" ] ; do
    echo -n "Please, choose your country and language (be, it, nl, uk, pt, se): "
    read line && [ -n "$line" ] && LANGUAGE="$line";
    COUNTRY="$LANGUAGE"
done

while [ -z "$TIMEZONE" ] ; do
    test -f /etc/timezone && TIMEZONE="$(cat /etc/timezone)"
    echo -n "Please, enter your time zone (default is $TIMEZONE): "
    read line && [ -n "$line" ] && TIMEZONE="$line";
done

while [ -z "$DB_ENGINE" ] ; do
    echo -n "Please, choose a database engine (sqlite3, the default, postgresql or mysql): "
    read line
    DB_ENGINE="${line:-sqlite3}"
    if [ "$DB_ENGINE" != "sqlite3" -a "$DB_ENGINE" != "mysql" -a "$DB_ENGINE" != "postgresql" ] ; then
        DB_ENGINE=""
    fi
done

if [ "$DB_ENGINE" = "sqlite3" ] ; then
    DB_NAME="ggm.db"
    DJANGO_ENGINE="sqlite3"
fi

if [ "$DB_ENGINE" = "mysql" ] ; then
    echo ""
    
    echo -n "Database host (just hit enter if on localhost/same host): "
    read line && [ -n "$line"] && DB_HOST="$line";
    
    echo -n "Database port (just hit enter if using default port): "
    read line && [ -n "$line"] && DB_PORT="$line";
    
    while [ -z "$DB_NAME" ] ; do
        echo -n "Database name (database will be created if necessary; default is epiwork): "
        read line && DB_NAME="${line:-epiwork}";
    done

    while [ -z "$DB_USERNAME" ] ; do
        echo -n "Database username (user will be created if necessary; default is epiwork): "
        read line && DB_USERNAME="${line:-epiwork}";
    done

    while [ -z "$DB_PASSWORD" ] ; do
        echo -n "Database password: "
        read line && [ -n "$line" ] && DB_PASSWORD="$line";
    done    

    DJANGO_ENGINE="mysql"
    
    if [ -n "$exe_mysql" ] ; then
        echo ""
        echo "Note: the following data will NOT be saved, but it is necessary to create"
        echo "the database '$DB_NAME' and the user '$DB_USERNAME' that will be used to"
        echo "connect to database for normal operation."
        
        echo ""
        echo -n "Please, insert MySQL administrator's username (default is root): "
        read line
        root_username="${line:-root}"
    
        root_password=""
        while [ -z "$root_password" ] ; do
            echo -n "Please, insert MySQL administrator's passsword: "
            read line && [ -n "$line" ] && root_password="$line";
        done
    fi
fi

if [ "$DB_ENGINE" = "postgresql" ] ; then
    echo ""
    
    echo -n "Database host (just hit enter if on localhost/same host): "
    read line && [ -n "$line" ] && DB_HOST="$line";
    
    echo -n "Database port (just hit enter if using default port): "
    read line && [ -n "$line" ] && DB_PORT="$line";
    
    while [ -z "$DB_NAME" ] ; do
        echo -n "Database name (database will be created if necessary; default is epiwork): "
        read line && DB_NAME="${line:-epiwork}";
    done

    while [ -z "$DB_USERNAME" ] ; do
        echo -n "Database username (user will be created if necessary; default is epiwork): "
        read line && DB_USERNAME="${line:-epiwork}";
    done

    while [ -z "$DB_PASSWORD" ] ; do
        echo -n "Database password: "
        read line && [ -n "$line" ] && DB_PASSWORD="$line";
    done    

    DJANGO_ENGINE="postgresql_psycopg2"
    
    if [ -n "$exe_psql" ] ; then
        echo ""
        echo "Note: the following data will NOT be saved, but it is necessary to create"
        echo "the database '$DB_NAME' and the user '$DB_USERNAME' that will be used to"
        echo "connect to database for normal operation."
        
        echo ""
        echo -n "Please, insert PostgrSQL administrator's username (default is postgres): "
        read line
        root_username="${line:-postgres}"
    fi
fi

echo ""
echo "Configuration parameters:"
echo ""
echo "  country and language: $LANGUAGE"
echo "  time zone:            $TIMEZONE"
echo "  database engine:      $DB_ENGINE ($DJANGO_ENGINE)"
echo "  database name:        $DB_NAME"
echo "  database host:        ${DB_HOST:-localhost}"
echo "  database port:        ${DB_PORT:-(default)}"
echo "  database username:    $DB_USERNAME"
echo "  database password:    $DB_PASSWORD"
echo ""
echo "We are about to generate a new Django configuration and to create a new"
echo "database. This will destroy your previous configuration and make you lose"
echo "all you data. Make sure all parameters are correct before proceeding."
echo ""
echo -n "Please, type YES if you want to preceed or ABORT to exit now: "

line=""
while [ -z "$line" ] ; do
    read line
    if [ "$line" = "ABORT" ] ; then exit 0 ; fi
    if [ "$line" != "YES" ] ; then line="" ; fi
done

echo ""

if [ "$DB_ENGINE" = "sqlite3" ] ; then
    echo -n "Creating database $DB_NAME ... "
    rm -f $DB_NAME
    echo "done"
fi

if [ "$DB_ENGINE" = "mysql" -a -n "$exe_mysql" ] ; then
    echo -n "Creating database $DB_NAME ... "
    mysql --batch --host=${DB_HOST:-localhost} --port=${DB_PORT:-0} --user=$root_username --password=$root_password mysql <<EOF
    CREATE DATABASE IF NOT EXISTS $DB_NAME ;
    INSERT INTO user VALUES ('%', '$DB_USERNAME', PASSWORD('$DB_PASSWORD'),
        'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y',
        'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y',
        '','','','',0,0,0,0)
           ON DUPLICATE KEY UPDATE User = '$DB_USERNAME' ;
    FLUSH PRIVILEGES ;
    GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USERNAME ;
    echo "done"
EOF
fi

if [ "$DB_ENGINE" = "postgresql" -a -n "$exe_psql" ] ; then
    echo "Creating database $DB_NAME ... "
    args="--username=$root_username template1"
    if [ -n "$DB_PORT" ] ; then
        args="--port=$DB_PORT $args"
    fi
    if [ -n "$DB_HOST" ] ; then
        args="--host=$DB_HOST $args"
    fi
    psql -q $args <<EOF
DROP DATABASE IF EXISTS $DB_NAME ;
DROP USER IF EXISTS $DB_USERNAME ;
CREATE USER $DB_USERNAME WITH ENCRYPTED PASSWORD '$DB_PASSWORD' ;
CREATE DATABASE $DB_NAME WITH OWNER = $DB_USERNAME ;
EOF
    echo "PostgreSQL setup complete"
fi

echo ""
echo -n "Generating settings.py ... "

cat local_settings.py.in \
    | sed -e "s/@DB_ENGINE@/django.db.backends.$DJANGO_ENGINE/g" \
    | sed -e "s/@DB_NAME@/$DB_NAME/g" \
    | sed -e "s/@DB_HOST@/$DB_HOST/g" \
    | sed -e "s/@DB_PORT@/$DB_PORT/g" \
    | sed -e "s/@DB_USERNAME@/$DB_USERNAME/g" \
    | sed -e "s/@DB_PASSWORD@/$DB_PASSWORD/g" \
    | sed -e "s/@LANGUAGE@/$LANGUAGE/g" \
    | sed -e "s/@COUNTRY@/$COUNTRY/g" \
    | sed -e "s%@TIMEZONE@%$TIMEZONE%g" \
    > local_settings.py

echo "done"
echo ""
echo "Initializing Django database and loading default surveys:"
echo ""

python manage.py syncdb
# On PostgreSQL ovverride the order of migrated tables creating first
# referenced tables (journal migration fails if CMS isn't available.)
python manage.py migrate cms
python manage.py migrate
python manage.py rule_type_register --title 'Show Question' --jsclass 'wok.pollster.rules.ShowQuestion'
python manage.py rule_type_register --title 'Hide Question' --jsclass 'wok.pollster.rules.HideQuestion'
python manage.py rule_type_register --title 'Show Options' --jsclass 'wok.pollster.rules.ShowOptions'
python manage.py rule_type_register --title 'Hide Options' --jsclass 'wok.pollster.rules.HideOptions'
python manage.py rule_type_register --title 'Check Options' --jsclass 'wok.pollster.rules.CheckOptions'
python manage.py rule_type_register --title 'Uncheck Options' --jsclass 'wok.pollster.rules.UncheckOptions'
python manage.py rule_type_register --title 'Exclusive' --jsclass 'wok.pollster.rules.Exclusive'
python manage.py rule_type_register --title 'Future Fill' --jsclass 'wok.pollster.rules.FutureFill'
python manage.py rule_type_register --title 'Future Show Question' --jsclass 'wok.pollster.rules.FutureShowQuestion'
python manage.py rule_type_register --title 'Future Hide Question' --jsclass 'wok.pollster.rules.FutureHideQuestion'
python manage.py rule_type_register --title 'Future Show Options' --jsclass 'wok.pollster.rules.FutureShowOptions'
python manage.py rule_type_register --title 'Future Hide Options' --jsclass 'wok.pollster.rules.FutureHideOptions'
python manage.py rule_type_register --title 'Fill' --jsclass 'wok.pollster.rules.Fill'
python manage.py question_data_type_register --title 'Text' --dbtype 'django.db.models.TextField(null=True, blank=True)' --cssclass 'text-type' --jsclass 'wok.pollster.datatypes.Text'
python manage.py question_data_type_register --title 'Numeric' --dbtype 'django.db.models.PositiveIntegerField(null=True, blank=True)' --cssclass 'numeric-type' --jsclass 'wok.pollster.datatypes.Numeric'
python manage.py question_data_type_register --title 'Date' --dbtype 'django.db.models.DateField(null=True, blank=True)' --cssclass 'date-type' --jsclass 'wok.pollster.datatypes.Date'
python manage.py question_data_type_register --title 'YearMonth' --dbtype 'db.models.YearMonthField(null=True, blank=True)' --cssclass 'monthyear-type' --jsclass 'wok.pollster.datatypes.YearMonth'
python manage.py question_data_type_register --title 'Timestamp' --dbtype 'django.db.models.DateTimeField(null=True, blank=True)' --cssclass 'timestamp-type' --jsclass 'wok.pollster.datatypes.Timestamp'
# PostalCode is added by the pollster migration 0005_postalcodefield.py
# python manage.py question_data_type_register --title 'PostalCode' --dbtype 'django.db.models.PostalCodeField(null=True, blank=True)' --cssclass 'postalcode-type' --jsclass 'wok.pollster.datatypes.PostalCode'
python manage.py virtual_option_type_register --title 'Range' --question-data-type-title 'Text' --jsclass 'wok.pollster.virtualoptions.TextRange'
python manage.py virtual_option_type_register --title 'Range' --question-data-type-title 'Numeric' --jsclass 'wok.pollster.virtualoptions.NumericRange'
python manage.py virtual_option_type_register --title 'Range' --question-data-type-title 'Date' --jsclass 'wok.pollster.virtualoptions.DateRange'
python manage.py virtual_option_type_register --title 'Years ago' --question-data-type-title 'Date' --jsclass 'wok.pollster.virtualoptions.DateYearsAgo'
python manage.py virtual_option_type_register --title 'Years ago' --question-data-type-title 'YearMonth' --jsclass 'wok.pollster.virtualoptions.YearMonthYearsAgo'
python manage.py virtual_option_type_register --title 'Weeks ago' --question-data-type-title 'Timestamp' --jsclass 'wok.pollster.virtualoptions.TimestampWeeksAgo'
python manage.py virtual_option_type_register --title 'Regular expression' --question-data-type-title 'Text' --jsclass 'wok.pollster.virtualoptions.RegularExpression'

python manage.py createcachetable django_cache 2>/dev/null || echo 'Cache table errors ignored'

if [ "$DB_ENGINE" = "postgresql" -a -n "$exe_psql" ] ; then
    postgis=$(ls /usr/share/postgresql/*/contrib/postgis-*/postgis.sql)
    srefsys=$(ls /usr/share/postgresql/*/contrib/postgis-*/spatial_ref_sys.sql)
    if [ -n "$postgis" -a -n "$srefsys" ] ; then
        echo "Setting up PostGIS"
        args="--username=$root_username $DB_NAME"
        if [ -n "$DB_PORT" ] ; then
            args="--port=$DB_PORT $args"
        fi
        if [ -n "$DB_HOST" ] ; then
            args="--host=$DB_HOST $args"
        fi
        psql -q $args <<EOF
\i $postgis
\i $srefsys
CREATE TABLE pollster_zip_codes (id serial, country TEXT, zip_code_key TEXT);
SELECT AddGeometryColumn('pollster_zip_codes', 'geometry', 4326, 'MULTIPOLYGON', 2);
ALTER TABLE pollster_zip_codes OWNER TO $DB_USERNAME;
ALTER TABLE spatial_ref_sys OWNER TO $DB_USERNAME;
ALTER TABLE geometry_columns OWNER TO $DB_USERNAME;
ALTER VIEW geography_columns OWNER TO $DB_USERNAME;
EOF
        echo "PostGIS setup complete"
    fi
fi


echo ""
echo "** All done. You can start the system by issuing: 'source ./bin/activate && python manage.py runserver'"
echo ""
