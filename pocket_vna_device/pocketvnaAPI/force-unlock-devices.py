from __future__ import print_function

import errno, sys
import pocketvna

## Api uses semaphore to limit number of simultaneous connection to a single device
## in case of crash or kill signal on linux (and on elder Windows) semaphore remains locked
## to force unlock using pocketvna_force_unlock_devices is required

try:
    pocketvna.force_unlock()

finally:
	pocketvna.close_api()


