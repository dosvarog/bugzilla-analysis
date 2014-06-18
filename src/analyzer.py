#!/usr/bin/python
# -*- coding: utf-8 -*-

from src.base import BugzillaDB, MongoDatabase


class AbstractAnalyzer(object):
    """ This is a base class that represents database interface.
    All other classes which represent concrete implementations of database
    must be derived from this class.
    """
    def calculateScore(self, qry):
        raise Exception("You must implement this method in a derived class!")

    def getNumberOfBugs(self, qry):
        raise Exception("You must implement this method in a derived class!")

    def getNumberOfBugsByType(self, qry):
        raise Exception("You must implement this method in a derived class!")

class MongoAnalyzer(AbstractAnalyzer):
    """ This is concrete implementation of database using the strategy
    interface.
    """
    #private:
    _enhan_weight = 0.143
    _trivial_weight = 0.286
    _minor_weight = 0.429
    _normal_weight = 0.571
    _major_weight = 0.714
    _critical_weight = 0.857
    _blocker_weight = 1

    _enhan_num = 0
    _trivial_num = 0
    _minor_num = 0
    _normal_num = 0
    _major_num = 0
    _critical_num = 0
    _blocker_num = 0

    def _reset(self):
        self._enhan_num = 0
        self._trivial_num = 0
        self._minor_num = 0
        self._normal_num = 0
        self._major_num = 0
        self._critical_num = 0
        self._blocker_num = 0

    def _countBugs(self, query):
        for bug in query.find():
            if bug['severity'] == 'enhancement':
                self._enhan_num += 1
            elif bug['severity'] == 'trivial':
                self._trivial_num += 1
            elif bug['severity'] == 'minor':
                self._minor_num += 1
            elif bug['severity'] == 'normal':
                self._normal_num += 1
            elif bug['severity'] == 'major':
                self._major_num += 1
            elif bug['severity'] == 'critical':
                self._critical_num += 1
            elif bug['severity'] == 'blocker':
                self._blocker_num += 1

    def calculateScore(self, qry):
        self._countBugs(qry)
        score = self._enhan_num*self._enhan_weight + \
                self._trivial_num*self._trivial_weight + \
                self._minor_num*self._minor_weight + \
                self._normal_num*self._normal_weight + \
                self._major_num*self._major_weight + \
                self._critical_num*self._critical_weight + \
                self._blocker_num*self._blocker_weight

        self._reset()
        return score

    def getNumberOfBugs(self, qry):
        self._countBugs(qry)
        numOfBugs = self._enhan_num + \
                    self._trivial_num + \
                    self._minor_num + \
                    self._normal_num + \
                    self._major_num + \
                    self._critical_num + \
                    self._blocker_num

        self._reset()
        return numOfBugs

    def getNumberOfBugsByType(self, qry):
        self._countBugs(qry)
        bugs_by_type = {'enhancement': self._enhan_num,
                        'trivial': self._trivial_num,
                        'minor': self._minor_num,
                        'normal': self._normal_num,
                        'major': self._major_num,
                        'critical': self._critical_num,
                        'blocker': self._blocker_num}
        self._reset()
        return bugs_by_type


class Analyzer(object):
    """ This class is actually a Context that is configured with
    a ConcreteStrategy object and maintains a reference to a Strategy object.
    """
    def __init__(self, database, analyzer):
        self.db = database
        self.an = analyzer

    def calculateScore(self, product):
        q = self.db.queryProductBugs(str(product))
        scr = self.an.calculateScore(q)
        return scr

    def getNumberOfBugs(self, product):
        q = self.db.queryProductBugs(str(product))
        num = self.an.getNumberOfBugs(q)
        return num

    def getNumberOfBugsByType(self, product):
        q = self.db.queryProductBugs(str(product))
        typ = self.an.getNumberOfBugsByType(q)
        return typ
