"""

 AggCompleteness.py
 
    Aggregate completeness metrics metadata based 
    on footprints in as second input file

      
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
        m = inRow.GetValue('Match')
        
        if m == 'M':
            value = inRow.GetValue('Length')
            matches.append(value)
        elif m == 'C':
            value = inRow.GetValue('Commission')
            commissions.append(value)
        elif m == 'O':
            value = inRow.GetValue('Omission')
            omissions.append(value)
        
        inRow = inCur.Next()

    del inRow
    del inCur

    suRow.SetValue('cTotal', len(matches) + len(commissions) + len(omissions))
    suRow.SetValue('cMatch', len(matches))
    suRow.SetValue('cCommissions', len(commissions))
    suRow.SetValue('cOmissions', len(omissions))

    suRow.SetValue('lTotal', sum(matches) + sum(commissions) + sum(omissions))
    suRow.SetValue('lMatch', sum(matches))
    suRow.SetValue('lCommissions', sum(commissions))
    suRow.SetValue('lOmissions', sum(omissions))
  
    suRow.SetValue('Completeness', \
                   sum(matches) / \
                   (sum(matches) + sum(omissions) + sum(commissions)) )
  
    suCur.UpdateRow(suRow)
    
    suRow = suCur.Next()
        
del suRow
del suCur

gp.AddMessage("Done...")

# Pass the resulting dataset back to ArcGIS
gp.SetParameterAsText(2, outFC)
del gp



