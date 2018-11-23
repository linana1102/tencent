# -*- coding: utf-8 -*-
import hashlib


def gen_id(li):
    st = ''.join(li)
    if isinstance(st, unicode):
        st = st.encode('utf-8')
    return hashlib.md5(st).hexdigest()