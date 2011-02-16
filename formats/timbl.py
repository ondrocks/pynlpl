###############################################################
#  PyNLPl - Timbl Classifier Output Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Derived from code by Sander Canisius
#
#       Licensed under GPLv3
# 
# This library offers a TimblOutput class for reading Timbl
# classifier output. It supports full distributions (+v+db) and comment (#)
#
###############################################################    


from sys import stderr
from pynlpl.statistics import Distribution


class TimblOutput:
    """A class for reading Timbl classifier output, supports the +v+db option and ignores comments starting with #"""

    def __init__(self, stream, delimiter = ' ', ignorecolumns = [], ignorevalues = []):
        self.stream = stream
        self.delimiter = delimiter
        self.ignorecolumns = ignorecolumns #numbers, ignore the specified FEATURE columns: first column is 1
        self.ignorevalues = ignorevalues #Ignore columns with the following values

    def __iter__(self):
        # Note: distance parsing (+v+di) works only if distributions (+v+db) are also enabled!
        
        
        for line in self.stream:
            endfvec = None
            line = line.strip()
            if line and line[0] != '#': #ignore empty lines and comments
                segments = [ x for i, x in enumerate(line.split(self.delimiter)) if x not in self.ignorevalues and i+1 not in self.ignorecolumns ]
              
                #segments = [ x for x in line.split() if x != "^" and not (len(x) == 3 and x[0:2] == "n=") ]  #obtain segments, and filter null fields and "n=?" feature (in fixed-feature configuration)
                

                if not endfvec:
                    try:
                        endfvec = segments.index("{")            
                    except ValueError:
                        endfvec = None
                            
                if endfvec > 2: #only for +v+db
                    try:
                        enddistr = segments.index('}',endfvec)
                    except ValueError:
                        raise
                    distribution = self.parseDistribution(segments, endfvec, enddistr)
                    if len(segments) > enddistr + 1:
                        distance = segments[-1]
                    else:
                        distance = None
                else:
                    endfvec = len(segments)
                    distribution = None
                    distance = None
                                    
                #features, referenceclass, predictedclass, distribution, distance
                yield segments[:endfvec - 2], segments[endfvec - 2], segments[endfvec - 1], distribution, distance    
           

    def parseDistribution(self, instance, start,end= None):
        dist = {}
        i = start + 1

        if not end:
            end = len(instance) - 1

        while i < end:  #instance[i] != "}":
            label = instance[i]
            try:
                score = float(instance[i+1].rstrip(","))
                key = label
                dist[key] = score
            except:
                print >>stderr, "ERROR: pynlpl.input.timbl.TimblOutput -- Could not fetch score for class '" + label + "', expected float, but found '"+instance[i+1].rstrip(",")+"'. Attempting to compensate..."
                del dist[key]
                i = i - 1
            i += 2

            
        if not dist:
            print >>stderr, "ERROR: pynlpl.input.timbl.TimblOutput --  Did not find class distribution for ", instance

        return Distribution(dist)

