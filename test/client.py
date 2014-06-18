#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.base import BugzillaDB, MongoDatabase, XMLDatabase


def main():
    #xmldb = XMLDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    mongodb = MongoDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    bugdb = BugzillaDB(mongodb)

    # bugdb.downloadProductBugs('galf')
    # bugdb.downloadAllProductsBugs()
    # bugdb.updateProductBugs('galf')
    # bugdb.updateAllProductsBugs()
    # var = bugdb.queryProductBugs('bonobo')
    # for p in var.find():
    #     print p
    # bugdb.listTrackedProducts()

if __name__ == '__main__':
    main()
