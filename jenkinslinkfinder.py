from __future__ import print_function
import os
import time
import re
import sys
import lxml.etree
import lxml.builder
import datetime

#from xml.dom.minidom import parse, parseString
from urllib2 import urlopen, HTTPError
from optparse import OptionParser
from urlparse import urlparse

input_site = ""
inputType = ""
BUILD_ENV = ""

TOTAL_TIME = 0
TOTAL_TESTS = 0
TOTAL_PASSES = 0
TOTAL_FAIL = 0
RESULT = 'passed'


def main():
    if len(sys.argv) < 3:
        print ("NOT ENOUGH PARAMETERS")
        sys.exit()
    
    global BUILD_ENV
    global input_site
    global inputType
    input_site = sys.argv[1]
    inputType = sys.argv[2]
    BUILD_ENV = sys.argv[3]

    if check(input_site):
        print ('INVALID HOSTNAME')
        sys.exit()

    links = getLinks(input_site, inputType)

    print ('LINKS TOTAL: ' + str(len(links)))
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
    #for link in links:
    #    print (link)
    for link in links:
        #print ("CHECKING %d OF %d" %(link_pos,num_links))
        try:
            code = urlopen(link).getcode()
        except HTTPError as e :
            #print('ERROR %d FROM %s' %(e.code, link))
            code = e.code
        except:
            code= 0

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

        link_pos+=1

    #print('TOOK %d SECONDS' % (time.clock() - t0))
        #returns themd httpstatus codes that were seen
    #print(returncodes.keys())
    httpstatus = None
    TOTAL_TIME = str('%d' % (time.clock() - t0))
    writeFile(links,returncodes)


def getLinks(url_string, type_of_link):
    return process(url_string, type_of_link)


def check(site_string):
    if urlopen(site_string).getcode() == 200:
        return False
    else:
        return True

#cleans links
def clean(pattern, url):
    urls = {}
    instances = 0
    for link in pattern:
        if link[0:2] == '//':
            #print('URL does not specify host, prepending http:')
            link = 'http:'+link
        elif link[0] == '/':
            #print('URL does not specify host, prepending '+urlparse(url).hostname)
            link = 'http://'+urlparse(url).hostname+link

    urls[link] = True
    instances += 1
    #print('%d Found link %s' % (instances, link))
    return urls

#Process html into dictionary
def process(url, type_of_link):
    #url = host+page
    #print('Opening %s...' % url)    
    #scrapes the page source
    content = urlopen(url).read()

    #print('Compiling RegExp...')
    if type_of_link == 'LNK':
        #print("link processing RegEx")
        pattern = re.compile(r'<a .*?href=["|\'](?!#)(.+?)["\']');
    elif type_of_link == 'IMG':
        #print("IMG processing for Regex")
        pattern = re.compile(r'<img .*?src=["|\'](?!#)(.+?)["\']');
    # we can avoid duplicates by using a hash - will save time later
    urls = {}
    instances = 0

    for link in pattern.findall(content):

        if link[0:2] == '//':
            #print('URL does not specify host, prepending http:')
            link = 'http:'+link
        elif link[0] == '/':
            #print('URL does not specify host, prepending '+urlparse(url).hostname)
            link = 'http://'+urlparse(url).hostname+link

        urls[link] = True
        instances += 1
        #print('%d Found link %s' % (instances, link))


    #print('Found %d links with %d unique URLs' % (instances, len(urls)))
#list of urls
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
    #print (inputType)
    #parse the dom for input_site and inputType
    
    #output = ROOT(FIELD1(input_site, name=name))
    output = selformat(links,returncodes)

    
    for key in returncodes.keys():
        for link in returncodes[int(key)]:
            #output.append(FIELD2(link,name=str(key)))
            output += "\n<tr class=\" status_done\" style=\"cursor: pointer;\">\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td></td>\n</tr>" %(link,key)

    output += "\n</tbody></table></div></td></tr></table>"

    time_str = str(now.strftime("%Y-%m-%d-%H-%M"))
    timefilename = inputType+"-"
    timefilename = timefilename+str(urlparse(input_site).hostname)
    timefilename = timefilename.replace("\n", "")
    timefilename = timefilename.replace("www.", "")
    timefilename = timefilename.replace(".com", "")
    timefilename+=time_str
    timefilename = timefilename+'.html'

    try:
        #output_temp_file = open("tempLinks.xml", "w+")
        #print (str(lxml.etree.tostring(output, pretty_print=True)), file=output_temp_file)
        #Log File Output
        thepath = "/var/lib/jenkins/jobs/LinkFinder/workspace"# % BUILD_ENV
        #os.makedirs(thepath)        
        pathwithname = os.path.abspath(thepath+"/%s" % (timefilename))
        output_log_file = open(pathwithname, "w+")
        #print (str(lxml.etree.tostring(output, pretty_print=True)), file=output_log_file)
        print (output, file=output_log_file)
        output_log_file.close()
    except Exception, e:
        print("Unable to open file for writing")
        print(e)

def selformat(links,returncode):
    global input_site
    global TOTAL_TESTS
    global TOTAL_TIME
    global TOTAL_PASSES
    global TOTAL_FAIL
    global RESULT
 
    output = "<html>\n<head><style type=\'text/css\'>\nbody, table {\n    font-family: Verdana, Arial, sans-serif;\n    font-size: 12;\n}\n\ntable {\n    border-collapse: collapse;\n    border: 1px solid #ccc;\n}\n\nth, td {\n    padding-left: 0.3em;\n    padding-right: 0.3em;\n}\n\na {\n    text-decoration: none;\n\n}\n\n.title {\n    font-style: italic;\n}\n\n.selected {\n    background-color: #ffffcc;\n}\n\n.status_done {\n    background-color: #eeffee;\n}\n\n.status_passed {\n    background-color: #ccffcc;\n}\n\n.status_failed {\n    background-color: #ffcccc;\n\n}\n\n.breakpoint {\n    background-color: #cccccc;\n    border: 1px solid black;\n}\n</style><title>Test suite results</title></head>\n<body>\n<h1>Test suite results </h1>\n"
    
    output += "\n<table>\n<tr>\n<td>result:</td>\n<td>%s</td>\n</tr>\n<tr>\n<td>totalTime:</td>\n<td>%s</td>\n</tr>\n<tr>\n<td>numTestTotal:</td>\n<td>%s</td> \n</tr>\n<tr>\n<td>numTestPasses:</td>\n<td>%s</td>\n</tr>\n<tr>\n<td>numTestFailures:</td>\n<td>%s</td>\n</tr>\n<tr>\n<td>numCommandPasses:</td>\n<td>0</td>\n</tr>\n<tr>\n<td>numCommandFailures:</td>\n<td>0</td>\n</tr>\n<tr>\n<td>numCommandErrors:</td>\n<td>0</td>\n</tr>\n<tr>\n<td>Selenium Version:</td>\n<td>2.31</td>\n</tr>\n<tr>\n<td>Selenium Revision:</td>\n<td>.0</td>\n</tr>\n<tr>\n<td>\n" % (RESULT, TOTAL_TIME, TOTAL_TESTS, TOTAL_PASSES, TOTAL_FAIL,)

    output+="<table id=\"suiteTable\" class=\"selenium\" border=\"1\" cellpadding=\"1\" cellspacing=\"1\"><tbody>\n<tr class=\"title status_passed\"><td><b>Test Suite</b></td></tr>\n<tr class=\"  status_passed\"><td><a href=\"#testresult0\">smoketest</a></td></tr>\n</tbody></table>\n\n\n</td>\n<td>&nbsp;</td>\n</tr>\n</table><table><tr>\n<td><a name=\"testresult0\">%s</a><br/><div>\n<table border=\"1\" cellpadding=\"1\" cellspacing=\"1\">\n<thead>\n<tr class=\"title status_passed\"><td rowspan=\"1\" colspan=\"3\">%s</td></tr>\n</thead><tbody>\n" % (input_site, input_site,)
    



    return output

main()


"""
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    output +="\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
    output +="\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lan=\"en\" lang=\"en\">"
    output +="\n<head profile=\"http://selenium-ide.openqa.org/prfiles/test-case\">"
    output +="\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />"
    output +="\n<link rel=\"selenium.base\" href=\"%s />"%input_site
    output +="\n<title>%s</title>"%input_site
    output +="\n</head>\n<body>\n<table cellpadding=\"1\" cellspacing=\"1\" border=\"1\">\n<thead>"
    output +="\n<tr><td rowspan=\"1\" colspan=\"3\">%s</td></tr>\n</thead><tbody>"%input_site
"""
