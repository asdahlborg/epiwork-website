#!/bin/bash
#
# Bootstraps everything installing Django and all required eggs, configuring
# the database and making sure a consistent Mono development environment is
# installed.

python bootstrap.py && ./bin/buildout

# Here we customize src/epiweb/settings.py by setting the user preferred
# database, language and country. Note that the database and the user used
# to connect should already exist.

DB_ENGINE=""
DB_NAME=""
DB_HOST=""
DB_PORT=""
DB_USERNAME=""
DB_USERNAME=""
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

echo -n "Checking for pre-requisites: mysql ...  "
exe_mysql="$(which mysql)"
if [ -n "$exe_mysql" ] ; then
    echo "$exe_mysql"
else
    echo "not found; automatic MySQL configuration disabled"
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
    echo -n "Please, choose a database engine (sqlite3, the default or mysql): "
    read line
    DB_ENGINE="${line:-sqlite3}"
    if [ "$DB_ENGINE" != "sqlite3" -a "$DB_ENGINE" != "mysql" ] ; then
        DB_ENGINE=""
    fi
done

if [ "$DB_ENGINE" = "sqlite3" ] ; then
    DB_NAME="ggm.db"
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

echo ""
echo "Configuration parameters:"
echo ""
echo "  country and language: $LANGUAGE"
echo "  time zone:            $TIMEZONE"
echo "  database engine:      $DB_ENGINE"
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
echo -n "Creating database $DB_NAME ... "

if [ "$DB_ENGINE" = "sqlite3" ] ; then
    rm -f $DB_NAME
fi

if [ "$DB_ENGINE" != "sqlite3" -a -n "$exe_mysql" ] ; then
    mysql --batch --host=${DB_HOST:-localhost} --port=${DB_PORT:-0} --user=$root_username --password=$root_password mysql <<EOF
    CREATE DATABASE IF NOT EXISTS $DB_NAME ;
    INSERT INTO user VALUES ('%', '$DB_USERNAME', PASSWORD('$DB_PASSWORD'),
        'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y',
        'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y',
        '','','','',0,0,0,0)
           ON DUPLICATE KEY UPDATE User = '$DB_USERNAME' ;
    FLUSH PRIVILEGES ;
    GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USERNAME ;
EOF
fi

echo "done"
echo -n "Generating settings.py ... "

cat src/epiweb/settings.py.in \
    | sed -e "s/@DB_ENGINE@/$DB_ENGINE/g" \
    | sed -e "s/@DB_NAME@/$DB_NAME/g" \
    | sed -e "s/@DB_HOST@/$DB_HOST/g" \
    | sed -e "s/@DB_PORT@/$DB_PORT/g" \
    | sed -e "s/@DB_USERNAME@/$DB_USERNAME/g" \
    | sed -e "s/@DB_PASSWORD@/$DB_PASSWORD/g" \
    | sed -e "s/@LANGUAGE@/$LANGUAGE/g" \
    | sed -e "s/@COUNTRY@/$COUNTRY/g" \
    | sed -e "s%@TIMEZONE@%$TIMEZONE%g" \
    > src/epiweb/settings.py

echo "done"
echo ""
echo "Initializing Django database and loading default surveys:"
echo ""

./bin/django syncdb
./bin/django loaddata data/initial.json 
./bin/django survey_register data/surveys/gsq/gold-standard-weekly.py 
./bin/django survey_register data/surveys/gsq/gold-standard-intake.py 
./bin/django survey_register data/surveys/gsq/gold-standard-contact.py
./bin/django rule_type_register --title 'Show Question' --jsclass 'wok.pollster.rules.ShowQuestion'
./bin/django rule_type_register --title 'Hide Question' --jsclass 'wok.pollster.rules.HideQuestion'
./bin/django rule_type_register --title 'Show Options' --jsclass 'wok.pollster.rules.ShowOptions'
./bin/django rule_type_register --title 'Hide Options' --jsclass 'wok.pollster.rules.HideOptions'
./bin/django rule_type_register --title 'Check Options' --jsclass 'wok.pollster.rules.CheckOptions'
./bin/django rule_type_register --title 'Uncheck Options' --jsclass 'wok.pollster.rules.UncheckOptions'
./bin/django rule_type_register --title 'Exclusive' --jsclass 'wok.pollster.rules.Exclusive'
./bin/django question_data_type_register --title 'Text' --dbtype 'django.db.models.TextField(null=True, blank=True)' --cssclass 'text-type' --jsclass 'wok.pollster.datatypes.Text'
./bin/django question_data_type_register --title 'Numeric' --dbtype 'django.db.models.PositiveIntegerField(null=True, blank=True)' --cssclass 'numeric-type' --jsclass 'wok.pollster.datatypes.Numeric'
./bin/django question_data_type_register --title 'Date' --dbtype 'django.db.models.DateField(null=True, blank=True)' --cssclass 'date-type' --jsclass 'wok.pollster.datatypes.Date'
./bin/django question_data_type_register --title 'MonthYear' --dbtype 'django.db.models.CharField(max_length=255, null=True, blank=True)' --cssclass 'monthyear-type' --jsclass 'wok.pollster.datatypes.MonthYear'
./bin/django question_data_type_register --title 'Timestamp' --dbtype 'django.db.models.DateTimeField(null=True, blank=True)' --cssclass 'timestamp-type' --jsclass 'wok.pollster.datatypes.Timestamp'
./bin/django virtual_option_type_register --title 'Range' --question-data-type-title 'Text' --jsclass 'wok.pollster.virtualoptions.TextRange'
./bin/django virtual_option_type_register --title 'Range' --question-data-type-title 'Numeric' --jsclass 'wok.pollster.virtualoptions.NumericRange'
./bin/django virtual_option_type_register --title 'Range' --question-data-type-title 'Date' --jsclass 'wok.pollster.virtualoptions.DateRange'
./bin/django virtual_option_type_register --title 'Years ago' --question-data-type-title 'Date' --jsclass 'wok.pollster.virtualoptions.DateYearsAgo'
./bin/django virtual_option_type_register --title 'Years ago' --question-data-type-title 'MonthYear' --jsclass 'wok.pollster.virtualoptions.MonthYearYearsAgo'
./bin/django virtual_option_type_register --title 'Regular expression' --question-data-type-title 'Text' --jsclass 'wok.pollster.virtualoptions.RegularExpression'

if [ "$DB_ENGINE" = "sqlite3" ] ; then
    echo ".read src/extra-survey.sqlite3.sql" | sqlite3 ggm.db
fi

echo ""
echo "** All done. You can start the system by issuing: ./bin/django runserver"
echo ""
