#!/usr/bin/env python3

import sys

from cyber.python.cyber_py3 import cyber


cyber.init()

if not cyber.ok():
    print('Well, something went wrong.')
    sys.exit(1)

print("hello cyber!")
# Do your job here.
cyber.shutdown()