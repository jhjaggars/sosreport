import os

def walk(p):
    for path, dir_list, file_list in os.walk(p):
        abspath = os.path.abspath(path)
        for f in file_list:
            yield f
        for d in dir_list:
            dpath = os.path.join(path, d)
            if os.path.islink(dpath):
                linkpath = os.path.abspath(os.readlink(dpath))
                print abspath, linkpath
                if abspath not in linkpath:
                    print "walking", linkpath
                    for f in walk(linkpath):
                        yield f
