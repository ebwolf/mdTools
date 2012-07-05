"""

   AggAccuracy.py 
   
      Aggregate accuracy metrics metadata based on footprints in 
      the second input file



"""

import sys
from SimpleStats import median, mode, mean, stddev

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
suFC = sys.argv[2]         # Spatial units to aggregate to

aggAttr = 'Accuracy'       # Field to be aggregated

desc = gp.Describe(suFC)
gp.workspace = desc.Path

OIDFieldName = desc.OIDFieldName

# Output Feature Class: just append '_Accuracy_Result' to spatial unit
outFC = desc.BaseName + '_Accuracy_Result'

gp.AddMessage('Creating output feature class: ' + outFC)

# Make sure the output doesn't already exist
if gp.Exists(outFC):
    gp.Delete(outFC)
    
gp.CopyFeatures(suFC, outFC)

# Metadata fields are all the same type
newFields = ['maCount', 'maMin', 'maMax', 'maSum', \
             'maMean', 'maMedian', 'maMode', 'maSD']
fields = desc.Fields

for f in newFields:
    if f not in fields:
        gp.AddField(outFC, f, 'DOUBLE')
        
gp.MakeFeatureLayer(outFC, 'footprint')
gp.MakeFeatureLayer(inFC, 'input')

gp.AddMessage('Calculating Statistics.')

suCur = gp.UpdateCursor(outFC)

suRow = suCur.Next()

#print "OID, count, min, max, sum, mean, median, mode, sd"
    
while suRow:
    fpID = suRow.GetValue(OIDFieldName)
    
    sql = OIDFieldName + " = " + str(fpID)
    #print sql
    gp.SelectLayerByAttribute('footprint', 'NEW_SELECTION', sql)
    
    gp.SelectLayerByLocation('input', \
                             'WITHIN', \
                             'footprint', \
                             '#', \
                             'NEW_SELECTION')
    

    inCur = gp.SearchCursor('input')
    inRow = inCur.Next()
    
    agList = []
    
    # Loop through each input feature inside the aggregation unit
    while inRow:
        attr = inRow.GetValue(aggAttr)
        
        if attr is not None:
            agList.append(attr)
        
        inRow = inCur.Next()


    del inRow
    del inCur

    if len(agList) > 0:
        # Calculate the descriptive statistics for this aggregation unit
        lmean = mean(agList)
        lmedian = median(agList)
        lmode = mode(agList)
        lsd = stddev(agList)
        
        #print "OID, count, min, max, sum, mean, median, mode, sd"
        #print str(fpID) + "," + str(len(agList)) + "," + \
        #      str(min(agList)) + "," + str(max(agList)) + "," + \
        #      str(sum(agList)) + "," + str(mean) + "," + \
        #      str(median) + "," + str(modes[1][0]) + "," + str(sd)
        
        suRow.SetValue('maCount', len(agList))
        suRow.SetValue('maMin', min(agList))
        suRow.SetValue('maMax', max(agList))
        suRow.SetValue('maSum', sum(agList))
        suRow.SetValue('maMean', lmean)
        suRow.SetValue('maMedian', lmedian)
        suRow.SetValue('maMode', lmode)
        suRow.SetValue('maSD', lsd)
    else:
        suRow.SetValue('maCount', 0)
        suRow.SetValue('maMin', 0)
        suRow.SetValue('maMax', 0)
        suRow.SetValue('maSum', 0)
        suRow.SetValue('maMean', 0)
        suRow.SetValue('maMedian', 0)
        suRow.SetValue('maMode', 0)
        suRow.SetValue('maSD', 0)
        
    suCur.UpdateRow(suRow)
    
    suRow = suCur.Next()
        
del suRow
del suCur

gp.AddMessage("Done.")

# Pass the resulting dataset back to ArcGIS
gp.SetParameterAsText(2, outFC)
del gp



