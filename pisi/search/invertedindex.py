# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@uludag.org.tr>

class InvertedIndex(object):
    """a database of term -> set of documents"""
    
    def __init__(self, id, lang):
        self.d = shelve.LockedDBShelf('ii-%s-%s' % (id, lang))

    def close(self):
        self.d.close()

    def has_term(self, term):
        return self.d.has_key(str(term))

    def get_term(self, term):
        term = str(term)
        if not self.has_term(term):
            self.d[term] = set()
        return self.d[term]

    def list_terms(self):
        list = []
        for term in self.d.iterkeys():
            list.append(term)
        return list

    def add_doc(self, doc, terms):
        for term_i in terms:
            term_i_docs = self.get_term(term_i)
            term_i_docs.add(doc)
            self.d[term_i] = term_i_docs # update

    def remove_doc(self, doc, terms):
        for term_i in terms:
            term_i_docs = self.get_term(term_i)
            term_i_docs.remove(doc)
            self.d[term_i] = term_i_docs # update
