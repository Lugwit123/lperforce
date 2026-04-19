# -*- coding: utf-8 -*-

name = "lperforce"
version = "999.0"
description = "Lugwit Perforce Library - P4 integration utilities"
authors = ["Lugwit Team"]

requires = ["python-3.12+<3.13"]

def commands():
    env.PYTHONPATH.append('{root}/src')
    env.PYTHONPATH.append('{root}/src/lperforce/P4_API/Py311')
    env.LPERFORCE_ROOT = '{root}'

build_command = False
cachable = True
relocatable = True

