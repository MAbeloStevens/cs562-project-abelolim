
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales where year=2009")
    
    _global = []
    
    class struct:
        def __init__(self, cust, prod, count_0_quant, sum_0_quant, avg_0_quant, max_0_quant):
            self.cust = cust
            self.prod = prod
            self.count_0_quant = count_0_quant
            self.sum_0_quant = sum_0_quant
            self.avg_0_quant = avg_0_quant
            self.max_0_quant = max_0_quant
            

    # scan table to fill mf_struct
    mf_struct = []
    for row in cur:
        if next((i for i, e in enumerate(mf_struct) if e.cust == row['cust'] and e.prod == row['prod']), -1) != -1:
            continue
        else:
            mf_struct.append(struct(row['cust'], row['prod'], 0, 0, 0, 0))

    # start scanning to calculate aggregates
    for sc in range(1):
        for row in cur:
            for i, e in enumerate(mf_struct):
                # check if grouping variable is satisfied
                if e.cust == row['cust'] and e.prod == row['prod'] and True: # true replaced with formatted such that clause for sc
                    # update aggregates
                    match sc:
                        case 0:
                            mf_struct[i].count_0_quant = mf_struct[i].count_0_quant + 1
                            mf_struct[i].sum_0_quant = mf_struct[i].sum_0_quant + row['quant']
                            mf_struct[i].avg_0_quant = mf_struct[i].sum_0_quant + mf_struct[i].count_0_quant
                            mf_struct[i].max_0_quant = max(mf_struct[i].max_0_quant, row['quant'])
                            
                else:
                    continue 

    # construct output in _global
    for e in mf_struct:
        _global.append([e.cust, e.prod, e.avg_0_quant, e.max_0_quant])
    
    
    return tabulate.tabulate(_global, headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    