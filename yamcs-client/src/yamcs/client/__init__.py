from yamcs import clientversion  # noqa
from yamcs.archive.client import *  # noqa
from yamcs.archive.model import *  # noqa
from yamcs.client.activities import *  # noqa
from yamcs.client.core import *  # noqa
from yamcs.core import GLOBAL_INSTANCE  # noqa
from yamcs.core.auth import *  # noqa
from yamcs.core.context import *  # noqa
from yamcs.core.exceptions import *  # noqa
from yamcs.core.futures import *  # noqa
from yamcs.core.helpers import *  # noqa
from yamcs.core.pagination import *  # noqa
from yamcs.core.subscriptions import *  # noqa
from yamcs.filetransfer.client import *  # noqa
from yamcs.filetransfer.model import *  # noqa
from yamcs.link.client import *  # noqa
from yamcs.link.model import *  # noqa
from yamcs.mdb.client import *  # noqa
from yamcs.mdb.model import *  # noqa
from yamcs.model import *  # noqa
from yamcs.storage.client import *  # noqa
from yamcs.storage.model import *  # noqa
from yamcs.tco.client import *  # noqa
from yamcs.tco.model import *  # noqa
from yamcs.timeline.client import *  # noqa
from yamcs.timeline.model import *  # noqa
from yamcs.tmtc.client import *  # noqa
from yamcs.tmtc.model import *  # noqa

"""
Migration in process:

All files should eventually be available from within yamcs.client package,
following a lengthy deprecation process.

(excluding protobuf classes, which we could move elsewhere).

As a first step, we make everything directly available from yamcs.client.
(next step will be to update the examples)
"""
