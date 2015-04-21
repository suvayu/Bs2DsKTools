"""Common configurations"""

from collections import OrderedDict

classifiers = OrderedDict({
    # 'BDTA': 'BDT w/ adaptive boost',
    'BDTG': 'BDT w/ gradient boost',
    'BDTB': 'BDT w/ bagging'
})

transforms = OrderedDict({
    'identity' : 'Identity',
    'deco' : 'Decorrelate',
    'pca' : 'PCA',
    'uniform' : 'Uniform',
    'uniform_deco' : 'Uniform+Decorrelate',
    'gauss' : 'Gaussianise',
    'gauss_deco' : 'Gaussianise+Decorrelate',
})

sessions = OrderedDict({
    'test.root': 'test',
    'chitra_base/dsk_train_out.root': 'base',
    'chitra_less1a/dsk_train_out.root': 'base - Ds radial FD',
    'chitra_less1b/dsk_train_out.root': 'base - Bs radial FD',
    'chitra_less2/dsk_train_out.root': 'base - Bs & Ds radial FD',
    'chitra_less3/dsk_train_out.root': 'base - bach IP #chi^{2}',
    'chitra_less4/dsk_train_out.root': 'base - radial FD - bach IP #chi^{2}',
    'chitra_deco1/dsk_train_out.root': 'base + deco (all)',
    'chitra_deco2/dsk_train_out.root': 'base + 4 vars deco',
    'chitra_all/dsk_train_out.root': 'base + deco - 3 vars',
    'chitra_combi1/dsk_train_out.root': 'base + deco - Ds FD',
    'chitra_combi2/dsk_train_out.root': 'base + deco - bach IP #chi^{2}',
    'chitra_combi3/dsk_train_out.root': 'base + deco - B/D RFD',
    'chitra_log/dsk_train_out.root': 'base + deco + log(IP #chi^{2}/p_{T}) - RFD',
    'chitra_loga/dsk_train_out.root': 'base + log(IP #chi^{2}/p_{T})',
    'chitra_log3/dsk_train_out.root': 'base + deco + log(IP #chi^{2}) - RFD',
    'chitra_log3a/dsk_train_out.root': 'base + log(IP #chi^{2})',
    'chitra_max_diff/dsk_train_out.root': 'base + deco + log(IP #chi^{2}) + max p_{T} diff',
    'chitra_tune/dsk_train_out.root': 'BDT tuning',
})

varnames = [
    'lab0_DIRA_OWNPV',
    'lab0_IPCHI2_OWNPV',
    'lab1_IPCHI2_OWNPV',
    'lab1_PT',
    'lab2_MINIPCHI2',
    'lab3_IPCHI2_OWNPV',
    'lab4_IPCHI2_OWNPV',
    'lab5_IPCHI2_OWNPV',
    'lab0_VCHI2NDOF',
    'lab2_VCHI2NDOF',
    'lab0_RFD',
    'lab2_RFD',
    'lab1345_TRACK_GhostProb',
    'lab345_MIN_PT',
    'lab345_MIN_IPCHI2_OWNPV',
]
