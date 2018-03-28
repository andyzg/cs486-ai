import numpy as np


def fields_view(array, fields):
    return array.getfield(np.dtype(
        {name: array.dtype.fields[name] for name in fields}
    ))


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
        print(f.dtype.names, f.view((float, len(f.dtype.names))))


def restrict(factor, variable, value):
    """Factor out rows where variable is not value, and then remove variable column.

    factor is a structuredarray
    """
    if variable not in factor.dtype.names:
        return factor
    indices = np.where(factor[variable] != value)
    result = np.delete(factor, indices, axis=0)  # Delete rows
    temp = remove_field_name(result, variable)
    return to_structured_array(np.array(temp.tolist()), ','.join(temp.dtype.names))


def multiply(factor1, factor2):
    if len(factor1.dtype.names) == 1:
        factor2['val'] *= factor1[factor1.dtype.names[0]][0]
        return factor2
    elif len(factor2.dtype.names) == 1:
        factor1['val'] *= factor2[factor2.dtype.names[0]][0]
        return factor1

    names = set(factor1.dtype.names).intersection(set(factor2.dtype.names))
    names.remove('val')  # Don't need 'val'

    # Let's assume that names is only 1 value now
    col = list(names)
    vals = fields_view(factor2, list(col))

    # Merge columns
    f1_names = list(factor1.dtype.names)
    f2_names = list(factor2.dtype.names)
    for name in col:
        f1_names.remove(name)
        f2_names.remove(name)
    f1_names.remove('val')
    f2_names.remove('val')
    new_col = f1_names + col + f2_names + ['val']

    temp1 = factor1
    temp2 = factor2
    for name in col:
        temp1 = remove_field_name(temp1, name)
        temp2 = remove_field_name(temp2, name)

    rows = []
    for v in vals:
        row1 = []
        row2 = []
        for i, c in enumerate(col):
            row1.append(np.array(np.where(factor1[c] == v[i])[0]))
            row2.append(np.array(np.where(factor2[c] == v[i])[0]))
        row1 = reduce(np.intersect1d, np.array(row1))
        row2 = reduce(np.intersect1d, np.array(row2))

        for i in row1:
            for j in row2:
                t1 = list(temp1[i])
                t2 = list(temp2[j])
                # Each permutation for each column where col == v
                rows.append(t1[0:-1] + list(v) + t2[0:-1] + [t1[-1] * t2[-1]])

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

    # print_factors(factorList)

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

    # print_factors(factorList)
    product = factorList[0]
    for i in range(1, len(factorList)):
        product = multiply(product, factorList[i])

    return normalize(product)
