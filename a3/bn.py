import numpy as np


def remove_field_name(a, name):
    """Removes a filed name of a structuredarray `a`."""
    names = list(a.dtype.names)
    if name in names:
        names.remove(name)
    b = a[names]
    return b


def to_structured_array(a, names):
    return np.core.records.fromarrays(a.transpose(),
                                      names=names)


def restrict(factor, variable, value):
    """Factor out rows where variable is not value, and then remove variable column.

    factor is a structuredarray
    """
    indices = np.where(factor[variable] != value)
    result = np.delete(factor, indices, axis=0)  # Delete rows
    return remove_field_name(result, variable)


def multiply(factor1, factor2):
    pass


def sumout(factor, variable):
    pass


def inference(factorList, queryVariables, orderedListOfHiddenVariables, evidenceList):
    pass


a = np.array([[1,1,1,.1],
             [1,1,0,.9],
             [1,0,1,.2],
             [1,0,0,.8],
             [0,1,1,.4],
             [0,1,0,.6],
             [0,0,1,.3],
             [0,0,0,.7]])

print(restrict(to_structured_array(a, 'x,y,z,val'), 'x', 1))
