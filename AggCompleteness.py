"""

 AggCompleteness.py
 
    Aggregate completeness metrics metadata based 
    on footprints in as second input file

      
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
suFC = sys.argv[2]         # Spatial units to aggregate to


desc = gp.Describe(suFC)
gp.workspace = desc.Path

OIDFieldName = desc.OIDFieldName

# Output Feature Class: just append '_Completeness_Result' to spatial unit
outFC = desc.BaseName + '_Completeness_Result'

gp.AddMessage('Creating output feature class: ' + outFC)

# Make sure the output doesn't already exist
if gp.Exists(outFC):
    gp.Delete(outFC)
    
gp.CopyFeatures(suFC, outFC)

# Metadata fields are all the same type
newFields = ['cTotal', 'cMatch', 'cOmissions', 'cCommissions', \
             'lTotal', 'lMatch', 'lOmissions', 'lCommissions', \
             'Completeness' ]
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
    
    gp.SelectLayerByLocation('input', 'WITHIN', \
                             'footprint', '#', 'NEW_SELECTION')
    

    inCur = gp.SearchCursor('input')
    inRow = inCur.Next()
    
    matches = []
    omissions = []
    commissions = []
    
    # Loop through each input feature inside the aggregation unit
    while inRow:
        m = inRow.GetValue('Match_Type')
        
        if m == 'M':
            value = inRow.GetValue('Match_Length')
            matches.append(value)
        elif m == 'C':
            value = inRow.GetValue('Commission_Length')
            commissions.append(value)
        elif m == 'O':
            value = inRow.GetValue('Omission_Length')
            omissions.append(value)
        
        inRow = inCur.Next()

    del inRow
    del inCur

    match_count = len(matches)
    com_count = len(commissions)
    om_count = len(omissions)

    suRow.SetValue('cTotal', match_count + com_count + om_count)
    suRow.SetValue('cMatch', match_count)
    suRow.SetValue('cCommissions', com_count)
    suRow.SetValue('cOmissions', om_count)

    match_sum = sum(matches)
    com_sum = sum(commissions)
    om_sum = sum(omissions)
    total = match_sum + com_sum + om_sum

    suRow.SetValue('lTotal', total)
    suRow.SetValue('lMatch', match_sum)
    suRow.SetValue('lCommissions', com_sum)
    suRow.SetValue('lOmissions', om_sum)
    
    if total != 0:
        suRow.SetValue('Completeness', match_sum / total)
      
    suCur.UpdateRow(suRow)
    
    suRow = suCur.Next()
        
del suRow
del suCur

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



