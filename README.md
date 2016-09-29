# Arrow

## Definitions

`f >> g`: `lambda x: g(f(x))`

`f + g`: `lambda x,y: (f(x), g(y))`

`f * 3`: `f + f + f`

`f & g`: `lambda x: (f(x), g(x))` or `split_arr >> (f + g)`

`[f]` or `~f`: `lambda l: map(f, l)`

## Laws
 
`(f >> g) >> h` = `f >> (g >> h)` / `(f + g) + h` = `f + (g + h)`

`(f0 + g0) >> (f1 + g1)` = `(f0 >> f1) + (g0 >> g1)`

`[f] >> [g]` = `[f >> g]`

`f * i` = `f + f * (i - 1)` / `f * 0` = `pass_arr`

`f & g` = `split_arr >> (f + g)`

## Example

```Python
from Arrow import Arrow, VArrow
import os, sh


@Arrow
def prepare():
    return enumerate(filter(os.path.exists, os.environ["PATH"].split(":")))


@VArrow
def my_ls(i, d):
    file_name = "bin_%d.txt" % i
    sh.ls("-l", d, _out=file_name)
    return file_name


if __name__ == '__main__':
    ls_cat = prepare >> [my_ls] >> VArrow(sh.cat)
    print(ls_cat())
```

