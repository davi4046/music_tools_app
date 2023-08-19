def circ_add(lhs, rhs, rmin, rmax):
    result = lhs + rhs
    range = rmax - rmin
    while result >= rmax: result -= range
    while result < rmin: result += range
    return result

def circ_sub(lhs, rhs, rmin, rmax):
    result = lhs - rhs
    range = rmax - rmin
    while result >= rmax: result -= range
    while result < rmin: result += range
    return result
