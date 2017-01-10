#! /usr/bin/python3
# # openvas_py_cli.py
# ###################################
# #  __  __  ____  _  _ ___   ____  #
# #  \ \_\ \ \ .,\ \\//  //  //__   #
# #   \_\`\_\ \_\_\ ||  //_ //___   #
# ###################################
# # OpenVAS Python (3) CLI Manageer #
# # Project started 12/28/2016      #
# ###################################
## Static Variables:
ovpnUser = 'admin'      #Your OpenVAS username
ovpnPass = '' 		#Your OpenVAS password
ovpnIP = '127.0.0.1'    #OpenVAS IP (localhost)
ovpnPort = '9390'       #OpenVAS port (9390 is default)
ovpnAuth = "omp -u " + ovpnUser + " -w " + ovpnPass + " -h " + ovpnIP + " -p " + ovpnPort

## Testing Variables:
outFilePath = '~/'

## Imports
import subprocess
import base64
from lxml import etree
from io import StringIO, BytesIO

## Functions
def runCommand(command):
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmdOutput = cmd.stdout.readlines()
    #cmd.stdin.close()
    cmd.wait()
    return cmdOutput

def listXML(rootXML):
    for i in range(0, len(rootXML)): #step through depth (max depth = len(rootXML))
        print(rootXML[i].tag + " " + str(rootXML[i].attrib)) # print XML tag (should already be string) and print XML attribute(s) (attributes are in dictionary form)

def parseXML(cmdResult):
    parser = etree.XMLParser()
    for line in cmdResult:
        parser.feed(((line.decode('utf-8').rstrip("\n\r")).strip()))
    return parser.close()

def getReportFormats(): # Get OMP report formats (2.0 only) output is NOT XML
    rptFormats = runCommand(ovpnAuth + " -F")
    class ReportFormat(object):
        def __init__(self, fmtname, fmtcode):
            self.fmtname = fmtname
            self.fmtcode = fmtcode
    rptFormatsDict = {} # declare dict
    rptFormatsTable = [] # declare list
    for formats in rptFormats:
        intrasplit = str(formats.decode('utf-8').rstrip("\n\r")).split('  ') # Create a list of fmt code and fmt name
        rptFormatsTable.append(ReportFormat(intrasplit[1], intrasplit[0])) # Create table of ReportFormat classes
    rptFormatsDict = dict([ (r.fmtname, r.fmtcode) for r in rptFormatsTable ]) # Create dict of format names and codes
    return rptFormatsDict

def getTxtRpt(rptOnID):
    rptFormatsDict = getReportFormats() # get OMP report formats
    txt_fmtcode = str(rptFormatsDict.get("TXT")) # Save code for text format
    commandStr = ovpnAuth + ' -i -X \'<get_reports report_id="' + rptOnID + '" format_id="' + txt_fmtcode + '"/>\''
    XMLList_rootXML = parseXML(runCommand(commandStr))
    for element in XMLList_rootXML:
        if str(element.tag) == "report":
            report_base64 = str(element.text)
    return base64.b64decode(report_base64)

def getTargets():
    cmdResult = runCommand(ovpnAuth + " -i -X '<get_targets/>'")
    rootXML = parseXML(cmdResult) # get rootXML from cmdResult
    parser = etree.XMLParser(ns_clean=True)
    tree = etree.parse(StringIO((etree.tostring(rootXML)).decode('utf-8')), parser)
    targetXML = tree.xpath('/get_targets_response/target/name')
    target_names = []
    for t in targetXML:
        target_names.append(t.text)

    return target_names


def getConfigs(): # return config formats as a dictionary
    vasConfigs = runCommand(ovpnAuth + " -i -X '<get_configs/>'")
    cfgsXML = parseXML(vasConfigs) # get root XML from vasConfigs
    config_ids = []
    for i in range(0, (len(cfgsXML))):
        if cfgsXML[i].tag == "config":
            config_ids.append(str(cfgsXML[i].attrib.get("id")))

    config_names = []
    for l in cfgsXML.xpath('/get_configs_response/config/name'):
        config_names.append(str(l.text))

    class ConfigFormat(object):
        def __init__(self, fmtcode, fmtname):
            self.fmtcode = fmtcode
            self.fmtname = fmtname

    cfgFormatsDict = {} # declare dict for Configs
    cfgFormatsTable = [] # declare list for Configs

    if len(config_ids) == len(config_names): # check to make sure that our list lengths match (need to find a better way to read XML element)
        for i in range(0, (len(config_ids))):
            cfgFormatsTable.append(ConfigFormat(config_ids[i], config_names[i])) # Create table of ConfigFormat classes
            
        cfgFormatsDict = dict([ (c.fmtcode, c.fmtname) for c in cfgFormatsTable ]) # Create dict of config codes and names
        return cfgFormatsDict
    
def getReports(): # Get OpenVAS reports, return dict
    reportsXMLList = runCommand(ovpnAuth + " -i -X '<get_reports/>'")
    reports_rootXML = parseXML(reportsXMLList)
    parser = etree.XMLParser(ns_clean=True)
    tree = etree.parse(StringIO((etree.tostring(reports_rootXML)).decode('utf-8')), parser)
    report_ids = [] # declare report IDs list
    for i in range(0, (len(reports_rootXML))):
        if reports_rootXML[i].tag == "report":
            report_ids.append(str(reports_rootXML[i].attrib.get("id")))
    
    report_names = [] # declare report names list (these are not actually OpenVAS report names, these are the task names)
    for taskName in tree.xpath('/get_reports_response/report/task/name'):
        report_names.append(str(taskName.text))
    
    class VASReports(object):
        def __init__(self, rptid, rptname):
            self.rptid = rptid
            self.rptname = rptname
    
    VASReportsDict = {} # declare dict for Reports
    VASReportsTable = [] # declare list for Reports
    if len(report_ids) == len(report_names):
        for j in range(0, (len(report_ids))):
            VASReportsTable.append(VASReports(report_ids[j], report_names[j]))
    
        VASReportsDict = dict([ (r.rptid, r.rptname) for r in VASReportsTable ]) # Create dict of report codes and task names
    return VASReportsDict


## Get OpenVAS targets
print("OpenVAS targets:")
target_names = getTargets()
for t in target_names:
    print(t)

## Get OpenVAS configs
print("Full and fast config:")
configDict = getConfigs()
print(list(configDict.keys())[list(configDict.values()).index("Full and fast")]) # attempt to find dictionary key from definition

## Get OpenVAS report formats
#rptFormatsDict = getReportFormats()
#txt_fmtcode = str(rptFormatsDict.get("TXT")) # Save code for text format

def reportsMenu(rptsDict):
    class rptMenuItem(object):
        def __init__(self, menuIndex, rptid, rptname):
            self.menuIndex = menuIndex
            self.rptid = rptid
            self.rptname = rptname
    
    menuCount = 1
    menuList = [] # Menu list for rptMenuItem class objects
    menuDict = {} # Menu dictionary for looking up report IDs
    for k, v in rptsDict.items():
        menuList.append(rptMenuItem(menuCount, k, v))
        menuCount = menuCount + 1
    
    menuDict = dict([ (m.menuIndex, m.rptid) for m in menuList ]) # Create dict of report codes and task names

    for menuItem in menuList:
        print("%s\t%s\t%s" % (menuItem.menuIndex, menuItem.rptid, menuItem.rptname))
    
    choice = input("Which report do you want to read: ")
    rptID = menuDict[int(choice)]
    #rptID = menuList[int(choice)].rptid
    return rptID


## Get OpenVAS reports
print("OpenVAS reports:")
reportDict = getReports() # get dict of report IDs and task names
rptID = reportsMenu(reportDict) # list menu of reports

#rptID = ""
# for k, v in reportDict.items():
#     print("%s\t%s" % (k, v)) # print the ids and report names
#     #rptID = k

# rptID = list(reportDict.keys())[list(reportDict.values()).index("BigB0x")] # set the report ID from the report name
## Get Single report TXT
# ToDo: Create a menu to drive selection
#rptIndex = 1
#rptID = report_ids[rptIndex] # For test purposes we are just grabbing the first report on the list

## Output OpenVAS report text
showRptYN = input("Do you want to view the report for %s [y/N]: " % (reportDict[rptID]))
if showRptYN[:1].lower() == "y":
    print("OpenVAS report for %s:" % (reportDict[rptID]))
    decodedRpt = getTxtRpt(rptID) # decode report
    print(decodedRpt.decode('utf-8')) # print decoded report


#print(decodedReport.decode('utf-8')) # display the decoded report
# Export decoded report to file.txt
# outFilePath = outFilePath + str(report_ids[rptIndex]) + ".txt"
# outFile = open(outFilePath, 'w') # Open the output file with the 'w' write flag
# outFile.write(decodedReport.decode('utf-8')) # Write out the file as utf-8

#################
## ToDo Notes:
## ToDo (part 1 - reporting)
#
## Get report ouput formats (Save to dict) ~Done
#   (currently text only , not xml)
#    ovpnAuth + " -F"
#
## Get OpenVAS configs ~Done
#   ovpnAuth + " -i -X '<get_configs/>'"
#
## Get OpenVAS targets ~Done
#   ovpnAuth + " -i -X '<get_targets/>'"
#
## Get OpenVAS tasks
#   ovpnAuth + " -i -X '<get_tasks/>'"
#
## Get OpenVAS reports ~Done
#   ovpnAuth + " -i -X '<get_reports/>'"
#
## Get OpenVAS report text ~Done
#   ovpnAuth + ' -i -X \'<get_reports report_id="' + rptOnID + '" format_id="' + txt_fmtcode + '"/>\''
#
## ToDo (part 2 - interaction)
## Transform into a fully dynamic tool based on omp -xml='<help/>' # to allow for future flexibility
#
## Create OpenVAS targets
# <create_target/>
#
## Create OpenVAS tasks
# <create_task/>
#
## Create OpenVAS configs
# <create_config/>

#parser3 = etree.XMLParser(ns_clean=True) # POC reverse
#tree3 = etree.parse(StringIO((etree.tostring(rootXML)).decode('utf-8')), parser3) # POC reverse

#print(etree.tostring(rootXML))
#print(rootXML[0].attrib)

#listXML(rootXML)
#print(etree.tostring(tree))

#rootXML[0].tag = target

#for i in range (0, len(rootXML)): #step through depth (max depth = len(rootXML))
#    print(rootXML[i].tag) #print XML tag (should be a string)
#    print(rootXML[i].attrib) #print XML attribute (attributes are in dictionary form)
#    #rootXML[i].attrib('id')

#####################
## Legacy debug code

#for line in info:
#    print(line.decode('utf-8'), end='') # end='' done to prevent duplicating new lines

#tree = etree.parse(info)
#rootXML = tree.getroot()
#rootXML[0]

#print(etree.tostring(rootXML, encoding='unicode', pretty_print=True))
#listXML(rootXML) # list tag & attrib
#tree = etree.ElementTree(rootXML) # To allow elemental traversal
## Some XPath stuff