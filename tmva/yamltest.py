from utils import read_yaml, make_paths, path2rootdir
from pprint import pprint
d = read_yaml('dsk_train_out.yaml')
allp = make_paths(d)
pprint(allp)

from ROOT import TFile

dirs = []
for path in allp:
    rfile, rdir = path2rootdir(path['path'])
    dirs.append(rdir)

print dirs
# for d in dirs:
#     d.ls()

# t = path2rootdir('dsk_train_out.root')
