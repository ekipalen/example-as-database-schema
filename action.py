from robocorp.actions import action
import sqlite3


@action(is_consequential=False)
def get_db_schema_and_details(db_path: str) -> str:
    """
    Let's work with a database. Reads database schema and necessary information from local db file to understand the content, to enable creation of queries.

    Args:
        db_path (str): File name / path in string format. Example: "my_folder/my_db.db"

    Returns:
        str: Database details in string format to enable creating queries against the db.
    """

    def get_table_info(cursor, table_name):
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        return cursor.fetchall()

    def get_foreign_key_info(cursor, table_name):
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        return cursor.fetchall()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_info = "Here's the details. Print only like: I have read the schema etc..."

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        schema_info += f"\nTable: {table_name}\n"

        columns = get_table_info(cursor, table_name)
        primary_keys = [col[1] for col in columns if col[5] == 1]
        schema_info += "Primary Key(s): " + (", ".join(primary_keys) or "None") + "\n"
        schema_info += "Columns:\n"
        for column_info in columns:
            schema_info += f"  {column_info[1]} ({column_info[2]})\n"

        fk_info = get_foreign_key_info(cursor, table_name)
        if fk_info:
            schema_info += "Foreign Keys:\n"
            for fk in fk_info:
                schema_info += f"  {fk[3]} references {fk[2]}({fk[4]})\n"

    cursor.close()
    conn.close()
    return schema_info


@action(is_consequential=False)
def make_database_query(db_path: str, query: str) -> str:
    """
    Executes a database queries, requires you to have the schema. The function can handle both single-line and multi-line SQL queries.

    Args:
        db_path (str): The path to the SQLite database file.
            Example: "my_folder/my_db.db"
        query (str): The SQL query to be executed. It can be a single-line or
            multi-line string.
            Example:
                '''
                SELECT
                    Customer.Title AS CustomerTitle,
                    Customer.Name AS CustomerName
                FROM
                    Customer
                INNER JOIN
                    Account ON Customer.CustomerId = Account.CustomerId
                LIMIT 10;
                '''

    Returns:
        str: A string of the results.
    """

    def execute_query(db_path, query):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            result_str = "\t".join(columns) + "\n"
            for row in rows:
                row_str = "\t".join(map(str, row))
                result_str += row_str + "\n"

            return result_str

    result = execute_query(db_path, query)
    return result
