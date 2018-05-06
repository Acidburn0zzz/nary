# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import inary.db
import inary.operations
import inary.blacklist
import inary.context as ctx

def list_needs_restart():
    """
    Return a list of packages that need a service restart.
    """
    return inary.db.installdb.InstallDB().list_needs_restart()

def list_needs_reboot():
    """
    Return a list of packages that need a system reboot.
    """
    return inary.db.installdb.InstallDB().list_needs_reboot()

def add_needs_restart(package):
    """
    Add a new package to service restart list.
    """
    inary.db.installdb.InstallDB().mark_needs_restart(package)

def add_needs_reboot(package):
    """
    Add a new package to system reboot list.
    """
    inary.db.installdb.InstallDB().mark_needs_reboot(package)

def remove_needs_restart(package):
    """
    Remove a package from service restart list. Passing "*" will clear whole list.
    """
    inary.db.installdb.InstallDB().clear_needs_restart(package)

def remove_needs_reboot(package):
    """
    Remove a package from system reboot list. Passing "*" will clear whole list.
    """
    inary.db.installdb.InstallDB().clear_needs_reboot(package)

def list_pending():
    """
    Return a list of configuration pending packages -> list_of_strings
    """
    return inary.db.installdb.InstallDB().list_pending()

def list_installed():
    """
    Return a list of installed packages -> list_of_strings
    """
    return inary.db.installdb.InstallDB().list_installed()

def list_obsoleted(repo=None):
    """
    Return a list of obsoleted packages -> list_of_strings
    @param repo: Repository of the obsoleted packages. If repo is None than returns
    a list of all the obsoleted packages in all the repositories
    """
    return inary.db.packagedb.PackageDB().get_obsoletes(repo)

def list_replaces(repo=None):
    """
    Return a dictionary of the replaced packages in the given repository
    @param repo: Repository of the replaced packages. If repo is None than returns
    a dictionary of all the replaced packages in all the repositories

    {'gaim':['pidgin'], 'gimp-i18n':['gimp-i18n-tr', 'gimp-18n-de', ...]}

    gaim replaced by pidgin and gimp-i18n is divided into smaller packages which also
    replaces gimp-i18n
    """
    return inary.db.packagedb.PackageDB().get_replaces(repo)

def list_available(repo=None):
    """
    Return a list of available packages in the given repository -> list_of_strings
    @param repo: Repository of the packages. If repo is None than returns
    a list of all the available packages in all the repositories
    """
    return inary.db.packagedb.PackageDB().list_packages(repo)

def list_sources(repo=None):
    """
    Return a list of available source packages in the given repository -> list_of_strings
    @param repo: Repository of the source packages. If repo is None than returns
    a list of all the available source packages in all the repositories
    """
    return inary.db.sourcedb.SourceDB().list_sources(repo)

def list_newest(repo=None, since=None):
    """
    Return a list of newest packages in the given repository -> list_of_strings since
    last update or before.
    @param repo: Repository of the packages. If repo is None than returns a list of
    all the newest packages from all the repositories.
    @param since: yyyy-mm-dd formatted
    """
    return inary.db.packagedb.PackageDB().list_newest(repo, since)

def list_upgradable():
    """
    Return a list of packages that are upgraded in the repository -> list_of_strings
    """
    installdb = inary.db.installdb.InstallDB()
    is_upgradable = inary.operations.upgrade.is_upgradable

    upgradable = list(filter(is_upgradable, installdb.list_installed()))
    # replaced packages can not pass is_upgradable test, so we add them manually
    upgradable.extend(list_replaces())

    # consider also blacklist filtering
    upgradable = inary.blacklist.exclude_from(upgradable, ctx.const.blacklist)

    return upgradable

def list_repos(only_active=True):
    """
    Return a list of the repositories -> list_of_strings
    @param only_active: return only the active repos list -> list_of_strings
    """
    return inary.db.repodb.RepoDB().list_repos(only_active)
