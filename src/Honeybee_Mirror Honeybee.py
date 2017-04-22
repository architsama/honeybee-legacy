#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Mirror Honeybee Objects

-
Provided by Honeybee 0.0.61

    Args:
        _HBObj: Honeybee surface or Honeybee zone
        _plane: Mirror plane
        keepAdj_: Set to 'True' to have the component preserve adjacencies with other zones.  If set to 'False' or left blank, the existing adjacencies and boundary conditions will be deleted.
    Returns:
        HBObj: Transformed objects
"""
ghenv.Component.Name = "Honeybee_Mirror Honeybee"
ghenv.Component.NickName = 'mirrorHBObj'
ghenv.Component.Message = 'VER 0.0.61\nAPR_21_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "00 | Honeybee"
#compatibleHBVersion = VER 0.0.57\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "6"
except: pass

import scriptcontext as sc
import uuid
import Rhino as rc


def main(HBObj, plane, keepAdj=False):

    # import the classes
    if not sc.sticky.has_key('honeybee_release'):
        print "You should first let Honeybee fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
        return -1
    
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    # call the objects from the lib
    hb_hive = sc.sticky["honeybee_Hive"]()
    try:
        HBObject = hb_hive.callFromHoneybeeHive(HBObj)
    except:
        raise TypeError("Wrong input type for _HBObj. Connect a Honeybee Surface or a HoneybeeZone to HBObject input")
    
    if keepAdj == False:
        clearBC = True
    else:
        clearBC = False
    
    # create a transform
    transform = rc.Geometry.Transform.Mirror(plane)
    newKey = str(uuid.uuid4())[:8]
    
    for HObj in HBObject:
        HObj.transform(transform, newKey, clearBC, True)
        if HObj.objectType == 'HBZone':
            HObj.checkZoneNormalsDir()
    
    HBObj = hb_hive.addToHoneybeeHive(HBObject, ghenv.Component)

    return HBObj
    
if _HBObj and _plane:
    result = main(_HBObj, _plane, keepAdj_)
    
    if result!=-1:
        HBObj = result