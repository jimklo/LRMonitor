'''
Created on Jul 20, 2011

@author: jklo
'''
import argparse, urllib2, json, base64
import types

def getOptions():
    parser = argparse.ArgumentParser(description='Get CouchDB Stats for Cacti')
    
    subparsers = parser.add_subparsers(help="sub-command help")
    
    stats_parser = subparsers.add_parser('stats', help="CouchDB general stats help")
    stats_parser.add_argument("server", help="The url of the couchdb including port and protocol. IE: http://couchdb.example.com:5984")
    stats_parser.add_argument("metric", help="The statistic from /_stats you want to parse in dotted form. IE: couchdb.database_reads")
    stats_parser.add_argument("-u", "--user", help="Basic Authentication user for couchdb", default=None)
    stats_parser.add_argument("-p", "--passwd", help="Basic Authentication password for couchdb", default=None)
    stats_parser.set_defaults(mode="stats")
    
    db_parser = subparsers.add_parser('db', help="CouchDB db stats help")
    db_parser.add_argument("server", help="The url of the couchdb including port and protocol. IE: http://couchdb.example.com:5984")
    db_parser.add_argument("dbname", help="The CouchDB name")
    db_parser.add_argument("-u", "--user", help="Basic Authentication user for couchdb", default=None)
    db_parser.add_argument("-p", "--passwd", help="Basic Authentication password for couchdb", default=None)
    db_parser.set_defaults(mode="db")
    
   
    view_parser = subparsers.add_parser('view', help="CouchDB view stats help")
    view_parser.add_argument("server", help="The url of the couchdb including port and protocol. IE: http://couchdb.example.com:5984")
    view_parser.add_argument("dbname", help="The CouchDB name")
    view_parser.add_argument("design", help="The CouchDB design document id")
    view_parser.add_argument("-u", "--user", help="Basic Authentication user for couchdb", default=None)
    view_parser.add_argument("-p", "--passwd", help="Basic Authentication password for couchdb", default=None)
    view_parser.set_defaults(mode="view")
    
    return parser.parse_args()


class BasicStats(object):
    
    def _getStatsJSON(self, path,  opts=getOptions()):
        req = urllib2.Request("{0}{1}".format(opts.server, path), headers= {"Content-type": "application/json"})
        if opts.user != None and opts.passwd != None:
            b64 = base64.encodestring('{0}:{1}'.format(opts.user, opts.passwd)).replace('\n', '')
            req.add_header("Authorization", "Basic {0}".format(b64))
        res = urllib2.urlopen(req)
        stats = json.load(res)
        return stats

class GeneralStats(BasicStats):
    def __init__(self):
        BasicStats.__init__(self)
    
    def _getStats(self, opts=getOptions()):
        stats = self._getStatsJSON("/_stats", opts)
        return stats
        
    def _getStat(self, allstats, opts):
        stat = opts.metric.split('.')
        buflist = []
        if len(stat) == 2:
            one_stat = allstats[stat[0]][stat[1]]
            for (key, value) in one_stat.items():
                if key != "description" and value != None:
                   buflist.append("{0}:{1}".format(key, value))
        return " ".join(buflist)
    
    def fetch(self, opts=getOptions()):
        return self._getStat(self._getStats(opts), opts)

class DBStats(BasicStats):
    def __init__(self):
        BasicStats.__init__(self)

    def _getStats(self, opts=getOptions()):
        stats = self._getStatsJSON("/{0}".format(opts.dbname), opts)
        return stats
        
    def fetch(self, opts=getOptions()):
        stats = self._getStats(opts)
        buflist = []
        for (key, value) in stats.items():
            if isinstance(value, (types.IntType, types.LongType, types.FloatType, types.BooleanType)):
                buflist.append("{0}:{1}".format(key, int(value)))
        return " ".join(buflist)
    
class ViewStats(BasicStats):
    def __init__(self):
        BasicStats.__init__(self)

    def _getStats(self, opts=getOptions()):
        stats = self._getStatsJSON("/{0}/{1}/_info".format(opts.dbname, opts.design), opts)
        return stats
        
    def fetch(self, opts=getOptions()):
        stats = self._getStats(opts)
        buflist = []
        if "view_index" in stats:
            for (key, value) in stats["view_index"].items():
                if isinstance(value, (types.IntType, types.LongType, types.FloatType, types.BooleanType)):
                    buflist.append("{0}:{1}".format(key, int(value)))
                
        return " ".join(buflist)
    
    
if __name__ == '__main__':
    modes = {
                "stats": GeneralStats(),
                "db": DBStats(),
                "view": ViewStats(),
            }
    opts = getOptions()
    
    if opts.mode in modes:
        print modes[opts.mode].fetch(opts)
