import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv


def query():
    """
    Used for testing standard queries in SQL.
    """
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("""WITH year2016 as (
	SELECT prod, max(quant) max16, min(quant) min16
	FROM Sales
	WHERE year = 2016
	GROUP BY prod
), year2020 as (
	SELECT prod, max(quant) max20, min(quant) min20
	FROM Sales
	WHERE year = 2020
	GROUP BY prod
)
SELECT *
FROM year2016 NATURAL JOIN year2020 ORDER BY prod
""")

    return tabulate.tabulate(cur.fetchall(),
                             headers="keys", tablefmt="psql")


def main():
    print(query())


if "__main__" == __name__:
    main()
