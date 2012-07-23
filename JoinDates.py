"""

   JoinDates.py - Joins features with quads to populate date fields





"""

import sys

import time

start = time.clock()

import arcgisscripting
gp = arcgisscripting.create(9.3)   # Old School
gp.overwriteoutput = 1

#
# ArcGIS 10.0 needs the m/z flags explicitly set to disabled
#
gp.outputmflag = "DISABLED"
gp.outputzflag = "DISABLED"

# Get the script parameters
inFC = sys.argv[1]         # Input feature class
quadFC = sys.argv[2]       # Quads feature class with dates

desc = gp.Describe(inFC)
gp.workspace = desc.Path
                
# Output Feature Class - just append '_dates' to input
outFC = inFC + "_dates"

# Create field mappins
gp.AddMessage("Creating field mappings.")

fm = gp.CreateObject('FieldMappings')
fm.AddTable(inFC)
fm.AddTable(quadFC)

# Remove unwanted fields
for fname in ('AREA', 'PERIMETER', 'Q24KMISS_', 'Q24KMISS_I', \
              'STATE1', 'STATE2', 'STATE3', 'STATE4', 'NAME', \
              'QUADID', 'QuadName', 'Imprint', 'PhotoIns', \
              'PhotoRev', 'FieldCheck', 'Survey', 'Edit'):
    fm.RemoveFieldMap(fm.FindFieldMapIndex(fname))

gp.AddMessage("Joining to quads.")

# Join based on "closest" which gets "most"
gp.SpatialJoin(inFC, quadFC, outFC, '#', '#', fm, 'CLOSEST')

gp.DeleteField(outFC, 'Join_Count')

count = int(gp.GetCount(outFC).GetOutput(0))

elapsed = time.clock() - start
msg = "Processed " + str(count) + " features in " \
    + str(elapsed) + " seconds."

gp.AddMessage(msg)

rate = count / elapsed

msg = "That's a rate of " + str(rate) + " features per second."

gp.AddMessage(msg)
    
# Pass the resulting dataset back to ArcGIS  
gp.SetParameterAsText(2, outFC)
del gp