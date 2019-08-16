# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

from . import *


def invalidate_caches():
    # Invalidates inary caches in use and forces to re-fill caches from disk when needed
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(), componentdb.ComponentDB(),
               installdb.InstallDB(), historydb.HistoryDB(), groupdb.GroupDB(), repodb.RepoDB()]:
        db.invalidate()


def flush_caches():
    # Invalidate and flush caches to re-generate them when needed
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(),
               componentdb.ComponentDB(), groupdb.GroupDB()]:
        db.invalidate()
        db.cache_flush()


def update_caches():
    # Updates ondisk caches
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(), componentdb.ComponentDB(),
               installdb.InstallDB(), groupdb.GroupDB()]:
        if db.is_initialized():
            db.cache_save()


def regenerate_caches():
    flush_caches()
    # Force cache regeneration
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(),
               componentdb.ComponentDB(), groupdb.GroupDB()]:
        db.cache_regenerate()
