_pad        = '_'
_eos        = '~'
_sos        = '^'
_special = "!'(),-.:;? "
Ko_ARPAbet = ['a', 'ae', 'b', 'b2', 'bb', 'ch', 'd', 'd2', 'dd', 'e', 'eo', 'eu',
                 'g', 'g2', 'gg', 'h', 'i', 'j', 'jj', 'kh', 'l', 'l2', 'm', 'm2',
                 'n', 'n2', 'ng', 'o', 'oe', 'p', 's', 'ss', 't', 'u', 'ui',
                 'wa', 'wae', 'we', 'wi', 'wo', 'ya', 'yae', 'ye', 'yeo', 'yo', 'yu']

phoneme_symbols = [_pad, _eos] + list(_special) + Ko_ARPAbet + [_sos]
