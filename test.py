#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.base import BugzillaDB

def main():
    d = BugzillaDB("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    #d.updateProductBugs('gnote')
    #d.downloadProductBugs('gnote')
    #d.updateBug("Atomic")
    var = d.queryProductBugs('gnote')
    #d.listTrackedProducts('xml')

if __name__ == '__main__':
    main()