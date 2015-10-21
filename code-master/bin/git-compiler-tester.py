from subprocess import call


commits = open("/tmp/gitlog","r")
for line in commits:
    commit = line[:8]
    print line
    call("git checkout --force %s" % commit, shell=True)
    call("git stash apply", shell=True)
    if call("./build Release", shell=True):
        print "Build Failt!"
        continue
    if not call("motion --simulate 127.0.0.1", shell=True):
        print "Sucsess!"
        break

