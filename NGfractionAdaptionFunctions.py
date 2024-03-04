import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC,SMOTE


##############################################################################
################## GenerateClassLabelsForNGRankingOutlier ####################
##############################################################################
def GenerateClassLabelsForNGRankingOutlier(DataKPOV,specValue,specLimits,ngFracDesired,tolRel=5.0e-2):
#GenerateClassLabelsForNGRankingOutlier: Generate the specified number of
#NG parts by finding appropriate outlier limits.
#
#   Usually, the number of true NG parts is too small for a meaningful
#   statistic. Therefore, additional artificial NG parts have to be
#   generated. One method is to define tighter spec limits, so that more
#   parts are outside the spec. With the help of the bisection algorithm 
#   this function determines appropriate spec limits, in order to achieve
#   the desired nimber of outlier, which are treated as NG parts.
#
#   function input:
#      DataKPOV: Sample data for the relevant KPOV. It has dimension 
#                (nData,1), where nData is the number of data sets. 
#      specValue: The spec value for this KPOV.
#      specLimits: The spec limits for this KPOV. It has the dimension (2,1).
#      ngFracDesired: The desired NG fraction that should be achieved by
#                     the definition of new spec limits for outlier. If it
#                     is smaller than zero a default value of 10 # is used.
#      There are additional optional input arguments collected in varargin.
#      tolRel=varargin{1}: The relative tolerance for the desired fraction 
#                 of NG parts. The default value is 5%=5.0e-2.
#
#   function output:
#      ClassLabels: The class labels for the outliers, which are treated as
#                   NG parts. Good parts are denoted by 1 and NG parts by
#                   -1.
#
#   Exceptions:
#      DataKPOV empty: If there are no sample data, an exception is thrown 
#               with the message: 
#                     "The array of KPOV data must not be empty!"
#      DataKPOV not 1d: If the array for the KPOV data is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of KPOV data has to be 1d!"
#      specLimits not 1d: If the array for the specLimits is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of specLimits has to be 1d!"
#      number of specLimits~=2: If the size of the spec limits is not 2,
#               an exception is thrown with the message: 
#                     "The array of spec limits has the wrong size!"

    ##################### check for correct data format and input parameter
    if np.size(DataKPOV)<1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPOV data must not be empty!"
        raise ValueError(errStr)
    shapeData=np.shape(DataKPOV)
    nData=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1  
    if nData==1 and n2>1: # DataKPOV is a row vector
        nData=n2;
        n2=1;
    if n2!=1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPOV data has to be 1d!"
        raise ValueError(errStr)
    shapeData=np.shape(specLimits)
    n1=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1  
    if n1==1 and n2>1: # specLimits is a row vector
        n1=n2;
        n2=1;
    if n2!=1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of spec limits has to be 1d!"
        raise ValueError(errStr)
    if n1!=2:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of spec limits has has the wrong size!"
        raise ValueError(errStr)
    
    ##################### choose default values for inappropriate function
    ##################### input
    if specLimits[1]<specLimits[0]: # wrong order
        swapVal=specLimits[0];
        specLimits[0]=specLimits[1];
        specLimits[1]=swapVal;
    if specLimits[0]>specValue:
        specLimits[0]=specValue;
    if specLimits[1]<specValue:
        specLimits[1]=specValue;
    if ngFracDesired>1:
        ngFracDesired=0.5;
    if ngFracDesired<0:
        ngFracDesired=0.1;
    if tolRel>1:
        tolRel=0.2;
    if tolRel<0:
        tolRel=5.0e-2;
    
    ##################### generate class labels by searching for appropriate
    ##################### outlier limits
    ClassLabels=np.ones([nData,1]);
    nNGDesired=ngFracDesired*nData;
    LowerInterval=specValue-specLimits[0];
    UpperInterval=specLimits[1]-specValue;
    posOutlier=np.nonzero(np.logical_or(DataKPOV<specValue-LowerInterval,DataKPOV>specValue+UpperInterval));
    nOutlier=posOutlier[0].size;
    if nOutlier>=nNGDesired: # we don't reduce the number of true outliers
        ClassLabels[posOutlier[0]]=-1.0;
    else:
        gammaLower=1.0;
        gammaUpper=0.0;
        gammaOutlier=0.5;
        posOutlier=np.nonzero(np.logical_or(DataKPOV<specValue-gammaOutlier*LowerInterval,DataKPOV>specValue+gammaOutlier*UpperInterval));
        nOutlier=posOutlier[0].size;   
        while nOutlier<(1.0-tolRel)*nNGDesired or nOutlier>(1.0+tolRel)*nNGDesired:
            if nOutlier<=nNGDesired:
                gammaLower=gammaOutlier;
            else:
                gammaUpper=gammaOutlier;
            gammaOutlier=0.5*(gammaLower+gammaUpper);
            posOutlier=np.nonzero(np.logical_or(DataKPOV<specValue-gammaOutlier*LowerInterval,DataKPOV>specValue+gammaOutlier*UpperInterval));
            nOutlier=posOutlier[0].size;
        ClassLabels[posOutlier[0]]=-1.0;

    return ClassLabels
##############################################################################
################ end GenerateClassLabelsForNGRankingOutlier ##################
##############################################################################


##############################################################################
################### GenerateClassLabelsForNGRankingSmote #####################
##############################################################################
def GenerateClassLabelsForNGRankingSmote(DataKPIV,DataKPOV,specLimits,ngFracDesired,CategoricalKPIVs=[]):
#GenerateClassLabelsForNGRankingSmote: Generate the specified global NG
#fraction by oversampling with thew SMOTE algorithm.
#
#   Usually, the number of true NG parts is too small for a meaningful
#   statistic. Therefore, additional artificial NG parts have to be
#   generated. One method is oversampling, which can be done with the
#   python package imblearn that implments the SMOTE algorithm.
#
#   function input:
#      DataKPIV: Sample data for the KPIVs. It has dimension (nData,nKPIV), 
#                where nData is the number of data sets and nKPIV the 
#                number of KPIVs. 
#      DataKPOV: Sample data for the relevant KPOV. It has dimension 
#                (nData,1). 
#      specLimits: The spec limits for this KPOV. It has the dimension (2,1).
#      ngFracDesired: The desired NG fraction that should be achieved by
#                     oversampling. If it is smaller than zero, a default 
#                     value of 10 # is used.
#      There are additional optional input arguments collected in varargin.
#      CategoricalKPIV=varargin{1}: The indices of categorical KPIVs that 
#                to be treated differently. This array might be empty, if
#                there are no categorical KPIVs.
#
#   function output:
#      ClassLabels: The class labels for the outliers, which are treated as
#                   NG parts. Good parts are denoted by 1 and NG parts by
#                   -1.
#      DataKPIVSmote: The oversampled data for the KPIVs.
#
#   Exceptions:
#      DataKPIV empty: If there are no sample data for the KPIVs, an 
#               exception is thrown with the message: 
#                     "The array of KPIV data must not be empty!"
#      DataKPOV empty: If there are no sample data for the KPOV, an 
#               exception is thrown with the message: 
#                     "The array of KPOV data must not be empty!"
#      DataKPOV not 1d: If the array for the KPOV data is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of KPOV data has to be 1d!"
#      nKPOV~=nData: If the size of the KPOV data does not fit to the size 
#               of the KPIV data, an exception is thrown with the message: 
#                     "The array of KPOV data must have the same length 
#                      as the array of KPIV data!"
#      specLimits not 1d: If the array for the specLimits is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of specLimits has to be 1d!"
#      number of specLimits~=2: If the size of the spec limits is not 2,
#               an exception is thrown with the message: 
#                     "The array of spec limits has the wrong size!"

    ##################### check for correct data format and input parameter
    if isinstance(DataKPIV,pd.DataFrame):
        ##################### check for correct data format and input parameter
        if DataKPIV.empty:
            errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPIV data must not be empty!"
            raise ValueError(errStr)
        shapeDataKPIV=DataKPIV.shape
    else: 
        if np.size(DataKPIV)<1:
            errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPIV data must not be empty!"
            raise ValueError(errStr)
        shapeDataKPIV=np.shape(DataKPIV)
    if np.size(DataKPOV)<1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPOV data must not be empty!"
        raise ValueError(errStr)
    shapeDataKPOV=np.shape(DataKPOV)
    nData=shapeDataKPOV[0]
    try: n2 = shapeDataKPOV[1]
    except: n2 = 1
    if nData==1 and n2>1: # DataKPOV is a row vector
        nData=n2;
        n2=1;
    if n2!=1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPOV data has to be 1d!"
        raise ValueError(errStr)
    n1=shapeDataKPIV[0]
    try: n2 = shapeDataKPIV[1]
    except: n2=1
    if n1!=nData:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of KPOV data must have the same length as the array of KPIV data!"
        raise ValueError(errStr)
    shapeData=np.shape(specLimits)
    n1=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if n1==1 and n2>1: # specLimits is a row vector
        n1=n2;
        n2=1;
    if n2!=1:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of spec limits has to be 1d!"
        raise ValueError(errStr)
    if n1!=2:
        errStr="GenerateClassLabelsForNGRankingOutlier:invalidInput','The array of spec limits has the wrong size!"
        raise ValueError(errStr)
    
    ##################### choose default values for inappropriate function
    ##################### input
    if specLimits[1]<specLimits[0]: # wrong order
        swapVal=specLimits[0];
        specLimits[0]=specLimits[1];
        specLimits[1]=swapVal;
    if ngFracDesired>0.5:
        ngFracDesired=0.5;
    if ngFracDesired<0:
        ngFracDesired=0.1;
    ngFracDesiredSmote=ngFracDesired/(1.0-ngFracDesired); # conversion to the corresponding SMOTE parameter
    
    ##################### generate class labels by oversampling with SMOTE
    ClassLabels=np.ones([nData,1]);
    nNGDesired=ngFracDesired*nData;
    posOutlier=np.nonzero(np.logical_or(DataKPOV<specLimits[0],DataKPOV>specLimits[1]));
    nOutlier=posOutlier[0].size;
    if nOutlier>=nNGDesired: # we don't reduce the number of true outliers
        ClassLabels[posOutlier[0]]=-1.0;
        DataKPIVSmote=DataKPIV
    else:
        ClassLabelsTrue=np.ones([nData,1]);
        ClassLabelsTrue[posOutlier[0]]=-1.0;
        if np.size(CategoricalKPIVs)<1:
            sm = SMOTE(sampling_strategy=ngFracDesiredSmote)
        else:
            sm = SMOTENC(categorical_features=CategoricalKPIVs,sampling_strategy=ngFracDesiredSmote)
        DataKPIVSmote, ClassLabels = sm.fit_resample(DataKPIV, ClassLabelsTrue)
        if np.size(ClassLabels)<1:
            ClassLabels=ClassLabelsTrue
        
    return ClassLabels,DataKPIVSmote
##############################################################################
################# end GenerateClassLabelsForNGRankingSmote ###################
##############################################################################
