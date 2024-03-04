import pandas as pd
import numpy as np

##############################################################################
######################### CleanDataForKPIVRanking ############################
##############################################################################
def CleanDataForKPIVRanking(DataInOut,tol=1.0e-12,tolZero=1.0e-12,VariableNamesForBarcodes=[]):
#CleanDataForKPIVRanking:   Remove problematic KPIVs (columns) and 
#datasets (rows).
#
#   Problematic KPIVs (columns) are removed from the data. These are KPIVs 
#   that have the same value for all data sets. Furthermore, datasets
#   (rows) with problematic values like NaN or Inf or missing values are
#   removed. Optionally, the data can also be made unique with respect to
#   the barcode. This means that from all rows with the same barcode only
#   the last one is kept.
#
#   function input:
#      DataInOut: Sample data where categorical KPIVs should be searched. It 
#              has dimension (nData,nPar), where nData is the number of 
#              data sets and nPar the number of KPIVs.
#      There are additional optional input arguments.
#      tol: The tolerance (relative or absolute) for the equality of floating 
#              point values. The default value is 1.0e-12.
#      tolZero: The limit, below which a floating point number be viewed as 
#              zero. It determines whether relative or absolute tolerance will 
#              be used for equality checking. The default value is 1.0e-12.
#      VariableNamesForBarcodes: Names of columns that contain barcodes, which 
#              should be used for making the data unique. It could also be 
#              empty. The default value is Barcode.
#
#   function output:
#      DataInOut: Table where the problematic KPIVs and datasets have 
#              been removed.
#      indKPIVsKept: Indices of the KPIVs that have been kept.
#      indKPIVsRemoved: Indices of the constant KPIVs that have been 
#              removed.
#
#   Exceptions:
#      DataIn empty: If there are no sample data, an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"

    ##################### code for pandas dataframe
    if isinstance(DataInOut,pd.DataFrame):
        ##################### check for correct data format and input parameter
        if DataInOut.empty:
            errStr="CleanDataForKPIVRanking:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)
        shapeData=DataInOut.shape

    ##################### code for numpy array
    else: 
        if np.size(DataInOut)<1:
            errStr="CleanDataForKPIVRanking:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)
        shapeData=np.shape(DataInOut)

    nRows=shapeData[0]
     
    ##################### choose default values for inappropriate function
    ##################### input
    if tol<1.0e-16:
        tol=1.0e-12;
    if tolZero<1.0e-16:
        tolZero=1.0e-12;
     
    ##################### clean the data
    DataInOut,indKPIVsKept,indKPIVsRemoved = RemoveConstantColumnTable(DataInOut,tol,tolZero); # remove columns with constant values
    if isinstance(DataInOut,pd.DataFrame):
        ColumnNames=list(DataInOut.columns)
        StringsFound=False
        for testStr in VariableNamesForBarcodes:
            if testStr in ColumnNames:
                StringsFound=True
                break
        DataInOut.index=np.array(range(0,nRows))
        DataInOut.dropna(subset=DataInOut.columns[indKPIVsKept],inplace=True); # remove nans and missing values
        if StringsFound==True:
            MakeTableUniqueBySelectedCols(DataInOut,VariableNamesForBarcodes); # remove rows with same barcode
        indRowsKept=np.array(list(DataInOut.index))
    else:
        MissingRowsBool=~np.isnan(DataInOut).any(axis=1)
        temp=np.nonzero(MissingRowsBool==True)
        inRowsKept=temp[0]
        DataInOut=DataInOut[inRowsKept,indKPIVsKept]; # remove nans and missing values
    
    return DataInOut,indKPIVsKept,indKPIVsRemoved,indRowsKept
##############################################################################
####################### end CleanDataForKPIVRanking ##########################
##############################################################################


##############################################################################
######################## RemoveConstantColumnTable ###########################
##############################################################################
def  RemoveConstantColumnTable(DataInOut,tol=1.0e-12,tolZero=1.0e-12):
#RemoveConstantParameterTable:   Identify columns that have only one 
#value and remove them from the data.
#
#   KPIVs that have the same value for all data sets contain no meaningful
#   statistical information, and thus can be omitted.
#   For KPIVs that are not floating point values this can be checked by
#   strict equality, i. e. means we look if the values are exactly equal
#   for all data sets. On the other hand, for floating points equality can
#   only be achieved within a given tolerance. This means a KPIV is viewed
#   as constant, if its relative range (difference between maximum and
#   minimum divided by the mean value) is smaller than a given tolerance.
#   The case, where the mean is very close to , needs a special
#   treatment. Here the absolute range (difference between maximum and
#   minimum) has to be smaller than the given tolerance.
#
#   function input:
#      DataInOut: Sample data from which constant KPIVs should be removed. It 
#              has dimension (nData,nPar), where nData is the number of 
#              data sets and nPar the number of KPIVs.
#      There are additional optional input arguments.
#      tol: The tolerance (relative or absolute) for the equality of floating 
#              point values. The default value is 1.0e-12.
#      tolZero: The limit, below which a floating point number be viewed as 
#              zero. It determines whether relative or absolute tolerance will 
#              be used for equality checking. The default value is 1.0e-12.
#
#   function output:
#      posSelected: Indices of the nonconstant KPIVs that have been kept.
#      posRemoved: Indices of the constant KPIVs that have been removed.
#
#   Exceptions:
#      DataInOut empty: If there are no sample data, an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"

    ##################### choose default values for inappropriate function
    ##################### input
    if tol<1.0e-16:
        tol=1.0e-12
    if tolZero<1.0e-16:
        tolZero=1.0e-12
    
    ##################### code for pandas dataframe
    if isinstance(DataInOut,pd.DataFrame):
        ##################### check for correct data format and input parameter
        if DataInOut.empty:
            errStr="RemoveConstantParameterTable:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)

        shapeData=DataInOut.shape
        columnTypes=DataInOut.dtypes
    ##################### code for numpy array
    else: 
        if np.size(DataInOut)<1:
            errStr="RemoveConstantParameterTable:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)
        shapeData=np.shape(DataInOut)

    n1=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    NonConst=np.ones((n2,)); # at start all parameter are declared as nonconstant
    for n in range(0,n2):
        bfloat=0.0
        ##################### code for pandas dataframe
        if isinstance(DataInOut,pd.DataFrame):
            tmpArray=DataInOut.iloc[:,n].to_numpy();
            if columnTypes.iloc[n]==np.dtype('float64') or columnTypes.iloc[n]==np.dtype('float32'): # for floating point data we have to apply tolerances
                bfloat=1.0;
        ##################### code for numpy array
        else:
            tmpArray=DataInOut[:,n]
            if type(DataInOut[0,n])==np.float64 or type(DataInOut[0,n])==np.float32: # for floating point data we have to apply tolerances
                bfloat=1.0;
        if bfloat>0.5:                
            meanTmp=np.mean(tmpArray);
            minTmp=np.min(tmpArray);
            maxTmp=np.max(tmpArray);
            if meanTmp>tolZero:
                if (maxTmp-minTmp)/meanTmp<tol: # relative range of variable is smaller then tolerance
                    NonConst[n]=0; # condition for constant data is fulfilled
            else:
                if (maxTmp-minTmp)<tol: # absolute range of variable is smaller then tolerance
                        NonConst[n]=0; # condition for constant data is fulfilled
        else:
            valfirst=tmpArray[0]; # for data that are not floating point we can check equality
            NonConst[n]=0;
            for m in range(1,n1):
                if tmpArray[m]!=valfirst:
                    NonConst[n]=1; # condition for constant data is fulfilled
                    break;
    posSelected=np.nonzero(NonConst>0.1); # indices of nonconstant columns
    posRemoved=np.nonzero(NonConst<0.1); # indices of constant columns
    if isinstance(DataInOut,pd.DataFrame):
        ColumnLabels=DataInOut.columns
        ColumnsSelected=list(ColumnLabels[posRemoved[0]])
        DataInOut.drop(columns=ColumnsSelected,inplace=True)
    else:
        DataInOut=np.delete(DataInOut,posRemoved[0],axis=1); # keep only nonconstant columns

        
    return DataInOut,posSelected[0],posRemoved[0]
##############################################################################
###################### end RemoveConstantColumnTable #########################
##############################################################################


##############################################################################
###################### MakeTableUniqueBySelectedCols #########################
##############################################################################
def MakeTableUniqueBySelectedCols(DataInOut,VariableNamesForUniqueness):
#MakeTableUniqueBySelectedCols:   Make data in seledcted colimns unique.
#The indices of the rows that should be kept are returned.
#
#   Sometimes the same part is measured more than once, e. g. with the He
#   leakage tester. However, in the statisical evaluation only  one value
#   should be included. Therefore, we have to make the data unique with
#   respect to the produced part, which usually is identified by a barcode.
#   Under the reasonable asumption that the data are sorted with respect to
#   time the latest is the relevant one, which should be kept. Therefore
#   the algorithm keeps only these rows.
#
#   function input:
#      DataIn: Sample data where categorical KPIVs should be searched. It 
#              has dimension (nData,nPar), where nData is the number of 
#              data sets and nPar the number of KPIVs.
#      VariableNamesForUniqueness: A string array with the names of the
#              columns that should be unique. If it is empty, the indices
#              for all rows are returned.
#
#   function output:
#      RowsToKeep: Indices of the rows that should be kept.
#
#   Exceptions:
#      DataIn empty: If there are no sample data, an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      DataIn no table: If the sample data are not given as a table, the 
#               names of the columns can not be checked. Therefore an 
#               exception is thrown with the message: 
#                     "The array of sample data must be a table!"
#      VariableNamesForUniqueness not 1d: If the array of column names is 
#               not 1d, an exception is thrown with the message: 
#                     "The array of column names has to be 1d!"

    ##################### check for correct data format and input parameter
    if not isinstance(DataInOut,pd.DataFrame):
        errStr="MakeTableUniqueBySelectedCols:invalidInput','The array of sample data must be a pandas DataFrame!"
        raise ValueError(errStr)
    if DataInOut.empty:
        errStr="MakeTableUniqueBySelectedCols:invalidInput','The array of sample data must not be empty!"
        raise ValueError(errStr)
    if type(VariableNamesForUniqueness)!=list:
        VariableNamesForUniqueness=list(VariableNamesForUniqueness)
    if type(VariableNamesForUniqueness[0])!=str:
        for s in VariableNamesForUniqueness:
            s=str(s)
    
    ##################### make data unique
    ColumnNames=list(DataInOut.columns)
    for testStr in VariableNamesForUniqueness:
        if testStr in ColumnNames:
            DataInOut.drop_duplicates(subset=testStr,keep='last',inplace=True)
    
##############################################################################
#################### end MakeTableUniqueBySelectedCols #######################
##############################################################################


##############################################################################
########################### FindCategoricalKPIVs #############################
##############################################################################
def FindCategoricalKPIVs(DataIn,nMinBins=4,tolInt=1.0e-12,tolUniform=0.8):
#FindCategoricalKPIVs:   Identify parameter that are not continuous.
#
#   For KPIVs that are not continuous the ranking algorithm is different. 
#   Therefore those categorical KPIVs have to be identified. Several 
#   criteria are checked, if a KPIV is categorical.
#   First we check if a KPIV is declared as categorical or string.
#   Furthermore, all KPIVs that are not numerical are categorical.
#   Numerical KPIVs that have only integer values are also viewed as
#   categorical. A number is viewed as integer, if its difference from an
#   integer is smaller than a given tolerance. Furthermore, KPIVs with a
#   histogram, which has less than a minimum number of bins, are viewed as 
#   categorical. Finally, KPIVs with a nearly uniform distribution have
#   also to be treated as categorical. 
#   Attention: Due to performance considerations the identification of the 
#              last two types of categorical variables is shifted to the actual
#              ranking calculations, although it violates the single 
#              responsibility principle!!!!!!!!!
#
#   function input:
#      DataIn: Sample data where categorical KPIVs should be searched. It 
#              has dimension (nData,nPar), where nData is the number of 
#              data sets and nPar the number of KPIVs.
#      There are additional optional input arguments.
#      nMinBins: The minimum number of bins for the histogram of a continuous 
#              KPIV. The default value is 4.
#      tolInt: The tolerance for the definition of integer values. If the 
#              deviation from a true integer value is smaller than tolInt, the 
#              number will be viewed as an integer. The default value 
#              is 1.0e-12.
#      tolUniform: The tolerance for the definition of a uniform distibution. 
#              If the difference between maximum and minimum of the histogram 
#              divided by its mean is smaller than tolUniform, the KPIV will  
#              be viewed as categorical. The default value is 0.8.
#
#   function output:
#      IndicesOfContinuousKPIVs: Indices of the continuous KPIVs that 
#              have been found.
#      IndicesOfCategoricalKPIVs: Indices of the categorical KPIVs that 
#              have been found.
#
#   Exceptions:
#      DataIn empty: If there are no sample data, an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"

##################### check for correct data format and input parameter
    ##################### code for pandas dataframe
    if isinstance(DataIn,pd.DataFrame):
        ##################### check for correct data format and input parameter
        if DataIn.empty:
            errStr="FindCategoricalKPIVs:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)
        shapeData=DataIn.shape
        columnTypes=DataIn.dtypes

    ##################### code for numpy array
    else: 
        if np.size(DataIn)<1:
            errStr="FindCategoricalKPIVs:invalidInput','The array of sample data must not be empty!"
            raise ValueError(errStr)
        shapeData=np.shape(DataIn)

    try: nKPIV = shapeData[1]
    except: nKPIV = 1

    ##################### choose default values for inappropriate function
    ##################### input
    if nMinBins<3:
        nMinBins=3;
    if tolInt<1.0e-16:
        tolInt=1.0e-12;
    if tolUniform<0.5:
        tolUniform=0.8;
    
    IndicesOfCategoricalKPIVsList=list([]);
    ############## for a table some columns may have different data types with 
    ############## some of them categorical
    if isinstance(DataIn,pd.DataFrame):
        for n in range(0,nKPIV):
            if columnTypes.iloc[n].name=='category': # defined as categorical
                IndicesOfCategoricalKPIVsList.append(n);
            if columnTypes.iloc[n].name=='object': # strings are also viewed as categorical
                IndicesOfCategoricalKPIVsList.append(n);
    ############## data with integer values are viewed as categorical
    for n in range(0,nKPIV):
        isfloat=False
        ##### compute fractional part of data
        if isinstance(DataIn,pd.DataFrame):
            if (columnTypes.iloc[n].name=='np.float32' or columnTypes.iloc[n].name=='np.float64'
                or columnTypes.iloc[n].name=='float64'): 
                isfloat=True
                dummy=DataIn.iloc[:,n]-DataIn.iloc[:,n].apply(np.floor)
                temp1=dummy.to_numpy()
                dummy=DataIn.iloc[:,n].apply(np.ceil)-DataIn.iloc[:,n]
                temp2=dummy.to_numpy()
        else:
            if (type(DataIn[0,n])==np.float64 or type(DataIn[0,n])==np.float32
                or type(DataIn[0,n])==np.float): 
                isfloat=True
                temp1=DataIn[:,n]-np.floor(DataIn[:,n])
                temp2=np.ceil(DataIn[:,n])-DataIn[:,n]
        if isfloat==True:   
            temp=np.multiply(temp1,temp1<temp2)+np.multiply(temp2,temp2<=temp1)
            posTmp=np.nonzero(temp>=tolInt); # find values that have a fractional part
            if np.size(posTmp)<1:
                IndicesOfCategoricalKPIVsList.append(n);
    
    ############## data with less than nMinBins and a nearly uniform 
    ############## distribution are viewed as categorical
    # for n in range(0,nKPIV):
    #     if (n in IndicesOfCategoricalKPIVsList)==False:
    #         if isinstance(DataIn,pd.DataFrame):
    #             temp=DataIn.iloc[:,n].to_numpy();
    #         else:
    #             temp=DataIn[:,n];
    #         histN,histBins = HistNG.HistCountsAdapted(temp,20,1); # compute histogram
    #         if histN.size<nMinBins:
    #             IndicesOfCategoricalKPIVsList.append(n);
    #         if (np.max(histN)-np.min(histN))/np.mean(histN)<tolUniform:
    #             IndicesOfCategoricalKPIVsList.append(n);
    ###### This calculation takes a very long time, because for each KPIV an
    ###### adapted histogram has to be computed. Since this is also done during
    ###### the ranking algorithm, we shift the identification of these types of
    ###### categorical data to this part ofthe programme, although it violates 
    ###### the single responsibility principle
    
    ######### convert lists with indices to numpy arrays and make indices unique
    indContinuousList=list(range(0,nKPIV))
    for indTmp in IndicesOfCategoricalKPIVsList: # remove categorical KPIVs from list of continuous KPIVs
        if indTmp in indContinuousList:
            indContinuousList.remove(indTmp)
    indTmp=np.array(IndicesOfCategoricalKPIVsList,dtype='int')
    IndicesOfCategoricalKPIVs=np.unique(indTmp) # remove double entries and sort in ascending order
    indTmp=np.array(indContinuousList)
    IndicesOfContinuousKPIVs=np.unique(indTmp) # remove double entries and sort in ascending order
    
    return IndicesOfContinuousKPIVs,IndicesOfCategoricalKPIVs
##############################################################################
######################### end FindCategoricalKPIVs ###########################
##############################################################################


##############################################################################
############################# FindDataResolution #############################
##############################################################################
def FindDataResolution(DataIn):
#FindDataResolution:   Find the numerical resolution of the data
#   For each parameter find the numerical resolution of the values, i. e. 
#   the minimum difference between two arbitrary values. 
# 
#   The input is sorted in a temporary array, so that the numerical 
#   resolution can be found as the minimum difference between adjacent 
#   elements. Due to the necessary sorting the complexity of this function
#   is O(n*log(n)).
#
#   function input:
#      DataIn: Sample data for all input parameter (features). It has
#              dimension (nData,nPar), where nData is the number of data 
#              sets and nPar the number of input parameter (features). 
#              Thus, the values for each data set are in one row. An input of
#              the form (nData,) is converted to (nData,1)
#              Due to some reasons we make an exception for the special
#              case of the dimension (1,nData), which will be treated as a
#              1d row vector of data, i.e. nPar=1.
#
#   function output:
#      DataResolution: Numerical resolution for all input parameter 
#                      (features). It has dimension (1,nPar).
#
#   Exceptions:
#      nData<2: If there are less than 2 data sets, it is not possible to
#               determine the numerical resolution. In that case a ValueError 
#               is thrown with the message: 
#                     "There have to be at least 2 samples in order to 
#                      determine the resolution!"

########## resolution = minimum difference between 2 neighbouring values
    shapeData = np.shape(DataIn)
############# check for valid input
    try: nData = shapeData[0]
    except: nData = 1
    try: nPar = shapeData[1]
    except: nPar = 1
    if nData==1 and nPar>1: # DataIn is a row vector
        nData=nPar;
        nPar=1;

    ResolutionTolerance=1.0e-6
    DataResolution = np.zeros((1, nPar), float)
    if nData<2:
        errStr="Error in FindDataResolution: There have to be at least 2 samples in order to determine the resolution!"
        raise ValueError(errStr)
        
    DataIn=np.reshape(DataIn,(nData,nPar)) # reshape in order to avoid considering different cases
    for n in range(0, nPar):
        dummy1 = np.sort(DataIn[:,n])  # sort data in ascending order
        dummy2 = np.diff(dummy1)   # compute difference between neighbouring values
        pos = dummy2 > 0    # only values that are different are considered
        if np.size(dummy2[pos])>0:
            DataResolution[:, n] = min(dummy2[pos])    # determine minimum difference larger than 0
        else:
            DataResolution[:,n]=dummy1[0]*ResolutionTolerance; # multiply that value with a small number
    return DataResolution
##############################################################################
########################## end FindDataResolution ############################
##############################################################################

