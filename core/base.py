#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
import errno
from pyzilla import BugZilla


class XMLDatabase(object):
    #private:
    _dbdir = ""
    _fileTemplate = "%s.xml"
    _productName = ""

    def _createNewXMLFile(self):
        """ Creates empty XML file and returns it's name."""

        if len(self._productName) == 0:
            raise ValueError("You must provide a valid product name!")

        filename = self._dbdir + self._fileTemplate % self._productName

        return filename

    #public:
    def setProductName(self, pn):
        """ Sets current product name """

        self._productName = str(pn)

    def setDatabaseName(self, dbname):
        """Sets database name """

        if len(dbname) == 0:
            pass
        else:
            self._dbdir = "./%s/" % dbname

    def createNewDBDir(self):
        """ Creates new directory where XML files will be saved """

        if len(self._dbdir) == 0:
            self._dbdir = "./default/"

        try:
            os.makedirs(self._dbdir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def serialize(self, bugsDict):
        """ Serializes retrieved bugs in a form of XML file. """

        def _serialize(tag, root):
            for k, v in tag.items():
                if isinstance(v, dict):
                    node = ET.SubElement(root, k)
                    _serialize(v, node)
                elif isinstance(v, list):
                    # value = ';'.join(v)
                    # node = ET.SubElement(root, k)
                    # node.text = value

                    # or even better, pass because we don't
                    # know what that list contains
                    pass
                elif isinstance(v, basestring):
                    node = ET.SubElement(root, k)
                    node.text = v
                else:
                    node = ET.SubElement(root, k)
                    node.text = str(v)

        k, v = bugsDict.items()[0]
        root = ET.Element(k)
        #numOfBugs = len(v)

        create_time = v[0]['creation_time']

        for bug in v:
            node = ET.Element("bug")

            if bug['creation_time'] > create_time:
                create_time = bug['creation_time']

            _serialize(bug, node)
            root.append(node)
            root.attrib["creation_time"] = str(create_time)

        return root

    def writeToXMLFile(self, ser):
        ET.ElementTree(ser).write(self._createNewXMLFile())
        print "Serialized:", self._productName

    def loadXMLFile(self):
        PATH = "%s%s.xml" % (self._dbdir, self._productName)

        if os.path.isfile(PATH):
            tree = ET.parse(PATH)
            root = tree.getroot()
            return root
        else:
            return None

    def getCreationTime(self, root):
        create_time = root.attrib.get("creation_time")

        return create_time.replace(":", "")

    def update(self, bugsDict):
        root = self.loadXMLFile()
        root_creation_time = root.attrib.get("creation_time")

        newBugs = self.serialize(bugsDict)
        new_creation_time = newBugs.attrib.get("creation_time")

        if root_creation_time == new_creation_time:
            pass
        else:
            for child in newBugs:
                root.append(child)
                root.set('creation_time', new_creation_time)
                self.writeToXMLFile(root)


class BugzillaDB(object):
    #private:
    _url = ""
    _dbname = ""

    #public:
    def __init__(self, url, dbname=""):
        self.database = XMLDatabase()

        if len(url) == 0:
            raise ValueError("You must provide database URL!")

        self._url = url
        self._dbname = dbname
        self.bzilla = BugZilla(self._url, verbose=False)
        self.database.setDatabaseName(self._dbname)
        self.database.createNewDBDir()

    def getListOfProducts(self):
        productsList = []
        productsIDs = self.bzilla.Product.get_selectable_products()
        productsDict = self.bzilla.Product.get({'ids': productsIDs['ids']})

        for product in productsDict['products']:
            productsList.append(product['name'])

        return productsList

    def getBugs(self):
        listOfProducts = self.getListOfProducts()

        for product in listOfProducts:
            self.database.setProductName(product)
            bugs = self.bzilla.Bug.search({"product": str(product)})
            serialized = self.database.serialize(bugs)
            self.database.writeToXMLFile(serialized)

    def getBug(self, product):
        self.database.setProductName(product)
        bugs = self.bzilla.Bug.search({"product": str(product)})
        serialized = self.database.serialize(bugs)
        self.database.writeToXMLFile(serialized)

    def updateBug(self, product):
        self.database.setProductName(product)
        create_time = self.database.getCreationTime(self.database.loadXMLFile())
        bugs = self.bzilla.Bug.search({"product": str(product),
                                       "creation_time": create_time})
        self.database.update(bugs)
