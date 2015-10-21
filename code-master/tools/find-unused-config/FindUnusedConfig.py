import os
import collections
import yaml

#################
###LOAD CONFIG###
#################

os.chdir("../../share/bitbots/")
root = os.path.curdir


def include(loader, node):
    """Include another YAML file."""
    filename = os.path.join(root, loader.construct_scalar(node))
    data = yaml.load(open("" + filename + ".yaml", 'r'))
    return data


yaml.add_constructor('!include', include)

config = yaml.load(open("config.yaml", "r"))

#print yaml.dump(config)

#####################
###END LOAD CONFIG###
#####################


###CLEAN CONFIG VALUES###


def clear(dic):
    for key, value in dic.iteritems():
        if isinstance(value, collections.Mapping):
            #Handelt sich um ein Verschachteltes Dictionary -> Recursiver absteieg
            rec = clear(value)
            dic[key] = rec
        else:
            dic[key] = False
    return dic

config = clear(config)
#
#print config  # config beinhaltet nurnoch False (= nicht benutzt)

###END CLEAN CONFIG VALUES###

###LOAD PYTHON FILELIST###
os.chdir("../../lib/bitbots")
filelist = []
for root, subdirs, files in os.walk("."):
    for allfile in files:
        #if allfile[-3:] == ".py":
        if "py" in allfile:
            filepath = root + "/" + allfile
            #print filepath
            filelist.append(filepath)


###END LOAD PYTHON FILELIST###

###LOOK FOR USED CONFIG###
    dictkeys = []
for filepath in filelist:
    pyfile = open(filepath, "r")

    prefix = []

    global dictkeys

    for line in pyfile:
        if "get_config()" in line:
            splitted = line.split("get_config()")[1]
            if "[" in splitted:
                splitted = splitted[2:-3]
                #print splitted
                if "\"][\"" in splitted:
                    for key in splitted.split("\"][\""):

                        prefix.append(key)
                else:
                    prefix = [splitted]
                #print prefix

        if "config[" in line:
            #print line
            line, var, var = line.rpartition("]")
            #print line
            try:
                eol = line.split("config[")[1][1:-1]

                keylist = eol.split("\"][\"")

                totalkeylist = prefix + keylist
                dictkeys.append(totalkeylist)
                #print "T:" + str(totalkeylist)
            except IndexError:
                pass
                #print line


###END LOOK FOOR USED CONFIG###


###MAP USED TO CONFIG###

def check(dict, keylist):
    try:
        #print "Dict" + str(dict)
        #print "KEyList" + str(keylist)
        if not keylist:
            print "unerwartetes Ende"
            return dict
        if isinstance(dict[keylist[0]], collections.Mapping):
            #Tiefer Absteigen
            subdict = check(dict[keylist[0]], keylist[1:])
            dict[keylist[0]] = subdict
            return dict
        else:
            dict[keylist[0]] = True
            #angekommen
            return dict
    except KeyError:
        print "Fehlerhafter Key" + str(keylist)
        return dict

for keylist in dictkeys:
    #print "Looking for: " + str(keylist)
    #print config
    config = check(config, keylist)

###END MAP USED TO CONFIG###

###TELL ME KEYS###


notusedliste = []
usedliste = []


def givekeys(node, bufferlist):
    if not isinstance(node, collections.Mapping):
        if node:
            usedliste.append(bufferlist)
        else:
            notusedliste.append(bufferlist)
    else:
        for dkey, value in node.iteritems():
            #bufferlist.append(dkey)
            givekeys(value, bufferlist + [dkey])


givekeys(config, [])

#print len(config)
#print "Dictionary:" + str(config)
#print "liste: " + str(listenliste)
###END TELL ME KEYS

for element in usedliste:
    print "Used", element

print "######################################################\n#########################################################"

for element in notusedliste:
    print "Probably not used", element

print "Used: ", len(usedliste), " - Unused: ", len(notusedliste)

print "#######BEHAVIOUR ONLY#######"
for element in notusedliste:
    if element[0] == "Behaviour":
        print "Not used", element

