# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import re
import gzip

import inary
import inary.context as ctx
import inary.data.specfile as Specfile
import inary.db.lazydb as lazydb

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

try:
    import ciksemel
    parser = "ciksemel"
except: 
    import xml.dom.minidom as minidom
    parser = "minidom"

class SourceDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)

    def init(self):
        self.__source_nodes = {}
        self.__pkgstosrc = {}
        self.__revdeps = {}

        repodb = inary.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__source_nodes[repo], self.__pkgstosrc[repo] = self.__generate_sources(doc)
            self.__revdeps[repo] = self.__generate_revdeps(doc)

        self.sdb = inary.db.itembyrepo.ItemByRepo(self.__source_nodes, compressed=True)
        self.psdb = inary.db.itembyrepo.ItemByRepo(self.__pkgstosrc)
        self.rvdb = inary.db.itembyrepo.ItemByRepo(self.__revdeps)

    def __generate_sources(self, doc):
        sources = {}
        pkgstosrc = {}

        if parser=="ciksemel":
            for spec in doc.tags("SpecFile"):
                src_name = spec.getTag("Source").getTagData("Name")
                sources[src_name] = gzip.zlib.compress(spec.toString().encode('utf-8'))
                for package in spec.tags("Package"):
                    pkgstosrc[package.getTagData("Name")] = src_name

        else:
            for spec in doc.childNodes:
                if spec.nodeType == spec.ELEMENT_NODE and spec.tagName == "SpecFile":
                    src_name = spec.getElementsByTagName("Source")[0].getElementsByTagName("Name")[0].firstChild.data
                    sources[src_name] = gzip.zlib.compress(spec.toxml('utf-8'))
                    for package in spec.childNodes:
                        if package.nodeType == package.ELEMENT_NODE and package.tagName == "Package":
                            pkgstosrc[package.getElementsByTagName("Name")[0].firstChild.data] = src_name

        return sources, pkgstosrc

    def __generate_revdeps(self, doc):
        revdeps = {}

        if parser=="ciksemel":
            for spec in doc.tags("SpecFile"):
                name = spec.getTag("Source").getTagData("Name")
                deps = spec.getTag("Source").getTag("BuildDependencies")
                if deps:
                    for dep in deps.tags("Dependency"):
                        revdeps.setdefault(dep.firstChild().data(), set()).add((name, dep.toString()))
        else:
            for spec in doc.childNodes:
                if spec.nodeType == spec.ELEMENT_NODE and spec.tagName == "SpecFile":
                    source = spec.getElementsByTagName("Source")[0]
                    name = source.getElementsByTagName("Name")[0].firstChild.data
                    deps = source.getElementsByTagName("BuildDependencies")
                    if deps:
                        for sdep in deps:
                            for dep in sdep.childNodes:
                                if dep.nodeType == dep.ELEMENT_NODE and dep.tagName == "Dependency":
                                    revdeps.setdefault(dep.childNodes[0].data, set()).add((name, dep.toxml()))
        return revdeps

    def list_sources(self, repo=None):
        return self.sdb.get_item_keys(repo)

    def which_repo(self, name):
        return self.sdb.which_repo(self.pkgtosrc(name))

    def which_source_repo(self, name):
        source = self.pkgtosrc(name)
        return source, self.sdb.which_repo(source)

    def has_spec(self, name, repo=None):
        return self.sdb.has_item(name, repo)

    def get_spec(self, name, repo=None):
        spec, repo = self.get_spec_repo(name, repo)
        return spec

    def search_spec(self, terms, lang=None, repo=None, fields=None, cs=False):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None this method will search in all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        if not lang:
            lang = inary.sxml.autoxml.LocalText.get_lang()
        found = []
        for name, xml in self.sdb.get_items_iter(repo):
            if terms == [term for term in terms if (fields['name'] and \
                    re.compile(term, re.I).search(name)) or \
                    (fields['summary'] and \
                    re.compile(resum.format(lang, term), 0 if cs else re.I).search(xml)) or \
                    (fields['desc'] and \
                    re.compile(redesc.format(lang, term), 0 if cs else re.I).search(xml))]:
                found.append(name)
        return found

    def get_spec_repo(self, name, repo=None):
        src, repo = self.sdb.get_item_repo(name, repo)
        spec = Specfile.SpecFile()
        spec.parse(src)
        return spec, repo

    def pkgtosrc(self, name, repo=None):
        return self.psdb.get_item(name, repo)

    def get_rev_deps(self, name, repo=None):
        try:
            rvdb = self.rvdb.get_item(name, repo)
        except Exception: #FIXME: what exception could we catch here, replace with that.
            return []

        rev_deps = []

        if parser=="ciksemel":
            for pkg, dep in rvdb:
                node = ciksemel.parseString(dep)
                dependency = inary.analyzer.dependency.Dependency()
                dependency.package = node.firstChild().data()
                if node.attributes():
                    attr = node.attributes()[0]
                    dependency.__dict__[attr] = node.getAttribute(attr)
                    rev_deps.append((pkg, dependency))

        else:
            for pkg, dep in rvdb:
                node = minidom.parseString(dep).documentElement
                dependency = inary.analyzer.dependency.Dependency()
                dependency.package = node.childNodes[0].data
                if node.attributes():
                    attr = node.attributes()[0]
                    dependency.__dict__[attr] = node.getAttribute(attr)
                rev_deps.append((pkg, dependency))
        return rev_deps
