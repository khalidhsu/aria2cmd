#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
try:
    import xmlrpclib
except:
    import xmlrpc.client as xmlrpclib
import config
 
def prettysize(size):
    suffixes = [("B",2**10), ("K",2**20), ("M",2**30), ("G",2**40), ("T",2**50)]
    for suf, lim in suffixes:
        if size > lim:
            continue
	else:
            return round(size/float(lim/2**10),2).__str__()+suf

class aria2ctl:
    def __init__(self):
        conf = config.aria2load()
        port = conf.get("xml-rpc-listen-port", "6800")
        user = conf.get("xml-rpc-user", "")
        passwd = conf.get("xml-rpc-passwd", "")
        self.ctl = xmlrpclib.ServerProxy("http://%s:%s@localhost:%s/rpc" %(user, passwd, port)).aria2
        self.attr = ["gid","files","totalLength","completedLength","uploadLength","downloadSpeed","uploadSpeed"]

    def abstract(self, cmd):
        try:
            string = "self.ctl."+cmd
            return eval(string)
        except Exception as e:
            return (False, e)
    
    def getlist(self, query):
        num = len(query)
        result = []

        for i in range(num):
            result.append({"gid":"0" ,"file":"0", "length":"0", "ratio":"0", "down":"0", "up":"0", "seed":"0"})
            result[i]["gid"] = query[i]["gid"]
            result[i]["file"] = os.path.basename(query[i]["files"][0]["path"])
            result[i]["length"] = prettysize(int(query[i]["totalLength"]))
            try:
                result[i]["ratio"] = str(int(float(query[i]["completedLength"])/float(query[i]["totalLength"])*100))+"%"
            except:
                result[i]["ratio"] = "0"
            result[i]["down"] = prettysize(int(query[i]["downloadSpeed"]))+"/s"
            result[i]["up"] = prettysize(int(query[i]["uploadSpeed"]))+"/s"
            try:
                result[i]["seed"] = str(round(float(query[i]["uploadLength"])/float(query[i]["totalLength"]), 1))
            except:
                result[i]["seed"] = "0"

        return result

    def add(self, uri):
        if os.path.isfile(uri):
            if uri.endswith(".metalink") or uri.endswith(".meta4"):
                string = "self.ctl.addMetalink(xmlrpclib.Binary(open('%s').read()))" %(uri)
            elif uri.endswith(".torrent"):
                string = "self.ctl.addTorrent(xmlrpclib.Binary(open('%s').read()))" %(uri)
        else:
            string = "self.ctl.addUri(['%s'])" %(uri)

        try:
            exec(string)
        except Exception as e:
            return (False, e) 
        return True

    def tell(self, status):
        try:
            if status == "wait":
                query = self.ctl.tellWaiting(0,5,self.attr)
            elif status == "stop":
                query = self.ctl.tellStopped(0,5,self.attr)
            else:
                query = self.ctl.tellActive(self.attr)
        except Exception as e:
            return (False, e)

        return self.getlist(query)

    def remove(self, gid):
        try:
            self.ctl.remove(gid)
        except Exception as e:
            return (False, e)
        return True

    def stop(self, gid=None):
        try:
            if gid == None:
                self.ctl.pauseAll()
            else:
                self.ctl.pause(gid)
        except Exception as e:
            return (False, e)
        return True    

    def start(self, gid=None):
        try:
            if gid == None:
                self.ctl.unpauseAll()
            else:
                self.ctl.unpause(gid)
        except Exception as e:
            return (False, e)
        return True
