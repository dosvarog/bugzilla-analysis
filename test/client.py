#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.base import BugzillaDB, XMLDatabase


def main():
    xmldb = XMLDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    bugdb = BugzillaDB(xmldb)

    # download bugs of a specific product, which exists of course
    #bugdb.downloadProductBugs('galf')

    # download bugs of all products in a database
    #bugdb.downloadAllProductsBugs()

    # update product in a local database
    #bugdb.updateProductBugs('galf')

    # update all products in a local database
    #bugdb.updateAllProductsBugs()

    # query local database for bugs on a provided product
    #bugs = bugdb.queryProductBugs('bonobo')

    # list all products that are tracked locally
    #bugdb.listTrackedProducts()

if __name__ == '__main__':
    main()
