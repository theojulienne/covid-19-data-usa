#!/usr/bin/env python3

import json
import datetime
import math
from collections import defaultdict
import itertools
import os

if not os.path.exists('by_state'):
    os.makedirs('by_state')
