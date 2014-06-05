#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.base import BugzillaDB

def main():
    d = BugzillaDB("https://bugzilla.redhat.com/xmlrpc.cgi", "fedora")
    d.getBug("Atomic")
    #d.updateBug("Atomic")

if __name__ == '__main__':
    main()