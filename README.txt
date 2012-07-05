CreateMetadata.py

Create new fields:

   mdLength
   mdError
   mdOmission
   mdCommission
   mdAccuracy

   mdSource
   mdOriginal
   mdVerify
   mdUpdate

Compute error per ReachCode.

1. Dissolve test and ref on ReachCode

2. Add fields to test

3. Calculate initial lengths

4. Create buffer on ref

5. Clip test to buffer

6. Calculate clip length, save length - clip as error

7. Joins clips

VT: 0108
   Test: High
   Reference: Local

CO: 1405
   Test: Med
   Reference: High

FL: 0311
   Test: Med
   Ref: High


1/50 inch at 1:24,000 = 40 feet = 12.192m