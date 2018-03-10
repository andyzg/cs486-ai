import numpy as np


def remove_field_name(a, names):
    """Removes a field name of a structuredarray `a`."""
    if type(names) == str:
        names = [names]
    new_names = list(a.dtype.names)
    for n in names:
        if n in new_names:
            new_names.remove(n)
    b = a[new_names]
    return b


def to_structured_array(a, names):
    return np.core.records.fromarrays(a.transpose(),
                                      names=names)


def unique(l):
    output = set()
    for x in l:
        output.add(x)
    return list(output)


def print_factors(factorList):
    for f in factorList:
        print f.dtype.names, f.view((float, len(f.dtype.names)))


def restrict(factor, variable, value):
    """Factor out rows where variable is not value, and then remove variable column.

    factor is a structuredarray
    """
    if variable not in factor.dtype.names:
        return factor
    indices = np.where(factor[variable] != value)
    result = np.delete(factor, indices, axis=0)  # Delete rows
    return remove_field_name(result, variable)


def multiply(factor1, factor2):
    names = set(factor1.dtype.names).intersection(set(factor2.dtype.names))
    names.remove('val')  # Don't need 'val'

    # Let's assume that names is only 1 value now
    col = list(names)[0]
    vals = unique(factor2[col])

    # Merge columns
    f1_names = list(factor1.dtype.names)
    f2_names = list(factor2.dtype.names)
    f1_names.remove(col)
    f1_names.remove('val')
    f2_names.remove(col)
    f2_names.remove('val')
    new_col = f1_names + [col] + f2_names + ['val']

    temp1 = remove_field_name(factor1, col)
    temp2 = remove_field_name(factor2, col)

    rows = []
    for v in vals:
        row1 = np.where(factor1[col] == v)[0]
        row2 = np.where(factor2[col] == v)[0]

        for i in row1:
            for j in row2:
                t1 = list(temp1[i])
                t2 = list(temp2[j])
                # Each permutation for each column where col == v
                rows.append(t1[0:-1] + [v] + t2[0:-1] + [t1[-1] * t2[-1]])

    result = to_structured_array(np.array(rows), new_col)
    return result


def sumout(factor, variable):
    f = remove_field_name(factor, ['val', variable])
    u, indices = np.unique(f, return_inverse=True, axis=0)
    indices = np.array(indices)

    rows = []
    for i in range(0, len(u)):
        row = list(u[i]) + [0]
        for j in np.where(indices == i)[0]:
            row[-1] += factor[j][-1]
        rows.append(row)

    # Get new column names
    new_cols = list(factor.dtype.names)
    new_cols.remove(variable)

    return to_structured_array(np.array(rows), new_cols)


def normalize(factor):
    s = np.sum(factor['val'])
    factor['val'] /= s
    return factor


def inference(factorList, queryVariables, orderedListOfHiddenVariables, evidenceList):
    """
    evidenceList: dict where key is variable name and value is the value.
    """
    for var in evidenceList:
        for i, factor in enumerate(factorList):
            factorList[i] = restrict(factor, var, evidenceList[var])

    for var in orderedListOfHiddenVariables:
        to_multiply = []
        for i, factor in reversed(list(enumerate(factorList))):
            if var in factor.dtype.names:
                f = factorList.pop(i)
                to_multiply.append(f)

        product = to_multiply[0]
        for i in range(1, len(to_multiply)):
            product = multiply(product, to_multiply[i])

        f = sumout(product, var)
        factorList.append(f)

    print_factors(factorList)
    product = factorList[0]
    for i in range(1, len(factorList)):
        product = multiply(product, factorList[i])

    return normalize(product)


# Test restrict
a = np.array([[1,1,1,.1],
             [1,1,0,.9],
             [1,0,1,.2],
             [1,0,0,.8],
             [0,1,1,.4],
             [0,1,0,.6],
             [0,0,1,.3],
             [0,0,0,.7]])
# print(restrict(to_structured_array(a, 'x,y,z,val'), 'x', 1))

f1 = np.array([[1,1,.1],
               [1,0,.9],
               [0,1,.2],
               [0,0,.8]])

f2 = np.array([[1,1,.3],
               [1,0,.7],
               [0,1,.6],
               [0,0,.4]])
# print(multiply(to_structured_array(f1, 'a,b,val'), to_structured_array(f2, 'b,c,val')).dtype)

s = np.array([[1,1,1,.03],
             [1,1,0,.07],
             [1,0,1,.54],
             [1,0,0,.36],
             [0,1,1,.06],
             [0,1,0,.14],
             [0,0,1,.48],
             [0,0,0,.32]])
# print(sumout(to_structured_array(s, 'a,b,c,val'), 'b'))
# print(normalize(to_structured_array(f1, 'a,b,val')))

M = to_structured_array(np.array([[0,.92], [1,.08]]), 'malfunction,val')

C = to_structured_array(np.array([[0,.68], [1,.32]]), 'cancer,val')

ta = to_structured_array(np.array([[1,1,.8], [1,0,.2], [0,1,.15], [0,0,.85]]), 'cancer,test a,val')


tb = to_structured_array(np.array([[1,1,1,.61],
                         [1,1,0,.39],
                         [1,0,1,.52],
                         [1,0,0,.48],
                         [0,1,1,.78],
                         [0,1,0,.22],
                         [0,0,1,.044],
                         [0,0,0,.956]]), 'malfunction,cancer,test b,val')

r = to_structured_array(np.array([[1,1,.98], [1,0,.02], [0,1,.01], [0,0,.99]]), 'test b,report,val')

d = to_structured_array(np.array([[1,1,.96],
                        [1,0,.04],
                        [0,1,.001],
                        [0,0,.999]]), 'report,database,val')


factorList = [M, C, ta, tb, r, d]
print(inference(factorList, 'database', ['cancer', 'malfunction', 'test a', 'test b', 'report'], {}))
