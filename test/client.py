#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.base import BugzillaDB, XMLDatabase


def main():
    xmldb = XMLDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    bugdb = BugzillaDB(xmldb)

    bugdb.downloadProductBugs('galf')
    #bugdb.downloadAllProductsBugs()
    #bugdb.updateProductBugs('galf')
    #bugdb.updateAllProductsBugs()
    #print bugdb.queryProductBugs('bonobo')
    #bugdb.listTrackedProducts()

if __name__ == '__main__':
    main()