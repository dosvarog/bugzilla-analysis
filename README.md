## Synopsis

This tool is intended for analysis of software quality based on the entries in
Bugzilla databases. It consists of a part that downloads and saves bug entries
locally, and a part that uses that information to estimate software quality.

## Installation

To install this tool simply clone it's git repository:

    git clone https://github.com/dosvarog/bugzilla-analysis.git

or download a .zip file and extract it.

Put .py files where you want and simply import them in Python.

## Requirements

You will also need to download two Python modules: PyZilla and CairoPlot
You can find PyZilla here: https://github.com/williamh/PyZilla
and CairoPlot here: https://launchpad.net/cairoplot

## Code Examples

    from src.base import BugzillaDB, XMLDatabase

    def main():
        xmldb = XMLDatabase("https://bugzilla.gnome.org/xmlrpc.cgi", "gnome")
        bugdb = BugzillaDB(xmldb)

        # now call methods that BugzillaDB provides
        # for a complete list, refer to a test.py file in test/ dir

        bugdb.downloadProductBugs('gnote')
