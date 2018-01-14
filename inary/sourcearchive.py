# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (AquilaNipalensis)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# python standard library

import os
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# inary modules
import inary
import inary.util as util
import inary.context as ctx
import inary.archive
import inary.uri
import inary.fetcher
import inary.mirrors

class Error(inary.Error):
    pass

class SourceArchives:
    """This is a wrapper for supporting multiple SourceArchive objects."""
    def __init__(self, spec):
        self.sourceArchives = [SourceArchive(a) for a in spec.source.archive]

    def fetch(self, interactive=True):
        for archive in self.sourceArchives:
            archive.fetch(interactive)

    def unpack(self, target_dir, clean_dir=True):
        self.sourceArchives[0].unpack(target_dir, clean_dir)
        for archive in self.sourceArchives[1:]:
            archive.unpack(target_dir, clean_dir=False)


class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, archive):
        self.url = inary.uri.URI(archive.uri)
        self.archiveFile = os.path.join(ctx.config.archives_dir(), self.url.filename())
        self.archive = archive

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                self.progress = ctx.ui.Progress
            else:
                self.progress = None

            try:
                ctx.ui.info(_("Fetching source from: %s") % self.url.uri)
                if self.url.get_uri().startswith("mirrors://"):
                    self.fetch_from_mirror()
                else:
                    inary.fetcher.fetch_url(self.url, ctx.config.archives_dir(), self.progress)
            except inary.fetcher.FetchError:
                if ctx.config.values.build.fallback:
                    self.fetch_from_fallback()
                else:
                    raise

            ctx.ui.info(_("Source archive is stored: %s/%s")
                % (ctx.config.archives_dir(), self.url.filename()))

    def fetch_from_fallback(self):
        archive = os.path.basename(self.url.get_uri())
        src = os.path.join(ctx.config.values.build.fallback, archive)
        ctx.ui.warning(_('Trying fallback address: %s') % src)
        inary.fetcher.fetch_url(src, ctx.config.archives_dir(), self.progress)

    def fetch_from_mirror(self):
        uri = self.url.get_uri()
        sep = uri[len("mirrors://"):].split("/")
        name = sep.pop(0)
        archive = "/".join(sep)

        mirrors = inary.mirrors.Mirrors().get_mirrors(name)
        if not mirrors:
            raise Error(_("%s mirrors are not defined.") % name)

        for mirror in mirrors:
            try:
                url = os.path.join(mirror, archive)
                ctx.ui.warning(_('Fetching source from mirror: %s') % url)
                inary.fetcher.fetch_url(url, ctx.config.archives_dir(), self.progress)
                return
            except inary.fetcher.FetchError:
                pass

        raise inary.fetcher.FetchError(_('Could not fetch source from %s mirrors.') % name);

    def is_cached(self, interactive=True):
        if not os.access(self.archiveFile, os.R_OK):
            return False

        # check hash
        if util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            if interactive:
                ctx.ui.info(_('%s [cached]') % self.archive.name)
            return True

        return False

    def unpack(self, target_dir, clean_dir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            raise Error(_("unpack: check_file_hash failed"))

        try:
            archive = inary.archive.Archive(self.archiveFile, self.archive.type)
        except inary.archive.UnknownArchiveType:
            raise Error(_("Unknown archive type '%s' is given for '%s'.")
                        % (self.archive.type, self.url.filename()))
        except inary.archive.ArchiveHandlerNotInstalled:
            raise Error(_("Inary needs %s to unpack this archive but it is not installed.")
                        % self.archive.type)

        target_dir = os.path.join(target_dir, self.archive.target or "")
        archive.unpack(target_dir, clean_dir)
