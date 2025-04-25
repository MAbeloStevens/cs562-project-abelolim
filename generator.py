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
    F = ['avg_0_quant', 'max_0_quant']
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
                numGroupVar = int(Phi[1].strip())
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

def accountAvg(F): # <- input array, F = aggregateList
    # should prepend the added count and sum strings so that they come before their respective avg string
    outputList = []
    
    for aggregate in F: # Main loop
        splitAggregate = aggregate.split("_")
        
        if splitAggregate[0] == "avg": # if aggr is AVG.
            countAggregate = "count_" + splitAggregate[1] + "_" + splitAggregate[2]
            sumAggregate = "sum_" + splitAggregate[1] + "_" + splitAggregate[2]
            if not (countAggregate in aggregate):
                outputList.append(countAggregate)
            if not (sumAggregate in aggregate):
                outputList.append(sumAggregate)
            outputList.append(aggregate)
        else: # if aggre is not avg
            outputList.append(aggregate)
    
    # Loop to rid of any repeating functions list(set())'s behavior flipped some values
    resList = []
    for aggr in outputList:
        if aggr not in resList:
            resList.append(aggr)
        
    return resList

def toE_replace(V,F,string):
    arr = V+F
    string = " "+string
    for col in arr:
        if "_" not in col:
            col = " "+col
            string=string.replace(col, " e."+ (col.strip()))
        else:
            string=string.replace(col, "e."+ (col.strip()))
    return string.strip()

def stringArrayToCommaString(stringArray):
    # given a string array, returns a single string of each element in the same string separated by commas and spaces
    return ', '.join(stringArray)

def setStructFields(stringArray):
    # given a string array, returns a multiline string to set struct fields given input parameters
    out = ""
    for str in stringArray:
        out = out + f"self.{str} = {str}\n            "
    return out

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

def insertSuchThatClauses(n, SVect):
    if n == 0 or len(SVect) == 0:
        return ""
    out = "and ("
    for i in range(1, n+1):
        if (i > 1):
            out = out + " or "
        out = out + f"(sc == {i} and {SVect[i-1]})"
    return out + ")"

def insertGroupCases(n, F):
    # given aggregate function array, and number of grouping variables
    # produces the cases for match that update the aggregates for each grouping variable
    FDecomp = list(map(lambda f: f.split('_'), F))
    # FDecomp splits f functions into [function, grouping, attrib]
    if(len(F) == 0):
        return ""
    out = "match sc:"
    for i in range(n+1):
        out = out + f"""
                        case {str(i)}:
                            """
        agg = ""
        for fd in FDecomp:
            if int(fd[1]) == i:
                match fd[0]:
                    case 'count':
                        agg = agg + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(fd)} + 1
                            """
                    case 'sum':
                        agg = agg + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(fd)} + row['{fd[2]}']
                            """
                    case 'max':
                        agg = agg + f"""mf_struct[i].{'_'.join(fd)} = max(mf_struct[i].{'_'.join(fd)}, row['{fd[2]}'])
                            """
                    case 'min':
                        agg = agg + f"""mf_struct[i].{'_'.join(fd)} = row['{fd[2]}'] if mf_struct[i].{'_'.join(fd)} == 0 else min(mf_struct[i].{'_'.join(fd)}, row['{fd[2]}'])
                            """
                    case 'avg':
                        agg = agg + f"""mf_struct[i].{'_'.join(fd)} = mf_struct[i].{'_'.join(['sum'] + fd[1:])} / mf_struct[i].{'_'.join(['count'] + fd[1:])}
                            """
                    case _:
                        raise ValueError(f"Aggregate function not recognized: {fd[0]}")
        if len(agg) == 0:
            agg = "pass"
        out = out + agg
    return out


def main():
    # get inputs
    S, n, V, F, SVect, G = getInput()
    # account for avg in F
    F = accountAvg(F)
    # reformat G to work for looping
    G = toE_replace(V, F, G)
    

    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    
    # mode = input("To test a relational algebra expression, enter input mode (terminal, file): ")

    body = f"""
    # get the table
    T = []
    for row in cur:
        if {"True" if len(W) == 0 else W}:
            T.append(row)
    
    # create structure for mf_struct
    class struct:
        def __init__(self, {stringArrayToCommaString(V)}, {stringArrayToCommaString(F)}):
            {setStructFields(V)}{setStructFields(F)}

    # scan table to fill mf_struct
    mf_struct = []
    for row in T:
        if next((i for i, e in enumerate(mf_struct) if {matchGroupByString(V)}), -1) != -1:
            continue
        else:
            mf_struct.append(struct({stringArrayToCommaString(map(lambda v: f"row['{v}']", V))}{', 0' * len(F)}))

    # start scanning to calculate aggregates
    for sc in range({n + 1}):
        for row in T:
            for i, e in enumerate(mf_struct):
                # check if grouping variable is satisfied
                if {matchGroupByString(V)}{insertSuchThatClauses(n, SVect)}:
                    # update aggregates
                    {insertGroupCases(n, F)}
                else:
                    continue 

    # construct output in _global with having in mind
    for e in mf_struct:
        if {"True" if len(G) == 0 else G}:
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
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}
    
    return tabulate.tabulate(_global, headers=[{stringArrayToCommaString(map(lambda s: f"'{s}'", S))}], tablefmt="psql")

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
