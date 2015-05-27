import codecs
import copy
import getopt
import sys
import datetime
import re
import random
from sniffles.regex_generator import *


class AmbiguousNotation(object):

    def __init__(self, notation=None):
        self.notation = notation

    def __str__(self):
        return self.toString()

    def toString(self):
        return self.notation


class RangeNotation(AmbiguousNotation):

    # Range notation should be expressed as [x:y] where
    # x is lower bound and y is upper bound.
    def __init__(self, notation=None):
        self.notation = notation
        self.prefix = notation[0:1]
        self.suffix = notation[-1:]
        myrange = notation[1:-1]
        self.separator = ":"
        bounds = myrange.split(self.separator)
        self.lower_bound = int(bounds[0])
        self.upper_bound = int(bounds[1])
        if self.upper_bound < 1:
            self.upper_bound = 1
        if self.lower_bound > self.upper_bound:
            self.lower_bound = self.upper_bound - 1

    def __str__(self):
        return self.toString()

    def toString(self):
        mylower = random.randint(self.lower_bound, self.upper_bound-1)
        myupper = random.randint(mylower, self.upper_bound)
        mystring = self.prefix + str(mylower) + self.separator + \
            str(myupper) + self.suffix
        return mystring


class ListNotation(AmbiguousNotation):

    # list notation should be [x,y] where x is lower bound and
    # y is upper bound.
    def __init__(self, notation=None):
        self.separator = notation
        self.prefix = notation[0:1]
        self.suffix = notation[-1:]
        mylist = notation[1:-1]
        self.separator = ","
        bounds = mylist.split(self.separator)
        self.lower_bound = int(bounds[0])
        self.upper_bound = int(bounds[1])
        self.max_list_size = 100
        if self.upper_bound < 1:
            self.upper_bound = 1
        if self.lower_bound > self.upper_bound:
            self.lower_bound = self.upper_bound - 1

    def __str__(self):
        return self.toString()

    def toString(self):
        num_elements = random.randint(2, self.max_list_size)
        if num_elements > (self.upper_bound - self.lower_bound):
            print("Error!!!!!")
        myelements = []
        while len(myelements) < num_elements:
            mypick = random.randint(self.lower_bound, self.upper_bound)
            if mypick not in myelements:
                myelements.append(mypick)
        myelements = sorted(myelements)
        mystring = self.prefix
        while myelements:
            myelement = myelements.pop(0)
            mystring += str(myelement)
            if len(myelements) > 0:
                mystring += self.separator
        mystring += self.suffix
        return mystring


class Feature(object):

    def __init__(self, name=None, lower_bound=0, upper_bound=0,
                 complexity_prob=0, ambiguity_list=None):
        self.feature_name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.complexity_prob = complexity_prob
        self.ambiguity_list = ambiguity_list
        if self.upper_bound < 1:
            self.upper_bound = 1
        if self.lower_bound > self.upper_bound:
            self.lower_bound = self.upper_bound - 1

    def __str__(self):
        return self.toString()

    def toString(self):
        complex = False
        mystring = self.feature_name + "="
        if self.complexity_prob > 0 and len(self.ambiguity_list) > 0:
            pick = random.randint(0, 100)
            if pick <= self.complexity_prob:
                complex = True
        if complex:
            pick = random.randint(0, len(self.ambiguity_list)-1)
            mystring += str(self.ambiguity_list[pick])
        else:
            mystring += str(random.randint(self.lower_bound, self.upper_bound))
        return mystring


class ContentFeature(Feature):
    def __init__(self, name="content", regex=True, complexity_prob=0, len=0):
        self.feature_name = name
        self.regex = regex
        self.complexity_prob = complexity_prob
        self.length = len

    def __str__(self):
        return self.toString()

    def toString(self):
        mystring = self.feature_name + "="
        complex = False
        if self.complexity_prob > 0:
            pick = random.randint(0, 100)
            if pick <= self.complexity_prob:
                complex = True
        if self.regex:
            mystring += "/"

        if complex:
            mystring += regex_generator.generate_regex(self.length, 0,
                                                       [60, 30, 10],
                                                       None, None,
                                                       [20, 20, 40, 20],
                                                       50, 30)
        else:
            mystring += regex_generator.generate_regex(self.length, 0,
                                                       [100, 0, 0],
                                                       [20, 35, 20, 20, 0],
                                                       None, None, 0, 0)
        if self.regex:
            mystring += "/"
            if complex:
                pick = random.randint(0, 100)
                if pick > 50:
                    mystring += "i"
                if pick > 75:
                    mystring += "m"
                if pick > 85:
                    mystring += "s"
        return mystring


class ProtocolFeature(Feature):

    def __init__(self, name="proto", proto_list=None, complexity_prob=0,
                 ambiguity_list=None):
        self.feature_name = name
        self.proto_list = proto_list
        self.complexity_prob = complexity_prob
        self.ambiguity_list = ambiguity_list

    def __str__(self):
        return self.toString()

    def toString(self):
        complex = False
        if self.complexity_prob > 0 and self.ambiguity_list is not None:
            pick = random.randint(0, 100)
            if pick <= self.complexity_prob:
                complex = True
        if complex:
            myproto = str(self.ambiguity_list[random.randint(0,
                          len(self.ambiguity_list)-1)])
        else:
            myproto = self.proto_list[random.randint(0,
                                      len(self.proto_list)-1)]
        mystring = self.feature_name + "=" + myproto
        return mystring


class IPFeature(Feature):

    def __init__(self, name="ip", version=4, complexity_prob=0):
        self.name = name
        self.version = version
        self.complexity_prob = complexity_prob

    def __str__(self):
        return self.toString()

    def toString(self):
        mystring = self.name + "="
        myip = []
        complex = False
        if self.complexity_prob > 0:
            pick = random.randint(0, 100)
            if pick <= self.complexity_prob:
                complex = True
        if complex:
            totalbytes = 4
            if self.version == 6:
                totalbytes = 16
            mynetmask = random.randint(0, totalbytes*8)
            myprefixbytes = int(mynetmask / 8)
            myremainder = mynetmask % 8
            mask = ((2**myremainder)-1) << (8 - myremainder)
            index = 0
            while index < myprefixbytes:
                if self.version == 4:
                    myip.append(random.randint(0, 255))
                else:
                    if (myprefixbytes - index) > 1:
                        myip.append(random.randint(0, 65535))
                        index += 1
                    else:
                        break
                index += 1
            mypartialbyte = (random.randint(0, 255) & mask)
            last_bytes = totalbytes - myprefixbytes
            if (myprefixbytes - index) == 1:
                mypartialbyte += (random.randint(0, 255)) << 8
            elif self.version == 6:
                mypartialbyte = mypartialbyte << 8
            if mypartialbyte > 0:
                myip.append(mypartialbyte)
                last_bytes -= 1
            while last_bytes > 0:
                myip.append(0)
                last_bytes -= 1
                if self.version == 6:
                    last_bytes -= 1
            if self.version == 4:
                myipstring = '.'.join(['%d' % byte for byte in myip])
            else:
                myipstring = ':'.join(['%04x' % byte for byte in myip])
            myipstring += "/" + str(mynetmask)
        else:
            if self.version == 4:
                for i in range(0, 4):
                    myip.append(random.randint(0, 255))

            elif self.version == 6:
                myip.append(0x2001)
                myip.append(random.randint(0x0000, 0x01F8) + 0x400)
                for i in range(0, 6):
                    myip.append(random.randint(0, 65535))
            else:
                print("Error, no IP version: ", self.version)
            if self.version == 4:
                myipstring = '.'.join(['%d' % byte for byte in myip])
            else:
                myipstring = ':'.join(['%04x' % byte for byte in myip])
        mystring += myipstring
        return mystring

# Features are defined in a semi-colon separated list one feature per line
#   type=feature; list of arguments in key=value pairs, lists using
#                 python formatting (i.e. [a, ..., z]
#   types are:
#     1. Feature -- generic feature
#     2. Content -- Content Feature
#     3. IP -- IP Feature
#     4. Protocol -- Protocol Feature
#
#     ambiguous features should be written as lists like [x:y]
#       for a range, [x,y] for a list with maximum of 10
#       or just * for a wildcard or similar single option.


class FeatureParser(object):

    def __init__(self, filename=None):
        self.features = []
        self.parseFile(filename)

    def parseFile(self, filename=None):
        if filename is not None:
            try:
                fd = codecs.open(filename, 'r', encoding='utf-8')
            except Exception as err:
                print("Could not read feature file.")
                print(err)
                return False
            line = fd.readline()
            while line:
                self.parseLine(line)
                line = fd.readline()
            fd.close()
            return True
        return False

    def getFeatures(self):
        return self.features

    def parseLine(self, line=None):
        if line:
            myelements = line.split(';')
            mypairs = {}
            while myelements:
                element = myelements.pop(0).strip()
                if element:
                    values = element.split('=')
                    mypairs[values[0].strip().lower()] = values[1].strip()
            myfeature = None
            name = None
            lower_bound = 0
            upper_bound = 0
            complexity_prob = 0
            ambiguity_list = None
            regex = False
            len = 0
            proto_list = None
            version = 4
            if 'name' in mypairs:
                name = mypairs['name']
            if 'lower_bound' in mypairs:
                lower_bound = int(mypairs['lower_bound'])
            if 'upper_bound' in mypairs:
                upper_bound = int(mypairs['upper_bound'])
            if 'complexity_prob' in mypairs:
                complexity_prob = int(mypairs['complexity_prob'])
            if 'ambiguity_list' in mypairs:
                myambiguity_list = self.buildAmbiguityList(
                    mypairs['ambiguity_list'])
            if 'regex' in mypairs:
                if mypairs['regex'] == 'True':
                    regex = True
            if 'len' in mypairs:
                len = int(mypairs['len'])
            if 'proto_list' in mypairs:
                plist = mypairs['proto_list']
                plist = plist[1:-1]
                pvals = plist.split(",")
                proto_list = []
                for p in pvals:
                    proto_list.append(p)
            if 'version' in mypairs:
                version = int(mypairs['version'])

            if 'type' not in mypairs:
                print("feature type Not specified:", line)
                return None
            if mypairs['type'].lower() == 'feature':
                myfeature = Feature(name, lower_bound, upper_bound,
                                    complexity_prob, myambiguity_list)
            elif mypairs['type'].lower() == 'content':
                myfeature = ContentFeature(name, regex, complexity_prob, len)
            elif mypairs['type'].lower() == 'ip':
                myfeature = IPFeature(name, version, complexity_prob)
            elif mypairs['type'].lower() == 'protocol':
                myfeature = ProtocolFeature(name, proto_list, complexity_prob,
                                            myambiguity_list)
            else:
                print("Unrecognized feature type.", line)
                return None
            self.features.append(myfeature)

    def buildAmbiguityList(self, list):
        mylist = []
        parsedlist = list[1:-1]
        values = re.split(r",\s", parsedlist)
        myamb = None
        for val in values:
            if ',' in val:
                myamb = ListNotation(val)
            elif ':' in val:
                myamb = RangeNotation(val)
            else:
                myamb = AmbiguousNotation(val)
            mylist.append(myamb)
        return mylist
