import os
import sh

from Arrow import Arrow, VArrow


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
    print(ls_cat)
    print(len(ls_cat()))

    ls2 = (my_ls & my_ls) >> VArrow(sh.cat)
    print(ls2)
    print(len(ls2((1, "/"))))
