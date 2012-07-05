"""
 
   PrepareData.py - Prepares data for metric metadata creation

      Dissolves on ReachCode, adds fields
   
   
   
"""

import sys

import arcgisscripting
gp = arcgisscripting.create(9.3)   # Old School
gp.overwriteoutput = 1

#
# ArcGIS 10.0 needs the m/z flags explicitly set to disabled
#
gp.outputmflag = "DISABLED"
gp.outputzflag = "DISABLED"

# Get the script parameters
inFC = sys.argv[1]         # Feature Class to be prepped


desc = gp.Describe(inFC)
gp.workspace = desc.Path

fields = desc.Fields

outFC = desc.BaseName + '_prepped'

gp.AddMessage('Creating output feature class: ' + outFC)

gp.AddMessage("Dissolving on ReachCode.")

# Convert Feature Date field to just the year
if 'FeatDate' not in fields:
    gp.AddField(inFC, 'FeatDate', 'LONG')
    
gp.CalculateField_management(inFC, \
                             'FeatDate', \
                             '1900 + int([FDate] / 365)', \
                             'VB')

# Dissolve on ReachCode

if 'ComID' in fields:
    gp.Dissolve_management(inFC, outFC, 'ReachCode', "ComID MAX;FeatDate MIN")
else:
    gp.Dissolve_management(inFC, outFC, 'ReachCode', "FeatDate MIN")
    
gp.AddMessage("Adding fields, calculating lengths.")
    
# Make our fields (if necessary)
desc = gp.Describe(outFC)
fields = desc.Fields

if 'Match' not in fields:
    gp.AddField(outFC, 'Match', 'TEXT')

# Metadata fields are all the same type
newFields = ['Length', 'Error', 'Omission', 'Commission', 'Accuracy']

for f in newFields:
    if f not in fields:
        gp.AddField(outFC, f, 'DOUBLE')

# Calculate lengths        
gp.CalculateField_management(outFC, \
                             'Length', \
                             'round(float(!SHAPE.length@meters!),2)', \
                             'PYTHON')

# Make sure we don't lose the ComID - some datasets don't have them!
if 'ComID' in fields:
    gp.AddField(outFC, 'ComID', 'DOUBLE')
    gp.CalculateField(outFC, 'ComID', '[MAX_ComID]')
    gp.DeleteField(outFC, 'MAX_ComID')

gp.AddField(outFC, 'FeatDate', 'DOUBLE')
gp.CalculateField(outFC, 'FeatDate', '[MIN_FeatDate]')
gp.DeleteField(outFC, 'MIN_FeatDate')
   
gp.AddMessage("Done.")
    
# Pass the resulting dataset back to ArcGIS
gp.SetParameterAsText(1, outFC)
del gp