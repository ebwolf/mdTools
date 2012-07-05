""" 
   
   CalculateAccuracy.py - Calculates positional accuracy and completeness

      Uses the Hunter-Goodchild Simple Positional Accuracy as described in

      Completeness is calculated as length of omissions and commissions

"""

import sys, os

import arcgisscripting
gp = arcgisscripting.create(9.3)   # Old School
gp.overwriteoutput = 1

#
# ArcGIS 10.0 needs the m/z flags explicitly set to disabled
#
gp.outputmflag = "DISABLED"
gp.outputzflag = "DISABLED"

# Get the script parameters
testFC = sys.argv[1]       # Test feature class
refFC = sys.argv[2]        # Reference feature class
tolerance = sys.argv[3]    # Buffer tolerance for accuracy

desc = gp.Describe(testFC)
gp.workspace = desc.Path
                
fields = desc.Fields

gp.AddMessage("Selecting matching features.")

gp.MakeFeatureLayer(testFC, 'test')
gp.MakeFeatureLayer(refFC, 'ref')

#
# Find matching features based on ReachCode in test and reference
#
sql = '"ReachCode" IN (SELECT "ReachCode" FROM ' \
    + os.path.basename(refFC) + ')'
gp.MakeFeatureLayer('test', 'tmpM', sql)

# Mark matched fields explicitly
gp.CalculateField_management('tmpM', 'Match', "str('M')", 'PYTHON')


#
# Calculate Simple Positional Acccuracy on matching features
#

# Create a buffer around the reference dataset
gp.AddMessage("Buffering reference.")
gp.Buffer_analysis(refFC, 'tmpBuf', float(tolerance) * 2)

# Clip the test (now in match) to the reference buffer
gp.AddMessage("Clipping matched features to reference buffer.")
gp.Clip_analysis('tmpM', 'tmpBuf', 'tmpM_clip')
gp.Delete('tmpBuf')

# Calculate the length of the the clipped features - this is inside the buffer
gp.CalculateField_management('tmpM_clip', 'Length', \
                             'round(float(!SHAPE.length@meters!),2)', \
                             'PYTHON')

# Join the original test feature class with the matched clips
gp.AddMessage("Joining matched to clipped features.")
gp.AddJoin('tmpM', 'ReachCode', 'tmpM_clip', 'ReachCode')

# Save the clipped length as the "Error" - bit of of a misnomer
gp.AddMessage("Calculating errors.")
gp.CalculateField_management('tmpM', 'Error', '[tmpM_clip.Length]')

gp.RemoveJoin('tmpM', 'tmpM_clip')

try:
    gp.Delete('tmpM_clip')
except:
    gp.AddMessage('Unable to remove temporary file: tmpM_Clip')

# Do the accuracy calculation
gp.AddMessage("Calculating accuracies.")

gp.CalculateField_management('tmpM', 'Accuracy', \
                             'round(float(!Error!) / float(!Length!), 2)', \
                             'PYTHON')




#
# Find errors of commission - reachcodes in the Test but not Reference
#
gp.AddMessage("Finding errors of commission")

# Select reachcodes not found in reference dataset
sql = '"ReachCode" NOT IN (SELECT "ReachCode" FROM ' \
    + os.path.basename(refFC) + ')'

gp.MakeFeatureLayer('test', 'tmpC', sql)

gp.CalculateField_management('tmpC', 'Commission', \
                             'round(float(!SHAPE.length@meters!),2)', \
                             'PYTHON')

# Mark the "match" field with a 'C' to explicitly denote a commission
gp.CalculateField_management('tmpC', 'Match', "str('C')", 'PYTHON')


#
# Find errors of ommission - reachcodes in the Reference but not the Test
#
gp.AddMessage("Finding errors of omission")

# Select features in Reference that are not in Test
sql = '"ReachCode" NOT IN (SELECT "ReachCode" FROM ' \
    + os.path.basename(testFC) + ')'

# Copy to omission feature set and update calculations
gp.MakeFeatureLayer('ref', 'tmpO', sql)

gp.CalculateField_management('tmpO', 'Omission', \
                             'round(float(!SHAPE.length@meters!),2)', \
                             'PYTHON')

# Mark the "match" field with a 'C' to explicitly denote a commission
gp.CalculateField_management('tmpO', 'Match', "str('O')", 'PYTHON')



#
# Merge omissions, commissions and matches into a new dataset 'Accuracy_Result'
#
gp.AddMessage("Merging into result dataset.")

vt = gp.createobject("ValueTable")
vt.AddRow('tmpM')
vt.AddRow('tmpC')
vt.AddRow('tmpO')

gp.Merge(vt, 'Accuracy_Result')

del vt

fm = gp.CreateObject('FieldMappings')
fm.AddTable('Accuracy_Result')

gp.AddMessage("Done.")

# Pass the resulting dataset back to ArcGIS
gp.SetParameterAsText(3, 'Accuracy_Result')
del gp