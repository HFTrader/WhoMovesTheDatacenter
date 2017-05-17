#!/usr/bin/python
import os
import sys
import subprocess
import json
import re

def runcmd( cmd ):
    # Run a system command, funneling stdout and stderr to the respective
    # configuration logs
    #print "Exec:", cmd
    pc = subprocess.Popen( cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=True )
    try:
        out,err = pc.communicate()
    except Exception, e:
        print >> sys.stderr, "Exception running", cmd, ":", e
    if pc.returncode != 0:
        print '\n'.join( err.split('\n')[-30:] )
    return (pc.returncode, out, err)


def listdeps( package ):
    if not package: return None
    cmd = "apt-cache depends \"%s\" | sed -n 's/^\s*Depends:\s*\(.*\)\s*/\\1/p' " % ( package, )
    retcode, out, err = runcmd( cmd )
    return [ p for p in out.split('\n') if p ]

script_re = re.compile( "^\s*([\w\-+]+)\s+(script|source)" )

def filegroup( typename ):
    if "," in typename:
        typename,_ = typename.split(",",1)
    grp = script_re.match( typename )
    if grp:
        typename =grp.group(1)
    return typename.strip().lower()

packages = dict( [ (fn,1) for fn in sys.argv[1:] ] )
processed = {}
while packages:
    new_packages = {}
    cnt = 0
    for pkg,count in packages.items():
        processed[pkg] = count
        print "Added",pkg, len(packages)+len(new_packages)-cnt, "remaining"
        cnt = cnt + 1
        for child in listdeps( pkg ):
            if child in processed:
                processed[child] += count
            else:
                new_packages[child] = count
    packages = new_packages

runcmd( "rm -rf build && mkdir -p build" )
filetypes = {}
for pkg,count in processed.iteritems():
    print "Downloading ", pkg
    retcode,out,err = runcmd( "( cd build && apt-get source \"%s\" )" % (pkg,) )
    if retcode != 0:
        print >> sys.stderr, "Error downloading and extracting", pkg


for root, dirnames, filenames in os.walk( "build" ):
    if root=='build':
        continue
    for fname in filenames:
        fpath = os.path.join(root,fname)
        try:
                   retcode, out, err = runcmd( "wc \"%s\" && file \"%s\" " % (fpath,fpath) )
                   wcout,fileout = out.split('\n')[0:2]
                   svec = [ t for t in wcout.strip().split(' ') if t]
                   lines, words, chars = [ int(t.strip()) for t in svec[0:3] ]
                   fnrep,ftype = fileout.split( ":", 1 )
                   group = filegroup( ftype )
                   print "\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d,%d" % ( pkg,group,ftype,fpath, lines, words, chars, count )

                   ft = filetypes.get(group) or (0,0,0,0,0)
                   filetypes[group] = (ft[0]+lines,ft[1]+words,ft[2]+chars, ft[3]+1, ft[4]+count)

        except Exception, e:
                   print fpath, ":", e
    #runcmd( "rm -rf build" )

with open( 'result.json', 'w' ) as fout:
    print >> fout, json.dumps( filetypes, sort_keys=True, indent=4 )

for pkgname,stats in sorted( filetypes.items(), key = lambda x: x[1][0] ):
    print "\"%-30s\",%7d,%7d,%7d,%7d,%7d" % (pkgname, stats[0], stats[1], stats[2],stats[3],stats[4])
