# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#


import inary
import inary.context as ctx
import unittest
from . import testcase

class FilesDBTestCase(testcase.TestCase):

    filesdb = inary.db.filesdb.FilesDB()

    def testHasFile(self):
        assert not self.filesdb.has_file("usr/bin/ethtool")
        inary.api.install(["ethtool"])
        assert self.filesdb.has_file("usr/bin/ethtool")
        inary.api.remove(["ethtool"])
        assert not self.filesdb.has_file("usr/bin/ethtool")

    def testGetFile(self):
        inary.api.install(["ethtool"])
        pkg, path = self.filesdb.get_file("usr/bin/ethtool")
        assert pkg == "ethtool"
        assert path == "usr/bin/ethtool"
        inary.api.remove(["ethtool"])
        assert not self.filesdb.has_file("usr/bin/ethtool")

    def testAddRemoveFiles(self):
        fileinfo1 = inary.data.files.FileInfo()
        fileinfo1.path = "etc/inary/inary.conf"
        fileinfo2 = inary.data.files.FileInfo()
        fileinfo2.path = "etc/inary/mirrors.conf"

        files = inary.data.files.Files()
        files.list.append(fileinfo1)
        files.list.append(fileinfo2)

        assert not self.filesdb.has_file("etc/inary/inary.conf")
        assert not self.filesdb.has_file("etc/inary/mirrors.conf")

        self.filesdb.add_files("inary", files)

        assert self.filesdb.has_file("etc/inary/inary.conf")
        assert self.filesdb.has_file("etc/inary/mirrors.conf")

        pkg, path = self.filesdb.get_file("etc/inary/inary.conf")
        assert pkg == "inary"

        # FIXME: inconsistency in filesdb.py add_remove and remove_remove parameters
        self.filesdb.remove_files(files.list)

        assert not self.filesdb.has_file("etc/inary/inary.conf")
        assert not self.filesdb.has_file("etc/inary/mirrors.conf")

    def testSearchFile(self):
        assert not self.filesdb.search_file("ethtool")
        inary.api.install(["ethtool"])
        found = self.filesdb.search_file("ethtool")
