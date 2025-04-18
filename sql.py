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
    cur.execute("""WITH ny as (
    SELECT prod, avg(quant) ny_avg
    FROM Sales
    WHERE state = 'NY'
    GROUP BY prod
), nj as (
    SELECT prod, avg(quant) nj_avg
    FROM Sales
    WHERE state = 'NJ'
    GROUP BY prod
), ct as (
    SELECT prod, avg(quant) ct_avg
    FROM Sales
    WHERE state = 'CT'
    GROUP BY prod
)
SELECT prod, ny_avg, nj_avg, ct_avg
FROM ny natural join nj natural join ct WHERE ny_avg > nj_avg or ny_avg > ct_avg""")

    return tabulate.tabulate(cur.fetchall(),
                             headers="keys", tablefmt="psql")


def main():
    print(query())


if "__main__" == __name__:
    main()
