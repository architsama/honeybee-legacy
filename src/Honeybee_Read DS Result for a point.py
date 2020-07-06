#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Read Daysim result for a test point

-
Provided by Honeybee 0.0.66

    Args:
        _illFilesAddress: List of .ill files
        _testPoints: List of 3d Points
        _annualProfiles: Address to a valid *_intgain.csv generated by daysim.
        _targetPoint: One of the points from the test points
    Returns:
        iIllumLevelsNoDynamicSHD: Illuminance values without dynamic shadings
        iIllumLevelsDynamicSHDGroupI: Illuminance values when shading group I is closed
        iIllumLevelsDynamicSHDGroupII: Illuminance values when shading group II is closed
        iIlluminanceBasedOnOccupancy: Illuminance values based on Daysim user behavior
"""
ghenv.Component.Name = "Honeybee_Read DS Result for a point"
ghenv.Component.NickName = 'readDSHourlyResults'
ghenv.Component.Message = 'VER 0.0.66\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "HB-Legacy"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



import os
import scriptcontext as sc
from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def isAllNone(dataList):
    for item in dataList.AllData():
        if item!=None: return False
    return True


def convertIllFileDaraTreeIntoSortedDictionary(illFilesAddress):
    
    # I should move this function into Honeybee_Honeybee #BadPractice!
    
    shadingGroupsCount = 0
    shadingGroups = []
    
    # get number of shading groups
    for branch in range(illFilesAddress.BranchCount):
        if illFilesAddress.Path(branch).Indices[0] not in shadingGroups:
            shadingGroups.append(illFilesAddress.Path(branch).Indices[0])
            shadingGroupsCount+=1    
    
    illFileSets = {}
    for branch in range(illFilesAddress.BranchCount):
        # sort files inside each branch if they are not sorted
        fileNames = list(illFilesAddress.Branch(branch))
        if illFilesAddress.BranchCount != 1:
            try:
                fileNames = sorted(fileNames, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
            except:
                tmpmsg = "Can't sort .ill files based on the file names. Make sure the branches are sorted correctly."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, tmpmsg)
        
        #convert data tree to a useful dictionary
        shadingGroupNumber = illFilesAddress.Path(branch).Indices[0]
        if shadingGroupNumber not in illFileSets.keys():
            illFileSets[shadingGroupNumber] = []
        
        # create a separate list for each state
        # the structure now is like llFileSets[shadingGroupNumber][[state 1], [state 2],..., [state n]]
        illFileSets[shadingGroupNumber].append(fileNames)
    
    return illFileSets

def main(illFilesAddress, testPoints, targetPoint, annualProfiles):
    msg = str.Empty
    
    shadingProfiles = []
    shadingGroupsCount = 0 # assume there in no shading groups
    
    #groups of groups here
    for resultGroup in  range(testPoints.BranchCount):
        shadingProfiles.append([])
    
    # print len(shadingProfiles)
    if len(annualProfiles)!=0 and annualProfiles[0]!=None:
        # check if the number of profiles matches the number of spaces (point groups)
        if testPoints.BranchCount!=len(annualProfiles):
            msg = "Number of annual profiles doesn't match the number of point groups!\n" + \
                  "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                  "In that case the component will give you the results with no dynamic shadings."
            return msg, None, None
        
        # sort the annual profiles
        try:
            annualProfiles = sorted(annualProfiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
        except:
            pass
        
        # import the shading groups
        # this is a copy-paste from Daysim annual profiles
        for branchCount in range(len(annualProfiles)):
            # open the file
            filePath = annualProfiles[branchCount]
            with open(filePath, "r") as inf:
                for lineCount, line in enumerate(inf):
                    if lineCount == 3:
                        headings = line.strip().split(",")[3:]
                        resultDict = {}
                        for heading in range(len(headings)):
                            resultDict[heading] = []
                    elif lineCount> 3:
                        results = line.strip().split(",")[3:]
                        for resCount, result in enumerate(results):
                            resultDict[resCount].append(float(result))
                            
                shadingCounter = 0
                for headingCount, heading in enumerate(headings):
                    if heading.strip().startswith("blind"):
                        shadingProfiles[branchCount].append(resultDict[headingCount])
                        shadingCounter += 1
        
        # make sure number of ill files matches the number of the shading groups
        # and sort them to work together
        shadingGroups = []
        
        # get number of shading groups
        for branch in range(illFilesAddress.BranchCount):
            if illFilesAddress.Path(branch).Indices[0] not in shadingGroups:
                shadingGroups.append(illFilesAddress.Path(branch).Indices[0])
                shadingGroupsCount+=1
                
        for shadingProfile in shadingProfiles:
            if len(shadingProfile)!= shadingGroupsCount - 1:
                msg = "Number of annual profiles doesn't match the number of shading groups!\n" + \
                      "NOTE: If you have no idea what I'm talking about just disconnect the annual Profiles\n" + \
                      "In that case the component will give you the results with no dynamic shadings."
                return msg, None, None
                    
    elif illFilesAddress.BranchCount > 1 and illFilesAddress.BranchCount-1 != len(annualProfiles):
        tempmsg = "Annual profile files are not provided.\nThe result will be only calculated for the original case with no blinds."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, tempmsg)
    
    illFileSets = convertIllFileDaraTreeIntoSortedDictionary(illFilesAddress)
        
    # find the index of the point
    pointFound = False
    targetPtIndex = 0
    for branch in range(testPoints.BranchCount):
        for pt in testPoints.Branch(branch):
            if pt.DistanceTo(targetPoint) < sc.doc.ModelAbsoluteTolerance:
                pointFound = True
                break
            targetPtIndex+=1
        if pointFound ==True: break
    
    # check number of points in each of the ill files
    # number of points should be the same in all the illfile lists
    # that's why I just try the first list of the ill files
    numOfPtsInEachFile = []
    for illFile in illFileSets[0][0]:
        with open(illFile, "r") as illInf:
            for lineCount, line in enumerate(illInf):
                if not line.startswith("#"):
                    numOfPtsInEachFile.append(len(line.strip().split(" ")) - 4)
                    break
    
    # find the right ill file(s) to look into and read the results
    # print targetPtIndex
    targetListNumber = None
    targetIndexNumber = None
    for listCount, numOfPts in enumerate(numOfPtsInEachFile):
        if sum(numOfPtsInEachFile[:listCount]) >= targetPtIndex + 1:
            targetListNumber = listCount - 1
            targetIndexNumber = targetPtIndex - sum(numOfPtsInEachFile[:listCount-1])
            #print "list number is: ", listCount - 1
            #print "index number is:", targetPtIndex - sum(numOfPtsInEachFile[:listCount-1])
            break
    
    # Probably this is not the best way but I really want to get it done tonight!
    if targetListNumber == None:
        targetListNumber = len(numOfPtsInEachFile)-1
        targetIndexNumber = targetPtIndex - sum(numOfPtsInEachFile[:targetListNumber])
    
    if targetIndexNumber < 0:
        msg = "The target point is not inside the point list"
        return msg, None, None
    
    # find in which space the point is located
    targetSpace = None
    for listCount, numOfPts in enumerate(numOfPtsInEachSpace):
        if sum(numOfPtsInEachSpace[:listCount]) >= targetPtIndex + 1:
            targetSpace = listCount - 1
            break    
    if targetSpace == None:
        targetSpace = len(numOfPtsInEachSpace)-1
    
    # 3 place holderd for the potential 3 outputs
    # no blinds, shading group I and shading group II
    illuminanceValues = {0: [],
                         1: [],
                         2: [],
                         }
                         
    # create a sublist for every shading state
    for shadingGroupCount in range(len(illFileSets.keys())):
        # each file represnts one state of shading
        for resultFile in illFileSets[shadingGroupCount]:
            # add an empty list for each state
            illuminanceValues[shadingGroupCount].append([])
    
    
    for shadingGroupCount in illFileSets.keys():
        for stateCount, targetIllFiles in enumerate(illFileSets[shadingGroupCount]):
            targetIllFile = targetIllFiles[targetListNumber]
            result = open(targetIllFile, 'r')
            for lineCount, line in enumerate(result):
                hourLuxValue = line.strip().split(" ")[targetIndexNumber + 4]
                illuminanceValues[shadingGroupCount][stateCount].append(float(hourLuxValue))
            result.close()
            
                
    return msg, illuminanceValues, shadingProfiles[branch]



if _targetPoint!=None and not isAllNone(_illFilesAddress) and not isAllNone(_testPoints):
    
    _testPoints.SimplifyPaths()
    _illFilesAddress.SimplifyPaths()
    
    numOfPtsInEachSpace = []
    for branch in range(_testPoints.BranchCount):
        numOfPtsInEachSpace.append(len(_testPoints.Branch(branch)))
    
    msg, illuminanceValues, shadingProfile = main(_illFilesAddress, _testPoints, _targetPoint, annualProfiles_)
    
    if shadingProfile!=[]: shadingProfile = shadingProfile[0]
    
    if msg!=str.Empty:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, msg)
        
    else:
        annualIllumNoDynamicSHD = []
        annualIllumDynamicSHDGroupI = DataTree[Object]()
        annualIllumDynamicSHDGroupII = DataTree[Object]()
        iIlluminanceBasedOnOccupancy = []
        
        heading = ["key:location/dataType/units/frequency/startsAt/endsAt",
                    " ", "Annual illuminance values", "lux", "Hourly",
                    (1, 1, 1), (12, 31, 24)]
        
        for shadingGroup in illuminanceValues.keys():
            # results with no blind
            if shadingGroup==0:
                annualIllumNoDynamicSHD.extend(heading + illuminanceValues[0][0])
            
            elif shadingGroup==1 and len(illuminanceValues[1])!=0:
                for shadingState, illumValues in enumerate(illuminanceValues[1]):
                    p = GH_Path(shadingState)
                    annualIllumDynamicSHDGroupI.AddRange(heading, p)
                    annualIllumDynamicSHDGroupI.AddRange(illumValues, p)
            
            elif shadingGroup==2 and len(illuminanceValues[2])!=0:
                for shadingState, illumValues in enumerate(illuminanceValues[2]):
                    p = GH_Path(shadingState)
                    annualIllumDynamicSHDGroupII.AddRange(heading, p)
                    annualIllumDynamicSHDGroupII.AddRange(illumValues, p)

        
        # create the mixed result with the shadings
        if len(shadingProfile)!=0 and len(illuminanceValues[1])!=0:
            mixResults = heading
            
            # for now Honeybee only supports single shading group so the number of
            # states is length of shading group 1
            numberOfStates = len(illuminanceValues[1])
            for HOY, shdProfile in enumerate(shadingProfile):
                if shdProfile == 0:
                    # no blinds
                    mixResults.append(illuminanceValues[0][0][HOY])
                else:
                    stateInEffect = int(round(numberOfStates * shdProfile))
                    mixResults.append(illuminanceValues[1][stateInEffect-1][HOY])
            
            iIlluminanceBasedOnOccupancy = mixResults
            
            if len(illuminanceValues[2])!=0:
                msg = "Honeybee currently only supports one shading group for results visulaization."
            
        
        if msg!=str.Empty:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, msg)