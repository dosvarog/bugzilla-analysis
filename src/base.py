#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import xml.etree.ElementTree as ET
import errno
import datetime

from pymongo import MongoClient
from pyzilla import BugZilla


class Database(object):
    """ This is a base class that represents database interface.
    All other classes which represent concrete implementations of database
    must be derived from this class.

    The Context (BugzillaDB class) uses this to call concrete strategy.
    """
    def getListOfProducts(self, dbtype=''):
        raise Exception("You must implement this method in a derived class!")

    def downloadProductBugs(self, product):
        raise Exception("You must implement this method in a derived class!")

    def downloadAllProductsBugs(self):
        raise Exception("You must implement this method in a derived class!")

    def updateProductBugs(self, product):
        raise Exception("You must implement this method in a derived class!")

    def updateAllProductsBugs(self):
        raise Exception("You must implement this method in a derived class!")

    def queryProductBugs(self, product):
        raise Exception("You must implement this method in a derived class!")

    def listTrackedProducts(self):
        raise Exception("You must implement this method in a derived class!")


class MongoDatabase(Database):
    """ This is concrete implementation of database using the strategy
    interface.

    This class represents MongoDB database and uses it to store data about
    bugs found in a specific product. Each product is a separate collection,
    while each document in that collection represents a bug.
    """

    def __init__(self, url, dbname='default'):
        if len(url) == 0:
            raise ValueError("You must provide database URL!")

        self.client = MongoClient()
        self.db = self.client[dbname]
        self.bzilla = BugZilla(url, verbose=False)

    def createDateTimeObjects(self, bugs_dict):
        """ Since Bugzilla doesn't return times in Python datetime format, we
        have to search through dictionaries for those times and transform them
        to datetime objects so MongoDB can save them in a BSON format.
        """

        def _create_datetime(corr_dicts):
            for k, v in corr_dicts.items():
                if isinstance(v, dict):
                    _create_datetime(v)
                elif k == 'creation_time':
                    dt = str(v)
                    corr_dt = datetime.datetime.strptime(dt,
                                                         '%Y%m%dT%H:%M:%S')
                    corr_dicts['creation_time'] = corr_dt
                elif k == 'last_change_time':
                    dt = str(v)
                    corr_dt = datetime.datetime.strptime(dt,
                                                         '%Y%m%dT%H:%M:%S')
                    corr_dicts['last_change_time'] = corr_dt
                elif k == 'cf_last_closed':
                    dt = str(v)
                    corr_dt = datetime.datetime.strptime(dt,
                                                         '%Y%m%dT%H:%M:%S')
                    corr_dicts['cf_last_closed'] = corr_dt

        bugs_list = bugs_dict.values()[0]

        for bug in bugs_list:
            _create_datetime(bug)

        return bugs_list

    def getListOfProducts(self, dbtype=''):
        productsList = []

        if dbtype.lower() == "bugzilla":
            productsIDs = self.bzilla.Product.get_selectable_products()
            productsDict = self.bzilla.Product.get({'ids': productsIDs['ids'],
                                                   'include_fields': ['name']})

            for product in productsDict['products']:
                productsList.append(product['name'])

        else:
            productsList = self.db.collection_names(include_system_collections=
                                                    False)

        return productsList

    def downloadProductBugs(self, product):
        collection = self.db[str(product)]
        if str(product) in self.db.collection_names():
            collection.drop()

        print "Downloading product: %s" % str(product)
        try:
            bugs = self.bzilla.Bug.search({'product': str(product)})
            collection.insert(self.createDateTimeObjects(bugs))
            print "Product saved to a database.\n"
        except Exception as e:
            print e
            print "Could not fetch %s bugs.\n" % product

    def downloadAllProductsBugs(self):
        listOfProducts = self.getListOfProducts('bugzilla')
        print "Found %d products for download." % len(listOfProducts)

        for product in listOfProducts:
            self.downloadProductBugs(product)

    def updateProductBugs(self, product):
        collection = self.db[str(product)]
        if str(product) in self.db.collection_names():
            last_entry = collection.aggregate([{'$sort': {'creation_time': -1}},
                                               {'$limit': 1}])
            last_creation_time = last_entry['result'][0]['creation_time']
            bugs = self.createDateTimeObjects(self.bzilla.Bug.search(
                {'product': str(product),
                 'creation_time': last_creation_time}))

            # Bugzilla's search method returns bugs that were created at this
            # time or later, it seems that 'this time' bug is always first in
            # the list.
            bugs.pop(0)

            # if it happens that that's not the case, we will have to
            # use following piece of code:
            # for bug in bugs[:]:
            #     if bug['creation_time'] == last_creation_time:
            #         bugs.remove(bug)
            if bugs:
                collection.insert(bugs)
                print "%s has been updated with new bug entries." % str(product)
            else:
                print "Nothing to update, " \
                      "%s is already up-to-date." % str(product)
        else:
            print "Product doesn't exist in a database."

    def updateAllProductsBugs(self):
        listOfProducts = self.getListOfProducts()

        for product in listOfProducts:
            print product
            self.updateProductBugs(product)

    def queryProductBugs(self, product):
        collection = self.db[str(product)]
        if str(product) not in self.db.collection_names():
            print "Local copy of requested product does not exist.\n" \
                  "Fetching it from Bugzilla..."
            self.downloadProductBugs(product)

        return collection

    def listTrackedProducts(self):
        trackedProducts = self.getListOfProducts()

        print "Currently we are tracking " \
              "%d products." % len(trackedProducts)
        print "Tracked products:"

        for p in trackedProducts:
            print p

        return trackedProducts


class XMLDatabase(Database):
    """ This is concrete implementation of database using the strategy
    interface.

    This class represents XML database which is actually a directory that
    holds XML files where every XML file represents bugs found in that specific
    product.
    """
    #private:
    _dbdir = ""
    _fileTemplate = "%s.xml"
    _productName = ""
    _numOfBugs = 0

    #constructor
    def __init__(self, url, dbname=''):

        if len(url) == 0:
            raise ValueError("You must provide database URL!")

        self.bzilla = BugZilla(url, verbose=False)
        self.createDatabasePath(dbname)
        self.createNewDBDir()

    #private:
    def _createNewXMLFile(self):
        """ Creates empty XML file and returns it's name."""
        if len(self._productName) == 0:
            raise ValueError("You must provide a valid product name!")

        filename = self._dbdir + self._fileTemplate % self._productName

        return filename

    #public:
    def createDatabasePath(self, dbname):
        """ Creates a path to a database directory based on provided dbname """
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
                #TODO specify this exeption
                raise

    def serialize(self, bugsDict):
        """ Serializes retrieved bugs in a form of XML tree.

        We receive a list of dictionaries. Each dictionary in a list
        represents one bug. Bug itself contains other dictionaries
        that hold some information. That is why we use recursive
        function: every nested dictionary is new subelement in XML tree.

        Based on that, we build entire XML tree and return it, ready
        to be written to a hard disk in a form of XML file.
        """
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
        self._numOfBugs = len(v)

        create_time = v[0]['creation_time']

        for bug in v:
            node = ET.Element("bug")

            if bug['creation_time'] > create_time:
                create_time = bug['creation_time']

            _serialize(bug, node)
            root.append(node)
            root.attrib["creation_time"] = str(create_time)

        root.attrib["num_of_bugs"] = str(self._numOfBugs)

        return root

    def writeToXMLFile(self, ser):
        """ Receives XML tree and writes it to XML file on the hard disk """
        ET.ElementTree(ser).write(self._createNewXMLFile())
        print "Serialized:", self._productName

    def loadXMLFile(self):
        """ Loads XML file and returns it in a form of tree (ElementTree) """
        PATH = "%s%s.xml" % (self._dbdir, self._productName)

        if os.path.isfile(PATH):
            tree = ET.parse(PATH)
            root = tree.getroot()
            return root
        else:
            return None

    def getCreationTime(self, root):
        """ Grabs creation time of the newest bug """
        create_time = root.attrib.get("creation_time")
        return create_time.replace(":", "")

    def update(self, bugsDict):
        """ Based on the creation time of the newest bug in XML file
        and creation time of the newest bug in remote Bugzilla
        database it either updates XML file with a new bug, or
        does nothing since there is nothing to update.
        """
        root = self.loadXMLFile()
        root_creation_time = root.attrib.get("creation_time")

        newBugs = self.serialize(bugsDict)
        new_creation_time = newBugs.attrib.get("creation_time")

        no_of_new_bugs = (int(newBugs.attrib.get("num_of_bugs")) +
                          int(root.attrib.get("num_of_bugs")) - 1)

        if root_creation_time == new_creation_time:
            pass
        else:
            for child in newBugs.findall('bug'):
                if child.find('creation_time').text == root_creation_time:
                    continue
                root.append(child)

            root.set('creation_time', new_creation_time)
            root.set('num_of_bugs', str(no_of_new_bugs))
            self.writeToXMLFile(root)

    def getListOfProducts(self, dbtype=''):
        """ Depending on the second argument it either queries Bugzilla
        database for list of products and returns it, or it returns
        a list of products we are currently monitoring in our local
        database. Other methods make use of this method.
        """
        productsList = []

        if dbtype.lower() == "bugzilla":
            productsIDs = self.bzilla.Product.get_selectable_products()
            productsDict = self.bzilla.Product.get({'ids': productsIDs['ids'],
                                                   'include_fields': ['name']})

            for product in productsDict['products']:
                productsList.append(product['name'])

        else:
            fileMatcher = self._dbdir + "*.xml"
            filesList = glob.glob(fileMatcher)

            for ffile in filesList:
                productsList.append(os.path.splitext(
                    os.path.basename(ffile))[0])

        return productsList

    #interface methods
    def downloadProductBugs(self, product):
        self._productName = str(product)

        print "Downloading: %s" % str(product)

        try:
            bugs = self.bzilla.Bug.search({"product": str(product)})
            serialized = self.serialize(bugs)
            self.writeToXMLFile(serialized)
        except Exception as e:
            print e
            print "Could not fetch %s bugs" % product

    def downloadAllProductsBugs(self):
        listOfProducts = self.getListOfProducts('bugzilla')
        print "Found %d products for download." % len(listOfProducts)

        for product in listOfProducts:
            self.downloadProductBugs(product)

    def updateProductBugs(self, product):
        self._productName = str(product)

        create_time = self.getCreationTime(
            self.loadXMLFile())
        bugs = self.bzilla.Bug.search({"product": str(product),
                                       "creation_time": create_time})
        self.update(bugs)

    def updateAllProductsBugs(self):
        listOfProducts = self.getListOfProducts()

        for product in listOfProducts:
            print product
            self.updateProductBugs(product)

    def queryProductBugs(self, product):
        self._productName = str(product)
        bugs = self.loadXMLFile()

        if bugs is None:
            print "Local copy of requested product does not exist.\n" \
                  "Fetching it from Bugzilla..."
            self.downloadProductBugs(product)
            bugs = self.loadXMLFile()

        return bugs

    def listTrackedProducts(self):
        trackedProducts = self.getListOfProducts()

        print "Currently we are tracking " \
              "%d products." % len(trackedProducts)
        print "Tracked products:"

        for p in trackedProducts:
            print p

        return trackedProducts


class BugzillaDB(object):
    """ Storing of collected information to a local database is implemented as
    Startegy pattern. This class is actually a Context that is configured with
    a ConcreteStrategy object and maintains a reference to a Strategy object.
    """
    def __init__(self, database):
        self.db = database

    def downloadProductBugs(self, product):
        """ Queries Bugzilla database for information about specific product,
        pulls that information and stores it in our local database.
        """
        self.db.downloadProductBugs(product)

    def downloadAllProductsBugs(self):
        """ Queries Bugzilla database for information about *all* products,
        pulls that information and stores it in our local database.
        """
        self.db.downloadAllProductsBugs()

    def updateProductBugs(self, product):
        """ Updates our local database with newest bugs and information
        from Bugzilla database on a specific product. It does nothing
        if everything is up to date.
        """
        self.db.updateProductBugs(product)

    def updateAllProductsBugs(self):
        """ Updates our local database with newest bugs and information
        from Bugzilla database on *all* products we have in our local
        database. It does nothing if everything is up to date.
        """
        self.db.updateAllProductsBugs()

    def queryProductBugs(self, product):
        """ Queries our local database for bugs on a specific product.

        If information regarding requested product is not available locally
        method will try to fetch that information from Bugzilla and
        return it.
        """
        bugs = self.db.queryProductBugs(product)
        return bugs

    def listTrackedProducts(self):
        """ List all products that we are tracking in our local database. """
        trackedProducts = self.db.listTrackedProducts()
        return trackedProducts
