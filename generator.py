import subprocess
import os
import os.path

"""
    Things to note
    aggregates in F are defined with the following structure:
        {function}_{groupingVariable}_{attribute}
        ex. avg_1_quant == avg(1.quant)
"""
def setInputTest():
    S = ['cust', 'prod', 'avg_0_quant', 'max_0_quant']
    n = 0
    V = ['cust', 'prod']
    F = ['count_0_quant', 'sum_0_quant', 'avg_0_quant', 'max_0_quant']
    SVect = []
    G = ''
    return S, n, V, F, SVect, G

def getInput():
    mode = input("Select Input mode: (terminal or file): \n")
    match mode: 
  
        case 'terminal':
            # S list of projected attributes
            selectInput = input("Enter SELECT attributes seperated by commas (ex. cust, quant, price): \n")
            select = selectInput.split(", ")
        
            for i in select:  # check for empty inputs
                if i.strip() == "": 
                    raise Exception("!!!SOME INPUT IS EMPTY!!!")
            
            
            # n (check for int)
            numGroupVar = int(input("enter num of grouping variables (ex. 2): \n"))      
            
            
            # V list grouping attributes 
            groupAttrInput = input("enter grouping attributes seperated by commas (ex. cust, quant): \n")
            groupAttr = groupAttrInput.split(", ")
            
            for i in groupAttr: # check for empty inputs
                if i.strip() == "": 
                    raise Exception("!!!SOME INPUT IS EMPTY!!!")      
            
            
            # F list aggregate functions
            aggreFuncInput = input("enter aggregate functions seperated by commas (ex. sum_1_quant, sum_2_quant): \n")
            aggreFunc = aggreFuncInput.split(", ")
            
            for i in aggreFunc: # check for empty inputs
                if i.strip() == "": 
                    raise Exception("!!!SOME INPUT IS EMPTY!!!")      
            
            
            # sigma list grouping variables SUCH THAT (conditions) 
            predicateInput = input("enter predicates for grouping variables in python syntax seperated by commas (ex. month_1==1, month_2==2): \n")
            predicate = predicateInput.split(", ")
            
            # G HAVING Clause
            having = (input("enter having clause: "))
            
            if isinstance(having, str):
                print(having)
            else:
                print("Input not a string")
                
            # print (select, numGroupVar, groupAttr, aggreFunc, predicate, having) #DEBUG
            return select, numGroupVar, groupAttr, aggreFunc, predicate, having
            
        case 'file':
            # getting directory path
            dirPath = os.path.dirname(os.path.realpath(__file__))
            filename = input("enter a file name, the file must be in the same directory as generator.py, follow up filename with .txt (ex. otherfile.txt) ): \n")
            filePath = os.path.join(dirPath, filename)
    
            if os.path.isfile(filePath): # check if the filePath works, if so, access it and read contents

                file = open(filePath, "r")
                Phi = file.readlines()
                
                select = Phi[0].strip().split(", ")
                numGroupVar = Phi[1].strip()
                groupAttr = Phi[2].strip().split(", ")
                aggreFunc = Phi[3].strip().split(", ")
                predicate = Phi[4].strip().split(", ")
                having = Phi[5].strip()
                
                file.close()
            
            else:
                print("file not found")

            # print (select, numGroupVar, groupAttr, aggreFunc, predicate, having) #DEBUG
            return select, numGroupVar, groupAttr, aggreFunc, predicate, having
        
        # No input recognized
        case _:
            print("mode not recognized\n")

def stringArrayToCommaString(stringArray):
    # given a string array, returns a single string of each element in the same string separated by commas and spaces
    return ', '.join(stringArray)

def setStructFields(stringArray):
    # given a string array, returns a multiline string to set struct fields given input parameters
    out = ""
    for str in stringArray:
        out = out + f"self.{str} = {str}\n            "
    return out

def accountAvg(F):
    # given F input array, adds strings for count and sum if a group has avg aggregate and if not already included
    # ex. F = ['avg_1_quant'] >> outputs ['avg_1_quant', 'count_1_quant', 'sum_1_quant']
    # ex. F = ['avg_1_quant', 'count_1_quant'] >> outputs ['avg_1_quant', 'count_1_quant', 'sum_1_quant']
    # ex. F = ['avg_1_quant', 'avg_2_quant', 'max_1_quant'] >> outputs ['avg_1_quant', 'count_1_quant', 'sum_1_quant', 'avg_2_quant', 'count_2_quant', 'sum_2_quant', 'max_1_quant']
    # ex. F = ['max_1_quant'] >> outputs ['max_1_quant']
    return []


def matchGroupByString(V):
    # given group by variables array
    # generates a matching condition string in the form:
    # e.attrib == row['attrib'] and ...
    out = ""
    for i, attrib in enumerate(V):
        if i > 0:
            out = out + " and "
        out = out + f"e.{attrib} == row['{attrib}']"
    return out

def insertGroupCases(n, F):
    # given aggregate function array, and number of grouping variables
    # produces the cases for match that update the aggregates for each grouping variable
    FDecomp = map(lambda f: f.split('_'), F)
    # FDecomp splits f functions into [function, grouping, attrib]
    out = ""
    for i in range(n+1):
        out = out + f"""case {str(i)}:
                            """
        for fd in FDecomp:
            if int(fd[1]) != i:
                continue
            else:
                match fd[0]:
                    case 'count':
                        out = out + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(fd)} + 1
                            """
                    case 'sum':
                        out = out + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(fd)} + row['{fd[2]}']
                            """
                    case 'max':
                        out = out + f"""mf_struct[i].{'_'.join(fd)} = max(mf_struct[i].{'_'.join(fd)}, row['{fd[2]}'])
                            """
                    case 'min':
                        out = out + f"""mf_struct[i].{'_'.join(fd)} = row['{fd[2]}'] if mf_struct[i].{'_'.join(fd)} == 0 else min(mf_struct[i].{'_'.join(fd)}, row['{fd[2]}'])
                            """
                    case 'avg':
                        out = out + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(['sum'] + fd[1:])} + mf_struct[i].{'_'.join(['count'] + fd[1:])}
                            """
                    case _:
                        raise ValueError(f"Aggregate function not recognized: {fd[0]}")
    return out


def main():
    S, n, V, F, SVect, G = setInputTest()

    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    
    # mode = input("To test a relational algebra expression, enter input mode (terminal, file): ")

    body = f"""
    class struct:
        def __init__(self, {stringArrayToCommaString(V)}, {stringArrayToCommaString(F)}):
            {setStructFields(V)}{setStructFields(F)}

    # scan table to fill mf_struct
    mf_struct = []
    for row in cur:
        if next((i for i, e in enumerate(mf_struct) if {matchGroupByString(V)}), -1) != -1:
            continue
        else:
            mf_struct.append(struct({stringArrayToCommaString(map(lambda v: f"row['{v}']", V))}{', 0' * len(F)}))

    # start scanning to calculate aggregates
    for sc in range({n + 1}):
        for row in cur:
            for i, e in enumerate(mf_struct):
                # check if grouping variable is satisfied
                if {matchGroupByString(V)} and {'True'}: # true replaced with formatted such that clause for sc
                    # update aggregates
                    match sc:
                        {insertGroupCases(n, F)}
                else:
                    continue 

    # construct output in _global
    for e in mf_struct:
        _global.append([{stringArrayToCommaString(map(lambda s: f"e.{s}", S))}])
    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
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
    cur.execute("SELECT * FROM sales{" where year=2009"}")
    
    _global = []
    {body}
    
    return tabulate.tabulate(_global, headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])

#!!!!!!!!!!!!!!!Note, I added the where clause to line 99 because where clauses are not apart of the 6 input variables and therefore should happen before aggregating
# otherwise, we would need to ask for where clause and add it to each such that clause

if "__main__" == __name__:
    main()
