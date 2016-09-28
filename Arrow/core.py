def fix_marrow(arr):
    if isinstance(arr, list):
        return _MArrow(arr[0])
    else:
        return arr


class ArrowBase:
    def __rshift__(self, other):
        return _SArrow(self, fix_marrow(other))

    def __rrshift__(self, other):
        return _SArrow(fix_marrow(other), self)

    def __add__(self, other):
        return _PArrow(self, fix_marrow(other))

    def __mul__(self, times):
        if times == 0:
            return None
        elif times == 1:
            return self
        else:
            return self + self * (times - 1)

    def __invert__(self):
        return _MArrow(self)

    def __and__(self, other):
        return split_arr >> (self + fix_marrow(other))

    def __rand__(self, other):
        return split_arr >> (fix_marrow(other) + self)


class Arrow(ArrowBase):
    def __init__(self, func):
        self.func = func

    def __call__(self, *arg):
        return self.func(*arg)

    def __str__(self):
        return "%s" % self.func.__name__


class VArrow(Arrow):
    def __call__(self, args):
        return self.func(*args)


class CompoundArrow(ArrowBase):
    def __init__(self, left, right):
        self.left = left
        self.right = right

        # Associative: C(C(x, y), z) = C(x, C(y, z))
        if self.left.__class__ == self.__class__:
            self.right = self.__class__(self.left.right, self.right)
            self.left = self.left.left

    def __call__(self, arg):
        raise NotImplementedError


class _SArrow(CompoundArrow):
    def __str__(self):
        return "(%s >> %s)" % (self.left, self.right)

    def __call__(self, *arg):
        return self.right(self.left(*arg))


class _PArrow(CompoundArrow):
    def __str__(self):
        return "(%s + %s)" % (self.left, self.right)

    def __call__(self, arg):
        if not isinstance(arg, tuple):
            arg = list(arg)
        if len(arg) == 2:
            arg_left, arg_right = arg
            return [self.left(arg_left), self.right(arg_right)]
        else:
            arg_left, *arg_right = arg
            return [self.left(arg_left)] + self.right(arg_right)


class _MArrow(ArrowBase):
    def __init__(self, arr):
        self.arr = arr

    def __str__(self):
        return "[%s]" % self.arr

    def __call__(self, arg):
        return map(self.arr, arg)


def optimise(arr):
    """Rules:
    1. S(P(f0, g0), P(f1, g1)) = P(S(f0, f1), S(g0, g1))
       or: f0 + g0 >> f1 + g1 = (f0 >> f1) + (g0 >> g1)
    2. S(M(f), M(g)) = M(S(f, g))
       or: ~f >> ~g = ~(f>>g)
    """

    if isinstance(arr, Arrow):
        return arr

    if isinstance(arr, _SArrow):
        if isinstance(arr.left, _PArrow) and isinstance(arr.right, _PArrow):
            # Rule 1
            arr = _PArrow(_SArrow(arr.left.left, arr.right.left),
                          _SArrow(arr.left.right, arr.right.right))
        elif isinstance(arr.left, _MArrow) and isinstance(arr.right, _MArrow):
            # Rule 2
            arr = _MArrow(_SArrow(arr.left.arr, arr.right.arr))

    if isinstance(arr, CompoundArrow):
        arr.left = optimise(arr.left)
        arr.right = optimise(arr.right)
    elif isinstance(arr, _MArrow):
        arr.arr = optimise(arr.arr)
    return arr


@Arrow
def pass_arr(arg):
    return arg


@Arrow
def split_arr(arg):
    return arg, arg
