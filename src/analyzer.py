#!/usr/bin/python
# -*- coding: utf-8 -*-

import CairoPlot


class AbstractAnalyzer(object):
    """ This is a base class that represents database interface.
    All other classes which represent concrete implementations of database
    must be derived from this class.
    """
    def calculateProductScore(self, qry):
        raise Exception("You must implement this method in a derived class!")

    def getNumberOfBugs(self, qry):
        raise Exception("You must implement this method in a derived class!")

    def getNumberOfBugsByType(self, qry):
        raise Exception("You must implement this method in a derived class!")

    def plotSeverityDistribution(self, dist, product):
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

    def calculateProductScore(self, qry):
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

    def plotProductSeverityDistribution(self, dist, product):
        severity_list = ['enhancement', 'trivial', 'minor', 'normal',
                         'major', 'critical', 'blocker']
        values_list = []

        for severity in severity_list:
            values_list.append(dist[severity])

        maxbugs = "%d bugs" % max(values_list)
        vlabels = ['zarro boogs', maxbugs]

        CairoPlot.bar_plot(str(product), values_list, 500, 400,
                           border=20, grid=True,
                           h_labels=severity_list, v_labels=vlabels)


class Analyzer(object):
    """ This class is actually a Context that is configured with
    a ConcreteStrategy object and maintains a reference to a Strategy object.
    """
    def __init__(self, database, analyzer):
        self.db = database
        self.an = analyzer

    def calculateProductScore(self, product):
        q = self.db.queryProductBugs(str(product))
        scr = self.an.calculateProductScore(q)
        return scr

    def getNumberOfBugs(self, product):
        q = self.db.queryProductBugs(str(product))
        num = self.an.getNumberOfBugs(q)
        return num

    def getNumberOfBugsByType(self, product):
        q = self.db.queryProductBugs(str(product))
        typ = self.an.getNumberOfBugsByType(q)
        return typ

    def plotProductSeverityDistribution(self, product):
        severity_dist = self.getNumberOfBugsByType(product)
        self.an.plotProductSeverityDistribution(severity_dist, product)

    def cmpTwoProducts(self, prod1, prod2):
        q = self.db.queryProductBugs(str(prod1))
        score1 = self.an.calculateProductScore(q)
        num_of_bugs1 = self.an.getNumberOfBugs(q)
        q = self.db.queryProductBugs(str(prod2))
        score2 = self.an.calculateProductScore(q)
        num_of_bugs2 = self.an.getNumberOfBugs(q)

        compared = {}
        # now we have to normalize the score,
        # since some products have a lot
        # of bugs, while others do not

        if num_of_bugs1 == num_of_bugs2:
            compared = {str(prod1): score1, str(prod2): score2}
            return compared
        elif num_of_bugs1 < num_of_bugs2:
            scale = num_of_bugs1/float(num_of_bugs2)
            score2 *= scale
            compared = {str(prod1): score1, str(prod2): score2}
            return compared
        else:
            scale = num_of_bugs2/float(num_of_bugs1)
            score1 *= scale
            compared = {str(prod1): score1, str(prod2): score2}
            return compared
