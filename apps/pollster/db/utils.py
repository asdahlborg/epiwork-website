def get_db_type(connection):
    db = None
    if connection.settings_dict['ENGINE'] == "django.db.backends.sqlite3":
        db = "sqlite"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.postgresql":
        db = "postgresql"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.postgresql_psycopg2":
        db = "postgresql"
    elif connection.settings_dict['ENGINE'] == "django.db.backends.mysql":
        db = "mysql"
    return db

def convert_query_paramstyle(connection, sql, params):
    db = get_db_type(connection)
    if db == 'postgresql':
        return sql
    translations = dict([(p, ':'+p) for p in params.keys()])
    converted = sql % translations
    return converted
