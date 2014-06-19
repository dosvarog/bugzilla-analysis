#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.base import BugzillaDB, MongoDatabase
from src.analyzer import Analyzer, MongoAnalyzer


def main():
    #xmldb = XMLDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    mongodb = MongoDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
    bugdb = BugzillaDB(mongodb)
    man = MongoAnalyzer()
    an = Analyzer(bugdb, man)

    # score = an.calculateProductScore('bonobo')
    # print score
    # num = an.getNumberOfBugs('bonobo')
    # print num
    # typ = an.getNumberOfBugsByType('bonobo')
    # print typ

    # an.plotProductSeverityDistribution('libgnome')
    # print an.cmpTwoProducts('bonobo', 'Gnumeric')

    # bugdb.downloadProductBugs('Atomic')
    # bugdb.downloadAllProductsBugs()
    # bugdb.updateProductBugs('galf')
    # bugdb.updateAllProductsBugs()
    # var = bugdb.queryProductBugs('galf')
    # for p in var.find():
    #     print p
    # bugdb.listTrackedProducts()

if __name__ == '__main__':
    main()
