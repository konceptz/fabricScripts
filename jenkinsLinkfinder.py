#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import import
time re
import sys
import lxml.etree
import lxml.builder
import datetime
import threading
# from xml.dom.minidom import parse, parseString

from urllib2 import urlopen, HTTPError
from optparse import OptionParser
from urlparse import urlparse


input_site = ''
inputType = ''
BUILD_ENV = ''

TOTAL_TIME = 0
TOTAL_TESTS = 0
TOTAL_PASSES = 0
TOTAL_FAIL = 0
RESULT = 'passed'


def main():
    if len(sys.argv) < 3:
        print('NOT ENOUGH PARAMETERS')
        sys.exit()

    global BUILD_ENV
    global input_site
    global inputType
    input_site = sys.argv[1]
    inputType = sys.argv[2]
    BUILD_ENV = sys.argv[3]

    if check(input_site):
        print('INVALID HOSTNAME')
        sys.exit()

    links = getLinks(input_site, inputType)

    print('LINKS TOTAL: ' + str(len(links)))
    output(links)


def output(links):
    global TOTAL_TESTS
    global TOTAL_TIME
    global TOTAL_PASSES
    global TOTAL_FAIL
    global RESULT
    returncodes = {}
    link_pos = 1
    num_links = len(links)
    TOTAL_TESTS = num_links
    t0 = time.clock()

    # for link in links:
    #    print (link)

    for link in links:

        # print ("CHECKING %d OF %d" %(link_pos,num_links))

        try:
            code = urlopen(link).getcode()
        except HTTPError, e:

            # print('ERROR %d FROM %s' %(e.code, link))

            code = e.code
        except:
            code = 0

        if code in returncodes:
            returncodes[code].append(link)
        else:
            returncodes[code] = [link]
        if code == 200:
            TOTAL_PASSES += 1
        elif code == 404 or code == 0:
            RESULT = 'failed'
            TOTAL_FAIL += 1
        else:
            TOTAL_FAIL += 1

        link_pos += 1

    # print('TOOK %d SECONDS' % (time.clock() - t0))
        # returns themd httpstatus codes that were seen
    # print(returncodes.keys())

    httpstatus = None
    TOTAL_TIME = str('%d' % (time.clock() - t0))
    writeFile(links, returncodes)


def getLinks(url_string, type_of_link):
    return process(url_string, type_of_link)


def check(site_string):
    if urlopen(site_string).getcode() == 200:
        return False
    else:
        return True


# cleans links

def clean(pattern, url):
    urls = {}
    instances = 0
    for link in pattern:
        if link[0:2] == '//':

            # print('URL does not specify host, prepending http:')

            link = 'http:' + link
        elif link[0] == '/':

            # print('URL does not specify host, prepending '+urlparse(url).hostname)

            link = 'http://' + urlparse(url).hostname + link

    urls[link] = True
    instances += 1

    # print('%d Found link %s' % (instances, link))

    return urls


# Process html into dictionary

def process(url, type_of_link):

    # url = host+page
    # print('Opening %s...' % url)
    # scrapes the page source

    content = urlopen(url).read()

    # print('Compiling RegExp...')

    if type_of_link == 'LNK':

        # print("link processing RegEx")

        pattern = re.compile(r'<a .*?href=["|\'](?!#)(.+?)["\']')
    elif type_of_link == 'IMG':

        # print("IMG processing for Regex")

        pattern = re.compile(r'<img .*?src=["|\'](?!#)(.+?)["\']')

    # we can avoid duplicates by using a hash - will save time later

    urls = {}
    instances = 0

    for link in pattern.findall(content):

        if link[0:2] == '//':

            # print('URL does not specify host, prepending http:')

            link = 'http:' + link
        elif link[0] == '/':

            # print('URL does not specify host, prepending '+urlparse(url).hostname)

             link = 'http://' + urlparse(url).hostname + link

        urls[link] = True
        instances += 1

        # print('%d Found link %s' % (instances, link))

    # print('Found %d links with %d unique URLs' % (instances, len(urls)))
# list of urls

    return urls.keys()


def writeFile(links, returncodes):
    global inputType
    global input_site
    global BUILD_ENV

    E = lxml.builder.ElementMaker()
    ROOT = E.root
    DOC = E.doc
    FIELD1 = E.Base
    FIELD2 = E.Code
    now = datetime.datetime.now()

    # print (inputType)
    # parse the dom for input_site and inputType

    # output = ROOT(FIELD1(input_site, name=name))

    output = selformat(links, returncodes)

    for key in returncodes.keys():
        for link in returncodes[int(key)]:

            # output.append(FIELD2(link,name=str(key)))

            output += \
                '''
<tr class=" status_done" style="cursor: pointer;">
\t<td>%s</td>
\t<td>%s</td>
\t<td></td>
</tr>''' \
                % (link, key)

    output += '\n</tbody></table></div></td></tr></table>'

    time_str = str(now.strftime('%Y-%m-%d-%H-%M'))
    timefilename = inputType + '-'
    timefilename = timefilename + str(urlparse(input_site).hostname)
    timefilename = timefilename.replace('\n', '')
    timefilename = timefilename.replace('www.', '')
    timefilename = timefilename.replace('.com', '')
    timefilename += time_str
    timefilename = timefilename + '.html'

    try:

        # output_temp_file = open("tempLinks.xml", "w+")
        # print (str(lxml.etree.tostring(output, pretty_print=True)), file=output_temp_file)
        # Log File Output

        thepath = '/var/lib/jenkins/jobs/LinkFinder/workspace'  # % BUILD_ENV

        # os.makedirs(thepath)

        pathwithname = os.path.abspath(thepath + '/%s' % timefilename)
        output_log_file = open(pathwithname, 'w+')

        # print (str(lxml.etree.tostring(output, pretty_print=True)), file=output_log_file)

        print(output, file=output_log_file)
        output_log_file.close()
    except Exception, e:
        print('Unable to open file for writing')
        print(e)


def selformat(links, returncode):
    global input_site
    global TOTAL_TESTS
    global TOTAL_TIME
    global TOTAL_PASSES
    global TOTAL_FAIL
    global RESULT

    output = \
        """<html>
<head><style type=\'text/css\'>
body, table {
    font-family: Verdana, Arial, sans-serif;
    font-size: 12;
}

table {
    border-collapse: collapse;
    border: 1px solid #ccc;
}

th, td {
    padding-left: 0.3em;
    padding-right: 0.3em;
}

a {
    text-decoration: none;

}

.title {
    font-style: italic;
}

.selected {
    background-color: #ffffcc;
}

.status_done {
    background-color: #eeffee;
}

.status_passed {
    background-color: #ccffcc;
}

.status_failed {
    background-color: #ffcccc;

}

.breakpoint {
    background-color: #cccccc;
    border: 1px solid black;
}
</style><title>Test suite results</title></head>
<body>
<h1>Test suite results </h1>
"""

    output += \
        '''
<table>
<tr>
<td>result:</td>
<td>%s</td>
</tr>
<tr>
<td>totalTime:</td>
<td>%s</td>
</tr>
<tr>
<td>numTestTotal:</td>
<td>%s</td> 
</tr>
<tr>
<td>numTestPasses:</td>
<td>%s</td>
</tr>
<tr>
<td>numTestFailures:</td>
<td>%s</td>
</tr>
<tr>
<td>numCommandPasses:</td>
<td>0</td>
</tr>
<tr>
<td>numCommandFailures:</td>
<td>0</td>
</tr>
<tr>
<td>numCommandErrors:</td>
<td>0</td>
</tr>
<tr>
<td>Selenium Version:</td>
<td>2.31</td>
</tr>
<tr>
<td>Selenium Revision:</td>
<td>.0</td>
</tr>
<tr>
<td>
''' \
        % (RESULT, TOTAL_TIME, TOTAL_TESTS, TOTAL_PASSES, TOTAL_FAIL)

    output += \
        '''<table id="suiteTable" class="selenium" border="1" cellpadding="1" cellspacing="1"><tbody>
<tr class="title status_passed"><td><b>Test Suite</b></td></tr>
<tr class="  status_passed"><td><a href="#testresult0">smoketest</a></td></tr>
</tbody></table>


</td>
<td>&nbsp;</td>
</tr>
</table><table><tr>
<td><a name="testresult0">%s</a><br/><div>
<table border="1" cellpadding="1" cellspacing="1">
<thead>
<tr class="title status_passed"><td rowspan="1" colspan="3">%s</td></tr>
</thead><tbody>
''' \
        % (input_site, input_site)

    return output


main()

