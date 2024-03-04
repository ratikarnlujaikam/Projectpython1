##############################################################################
# This file collects all functions that are necessary to generate and plot   # 
# Ng-Fraction-Histograms. These are diagrams that show the histogram of a    # 
# selected KPIV together with the local NG fraction, which is the number of  #
# ng parts in a bin divided by the number of all parts in this bin. There    #
# are two slightly different types of such diagrams. The function            #
# HistogramWithNGfraction produces a histogram with bins that have the same  #
# width, whereas HistogramWithNGfractionAdapted generates bins that have an  #
# adapted width, so that a minimum number of parts is guaranteed for all     #
# bins. Details of the employed mathematical algorithms can be found in the  # 
# description of the individual functions.                                   #
#                                                                            #
# Many of the functions in this file check the validity of their input       #
# arguments and throw a ValueError as an exception, if the requirements are  #
# not fulfilled. A description of the potential exceptions can be found in   #
# the corresponding function description. If these exceptions are not caught,#
# the program will crash. Therefore, it is highly recommended that a program,#
# which calls some of the functions in this file, should catch the potential #
# exceptions and handle them appropriately.                                  #
#                                                                            #
# Several functions from the packages numpy and matplotlib are used, i. e.   # 
# these packages must be installed.                                          #
#                                                                            #
##############################################################################
#                                                                            #
# Author: Werner Karpen, modified 08.11.2022                                 #
#                                                                            #
##############################################################################

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import DataSciencePreprocessingFunctions as Prepro

plt.rcParams['axes.grid'] = True

##############################################################################
####################### HistogramWithNGfractionAdapted #######################
##############################################################################
def HistogramWithNGfractionAdapted(DataInput, ClassLabels, parIndex,FeatureNames, nBins=-1, minCount=-1, bShowPlot=-1,bShowErrorBars=1,countDensity=1):
#HistogramWithNGfractionAdapted:   Determine adapted histogram together 
#with localized NG fraction for each bin.
#
#   From the given sample data the histogram for the selected parameter is 
#   determined. The bin sizes are adapted in such a way that no bin has  
#   lower counts than minCount (see the function HistCountsAdapted for 
#   details). Furthermore, for this histogram the local NG fraction for 
#   each bin is calculated. Optionally both quantities are plotted together
#   in one diagram. The histogram can either be represented by the count
#   density, which is for each bin the number of counts divided by the 
#   width of the bin, or by the probability density which is the count
#   density divided by the total number sample data (nData).
#
#   function input:
#      DataIn: Sample data for all input parameter (features). It has
#              dimension (nData,nPar), where nData is the number of data 
#              sets and nPar the number of input parameter (features). 
#              Thus, the values for each data set are in one row.
#      CLassLabels: Labels for a binary classification of the sample data. 
#                   The label (-1) indicates ng parts, whereas the label 
#                   (+1) indicates good parts. The array must have  
#                   dimension (nData,1) or (1,nData).
#      parIndex: Index of the selected parameter for the histogram.
#      FeatureNames: Names of all features. It is used to identify the name of 
#                    feature that is selected by parIndex. The array must have  
#                    dimension (nPar,1) or (1,nPar).
#      nBins: Desired number of bins. The true number of bins in the
#             generated histogram might be smaller for pathological cases.
#             If nBins<1, Sturges'rule will be applied, i. e. 
#             nBins=1+log2(nData).
#      minCount: The allowed minimum number of counts in one bin.  
#                Obviously, if nData<minCount, it is impossible to fulfill
#                this requirement. If minCount is negative or larger than
#                nData, the following empirical rule will be applied: 
#                minCount=0.05*nData.
#      bShowPlot: This function argument controls the optional plotting. If
#                 bShowPlot>0 the diagram will be shown, otherwise only the
#                 data are calculated. The default value is -1.
#      bShowErrorBars: This function argument controls a ertain aspect of the 
#                 optional plotting. If bShowErrorBars>0 the error bars for  
#                 the NG fraction will be shown, otherwise not. The default 
#                 value is +1.
#      countDensity: This function argument controls whether the count density 
#                (number of counts/width of the bin) or the probability
#                 density (count density/nData) will be plotted for the  
#                 histogram. If countDensity is smaller than 0 the   
#                 count density will be shown, otherwise the probability 
#                 density. The default value is +1.
#
#   function output:
#      histN: The number of parts in each bin. It has dimension (nBins,1).
#      histbins: The values for the consecutive bin edges. It has 
#                dimension (nBins+1,1).
#      ngFracBin: Local NG fraction for each bin. It has dimension 
#                 (nBins,1).
#      ngFracError: Error of the NG fraction for each bin. It has 
#                   dimension (nBins,1).
#
#   Exceptions:
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      ClassLabels not 1d: If the array for the class labels is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of class labels has to be 1d!"
#      nClassLabels~=nData: If the size of the class labels does not fit to
#               the size of the sample data an exception is thrown with the
#               message: 
#                     "The array of sample data must have the same length 
#                      as the array of class labels!"
#      FeatureNames not 1d: If the array for the feature names is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of feature names has to be 1d!"
#      nFeatureNames~=nPar: If the size of the feature does not fit to the size
#                of the features an exception is thrown with the
#               message: 
#                     "The array of feature names must have the same length 
#                      as the second dimension of the sample data!"
#      parIndex<1 or parIndex>nPar: If index for the selected parameter is
#               smaller than 1 or larger than the number of parameter, an 
#               exception is thrown with the message: 
#                     "The index of the selected parameter is out of the bounds of the sample data!"

######### set default values for unspecified function input
    shapeData=np.shape(DataInput)
    nData=shapeData[0]
    if nBins<1:
        nBins=1+int(math.ceil(math.log2(nData)))
    if minCount<0 or minCount>nData:
        minCount=int(0.01*nData)
        if minCount<500:
            minCount=500;

############# check for valid input
    nLabels=np.size(ClassLabels)
    try: nPar = shapeData[1]
    except: nPar = 1
    if nData<1:
        errStr="Error in HistogramWithNGfractionAdapted: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(ClassLabels).ndim>1:
        errStr="Error in HistogramWithNGfractionAdapted: The array of class labels has to be 1d!"
        raise ValueError(errStr)
    if nLabels!=nData:
        errStr="Error in HistogramWithNGfractionAdapted: The array of sample data must have the same length as the array of class labels!"
        raise ValueError(errStr)
    if np.squeeze(FeatureNames).ndim>1:
        errStr="Error in HistogramWithNGfractionAdapted: The array of feature names has to be 1d!"
        raise ValueError(errStr)
    nFeatureNames=np.size(FeatureNames)
    if nFeatureNames!=nPar:
        errStr="Error in HistogramWithNGfractionAdapted: The array of feature names must have the same length as the second dimension of the sample data!"
        raise ValueError(errStr)
    if parIndex<0 or parIndex>nPar-1:
        errStr="Error in HistogramWithNGfractionAdapted: The index of the selected parameter is out of the bounds of the sample data!"
        raise ValueError(errStr)

######### compute histogram with specified number of bins
######### However, the bin size is adapted, so that no bin contains less than minCount parts
######### As a consequence the true number of bins might be less than nBins
    histN, histbins = HistCountsAdapted(DataInput[:, parIndex], nBins, minCount)

######## compute NG fraction for each bin:
    ngFracBin, ngFracError,_ = ComputeNGfractionInBins(DataInput[:, parIndex], ClassLabels, histbins)

####### if desired, plot a histogram of p(x) together with the local NG fraction for each bin and its error
    if bShowPlot>0:
        PlotHistogramWithNGfraction(histN, histbins, ngFracBin, ngFracError, FeatureNames[parIndex])
    return histN, histbins, ngFracBin, ngFracError
##############################################################################
#################### end HistogramWithNGfractionAdapted ######################
##############################################################################



##############################################################################
########################### HistogramWithNGfraction ##########################
##############################################################################
def HistogramWithNGfraction(DataInput, ClassLabels, parIndex,FeatureNames, nBins=-1, bShowPlot=-1,bShowErrorBars=1,countDensity=1):
#HistogramWithNGfraction:   Determine histogram together with localized
#NG fraction for each bin.
#
#   From the given sample data the histogram for the selected parameter is 
#   determined. Furthermore, for this histogram the local NG fraction for 
#   each bin is calculated. Optionally both quantities are plotted together
#   in one diagram. The histogram can either be represented by the count
#   density, which is for each bin the number of counts divided by the 
#   width of the bin, or by the probability density which is the count
#   density divided by the total number sample data (nData).
#
#   function input:
#      DataIn: Sample data for all input parameter (features). It has
#              dimension (nData,nPar), where nData is the number of data 
#              sets and nPar the number of input parameter (features). 
#              Thus, the values for each data set are in one row.
#      CLassLabels: Labels for a binary classification of the sample data. 
#                   The label (-1) indicates ng parts, whereas the label 
#                   (+1) indicates good parts. The array must have  
#                   dimension (nData,1) or (1,nData).
#      parIndex: Index of the selected parameter for the histogram.
#      FeatureNames: Names of all features. It is used to identify the name of 
#                    feature that is selected by parIndex. The array must have  
#                    dimension (nPar,1) or (1,nPar).
#      nBins: Desired number of bins. The true number of bins in the
#             generated histogram might be smaller for pathological cases.
#             If the value is not specified, Sturges'rule will be applied, 
#             i. e. nBins=1+log(2*nData).
#      bShowPlot: This function argument controls the optional plotting. If
#                 bShowPlot>0 the diagram will be shown, otherwise only the
#                 data are calculated. The default value is -1.
#      bShowErrorBars: This function argument controls a ertain aspect of the 
#                 optional plotting. If bShowErrorBars>0 the error bars for  
#                 the NG fraction will be shown, otherwise not. The default 
#                 value is +1.
#      countDensity: This function argument controls whether the count density 
#                (number of counts/width of the bin) or the probability
#                 density (count density/nData) will be plotted for the  
#                 histogram. If countDensity is smaller than 0 the   
#                 count density will be shown, otherwise the probability 
#                 density. The default value is +1.
#
#   function output:
#      histN: The number of parts in each bin. It has dimension (nBins,1).
#      histbins: The values for the consecutive bin edges. It has 
#                dimension (nBins+1,1).
#      ngFracBin: Local NG fraction for each bin. It has dimension 
#                 (nBins,1).
#      ngFracError: Error of the NG fraction for each bin. It has 
#                   dimension (nBins,1).
#
#   Exceptions:
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      ClassLabels not 1d: If the array for the class labels is not 1d an 
#               exception is thrown with the message: 
#                     "The array of class labels has to be 1d!"
#      nClassLabels!=nData: If the size of the class labels does not fit to
#               the size of the sample data an exception is thrown with the
#               message: 
#                     "The array of sample data must have the same length 
#                      as the array of class labels!"
#      FeatureNames not 1d: If the array for the feature names is not 1d, an 
#               exception is thrown with the message: 
#                     "The array of feature names has to be 1d!"
#      nFeatureNames~=nPar: If the size of the feature does not fit to the size
#                of the features an exception is thrown with the
#               message: 
#                     "The array of feature names must have the same length 
#                      as the second dimension of the sample data!"
#      parIndex<1 or parIndex>nPar: If index for the selected parameter is
#               smaller than 1 or larger than the number of parameter, an 
#               exception is thrown with the message: 
#                     "The index of the selected parameter is out of the bounds of the sample data!"

######### set default values for unspecified function input
    shapeData=np.shape(DataInput)
    nData=shapeData[0]
    if nBins<1:
        nBins=1+int(math.ceil(math.log2(nData)))
        
############# check for valid input
    nLabels=np.size(ClassLabels)
    try: nPar = shapeData[1]
    except: nPar = 1
    if nData<1:
        errStr="Error in HistogramWithNGfraction: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(ClassLabels).ndim>1:
        errStr="Error in HistogramWithNGfraction: The array of class labels has to be 1d!"
        raise ValueError(errStr)
    if nLabels!=nData:
        errStr="Error in HistogramWithNGfraction: The array of sample data must have the same length as the array of class labels!"
        raise ValueError(errStr)
    if np.squeeze(FeatureNames).ndim>1:
        errStr="Error in HistogramWithNGfraction: The array of feature names has to be 1d!"
        raise ValueError(errStr)
    nFeatureNames=np.size(FeatureNames)
    if nFeatureNames!=nPar:
        errStr="Error in HistogramWithNGfraction: The array of feature names must have the same length as the second dimension of the sample data!"
        raise ValueError(errStr)
    if parIndex<0 or parIndex>nPar-1:
        errStr="Error in HistogramWithNGfraction: The index of the selected parameter is out of the bounds of the sample data!"
        raise ValueError(errStr)
       
######### compute histogram with specified number of bins
    histN, histbins = np.histogram(DataInput[:, parIndex], nBins)

######### compute NG fraction for each bin:
    ngFracBin, ngFracError,_ = ComputeNGfractionInBins(DataInput[:, parIndex], ClassLabels, histbins)

######## if desired, plot a histogram of p(x) together with the local NG fraction for each bin and its error
    if bShowPlot > 0:
        PlotHistogramWithNGfraction(histN, histbins, ngFracBin, ngFracError, FeatureNames[parIndex])
    return histN, histbins, ngFracBin, ngFracError
##############################################################################
####################### end HistogramWithNGfraction ##########################
##############################################################################



##############################################################################
############################## HistCountsAdapted #############################
##############################################################################
def HistCountsAdapted(DataIn, nBins, minCount):
#HistCountsAdapted:   Determine histogram with non-equidistant bin sizes. 
#   The bin sizes are adapted in such a way that no bin has lower counts 
#   than minCount.
#
#   Bins with lower counts than minCount are joined until all bins fulfill
#   this requirement. Simultaneously, bins with the temporary maximum 
#   number of counts are split into two bins, in order to achieve the 
#   desired number of bins (nBin). There might be pathological cases, where
#   it is not possible to fulfill both requirements (minCount and nBins).
#   Then the number of bins might be smaller than nBins. If the number of
#   sample data is smaller than minCount, it is obviously impossible to 
#   fulfill the requirement on minCount.
#
#   function input:
#      DataIn: Sample data from which the histogram has been derived. It 
#              has dimension (nData,1), (nData,) or (1,nData), where nData is   
#              the number of data sets.
#      nBins: Desired number of bins. The true number of bins in the
#             generated histogram might be smaller for pathological cases.
#      minCount: The allowed minimum number of counts in one bin.  
#                Obviously, if nData<minCount, it is impossible to fulfill
#                this requirement.
#
#   function output:
#      histN: Number of parts in each bin. Besides pathological cases it  
#             has dimension (nBins,1).
#      binEdges: Values for the consecutive bin edges. Besides pathological
#                cases it has dimension (nBins+1,1).
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an 
#               exception is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      nBins<1: If the desired number of bins for the histogram is smaller 
#               than 1, an exception is thrown with the message: 
#                     "The desired number of bins must be larger than 0!"
#      minCount>nData: If the allowed minimum number of counts in one bin  
#                is larger than than the number of sample data, the 
#                requirement on minCount can not be fulfilled. In that case
#                an exception is thrown with the message: 
#                      "It is imposible to fulfill the requirment on the 
#                       minimum number of counts in one bin!"

############# check for valid input
    nData=np.size(DataIn)
    if np.squeeze(DataIn).ndim>1:
        errStr="Error in HistCountsAdapted: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    if nData<1:
        errStr="Error in HistCountsAdapted: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if nBins<1:
        errStr="Error in HistCountsAdapted: The number of bins has to be larger than zero!"
        raise ValueError(errStr)
    if minCount>nData:
        errStr="Error in HistCountsAdapted: It is imposible to fulfill the requirment on the minimum number of counts in one bin!"
        raise ValueError(errStr)

    DataIn=np.reshape(DataIn,(nData,1)) # reshape in order to avoid considering different cases    

######### determine minimum and maximum value of data for later us
    xMin=min(DataIn)
    xMax=max(DataIn)
    binSizeEqual=(xMax-xMin)/nBins # size of equidistant bins
    minBinSize=binSizeEqual/5.0 # allowed minimum size of bins
    
######### compute histogram with specified number of bins
    histCountsTmp, histEdgesTmp = np.histogram(DataIn, nBins)

######### the bin size can not be smaller than the minimum distance between the sample data --> determine this minimum size
    binResolution = Prepro.FindDataResolution(DataIn)
    if minBinSize<binResolution:
        minBinSize=binResolution


######### By iterating over the existing bins we search bins with a number of parts that is too
######### small and join them with a neighbouring bin.
######### Similarly bins with a very large count are split into two bins.
######### This is necessary, because otherwise the total number of bins
######### might become too small (much less than the desired number of bins)
    mw = min(histCountsTmp)
    iterationCount = 0
    while mw < minCount and iterationCount < 10:
        ########## connect bins with small counts until minimum number in each bin is reached
        mw = min(histCountsTmp)             # find bin with minimum number of parts
        mpos = np.where(histCountsTmp == mw)[0][0]
        nBinsTmp = len(histCountsTmp)
        while mw < minCount and nBinsTmp > 1:
            if mpos > 0:    # number of parts in left neighbour
                nLeft = histCountsTmp[mpos-1]
            else:
                nLeft = len(DataIn) + 1000
            if mpos < nBinsTmp-1:  # number of part in right neighbour
                nRight = histCountsTmp[mpos+1]
            else:
                nRight = len(DataIn) + 1000
            temp1 = histCountsTmp
            temp2 = histEdgesTmp
            del histCountsTmp
            del histEdgesTmp
            if nLeft <= nRight:  # join bin with neighbour that has the lower number of parts
                histCountsTmp, histEdgesTmp = JoinBins(temp1, temp2, mpos-1)
            else:
                histCountsTmp, histEdgesTmp = JoinBins(temp1, temp2, mpos)
            mw = min(histCountsTmp)
            mpos = np.where(histCountsTmp == mw)[0][0]
            nBinsTmp = nBinsTmp-1

        ######## split bins with large bin count
        maxTmp = max(histCountsTmp)
        mpos = np.where(histCountsTmp == maxTmp)[0][0]
        binSplitSize = 0.5*(histEdgesTmp[mpos+1] - histEdgesTmp[mpos])
        while True:
            if nBinsTmp >= nBins:
                break
            else:
                if len(np.argwhere(binSplitSize < minBinSize)) != 0: break
            temp1 = histCountsTmp
            temp2 = histEdgesTmp
            histCountsTmp, histEdgesTmp = SplitBin(DataIn, temp1, temp2, mpos)
            maxTmp = max(histCountsTmp)
            mpos = np.where(histCountsTmp == maxTmp)[0][0]
            binSplitSize = 0.5 * (histEdgesTmp[mpos + 1] - histEdgesTmp[mpos])
            nBinsTmp = nBinsTmp + 1
        mw = min(histCountsTmp)
        iterationCount = iterationCount + 1  # counter to prevent infinite loop

########## The last operation in the iteration above was splitting of bins with large counts.
########## In pathologocal cases this might create a bin that has less counts than the required minimum.
########## Therefore a last pass to remove too small bins might be necessary
    mw = min(histCountsTmp)
    mpos = np.where(histCountsTmp == mw)[0][0]
    nBinsTmp = len(histCountsTmp)
    while mw < minCount and nBinsTmp > 1:
        if mpos > 0:    # number of parts in left neighbour
            nLeft = histCountsTmp[mpos-1]
        else:
            nLeft = len(DataIn) + 1000
        if mpos < nBinsTmp-1:  # number of parts in right neighbour
            nRight = histCountsTmp[mpos+1]
        else:
            nRight = len(DataIn) + 1000
        temp1 = histCountsTmp
        temp2 = histEdgesTmp
        del histCountsTmp
        del histEdgesTmp
        if nLeft <= nRight:  # join bin with neighbour that has the lower number of parts
            histCountsTmp, histEdgesTmp = JoinBins(temp1, temp2, mpos-1)
        else:
            histCountsTmp, histEdgesTmp = JoinBins(temp1, temp2, mpos)
        mw = min(histCountsTmp)
        mpos = np.where(histCountsTmp == mw)[0][0]
        nBinsTmp = nBinsTmp - 1

    histN = histCountsTmp
    binEdges = histEdgesTmp
    return histN, binEdges
##############################################################################
########################## end HistCountsAdapted #############################
##############################################################################


##############################################################################
###################### end ComputeHistogramAdapted ###########################
##############################################################################
def ComputeHistogramAdapted(DataIn,nBins,minCounts,statistcalMethod=0.0,bAdapted=1.0):
#ComputeHistogramAdapted:   Compute histogram in bins for the given data.
#
#   From the given sample data the histogram for the selected parameter is 
#   determined. By default the bin sizes are adapted in such a way that no   
#   bin has lower counts than minCount (see the function HistCountsAdapted 
#   for details). However, this behaviour can be changed by the optional 
#   function input bAdapted (see description below). The histogram can be 
#   evaluated either by simple counting of the parts in the bins or by the 
#   more advanced kernel density approximation.
#
#   function input:
#      DataIn: Sample data from which the histogram should be derived. It 
#              has dimension (nData,1) or (1,nData), where nData is the  
#              number of data sets.
#      nBins: Desired number of bins. The true number of bins in the
#             generated histogram might be smaller for pathological cases.
#      minCounts: The allowed minimum number of counts in one bin.  
#                 Obviously, if nData<minCount, it is impossible to fulfill
#                 this requirement.
#      There are additional optional input arguments collected in varargin.
#      statistcalMethod=varargin{1}: This function argument controls the
#                 method that is used for calculating the histogram and the
#                 local NG fraction. The following values are allowed:
#                 statistcalMethod<0.5: The parts parts in the bins are 
#                                       counted (default).
#                 statistcalMethod>=0.5: The kernel density approximation
#                                       is applied (approximation by radial
#                                       basis functions).
#      bAdapted=varargin{2}: This function argument controls, if the 
#                 histogram should have adapted bin sizes. The following 
#                 values are allowed:
#                 bAdapted<0.5: The bin sizes are equal. In this case the
#                               function input minCounts is ignored.
#                 bAdapted>=0.5: The bin sizes are adapted to the number of 
#                                parts in the bins (default).
#
#   function output:
#      pdfN: The probabilty density function (pdf) for each bin of the 
#            histogram. It is defined as the number of parts in the bin 
#            divided by the width of the bin.
#      histbins: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. 
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an 
#               exception is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      nBins<1: If the desired number of bins for the histogram is smaller 
#               than 1, an exception is thrown with the message: 
#                     "The desired number of bins must be larger than 0!"
#      minCounts>nData: If the allowed minimum number of counts in one bin  
#                is larger than than the number of sample data, the 
#                requirement on minCount can not be fulfilled. In that case
#                an exception is thrown with the message: 
#                      "It is imposible to fulfill the requirment on the 
#                       minimum number of counts in one bin!"

    ##################### check for correct data format and input parameter
    nData=np.size(DataIn)
    if np.squeeze(DataIn).ndim>1:
        errStr="Error in ComputeHistogramAdapted: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    if nData<1:
        errStr="Error in ComputeHistogramAdapted: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if nBins<1:
        errStr="Error in ComputeHistogramAdapted: The number of bins has to be larger than zero!"
        raise ValueError(errStr)
    if minCounts>nData:
        errStr="Error in ComputeHistogramAdapted: It is imposible to fulfill the requirment on the minimum number of counts in one bin!"
        raise ValueError(errStr)

    ################### compute adapted histogram and corresponding local ng fractions
    if bAdapted>=0.5:
        histN,histbins = HistCountsAdapted(DataIn,nBins,minCounts)
    else:
        histN,histbins = np.histogram(DataIn,nBins)
    nBinsTrue=np.size(histN)
    xWidth=histbins[1:nBinsTrue+1]-histbins[0:nBinsTrue]; # width of bins
    if statistcalMethod<0.5:
        pdfN=np.squeeze(histN)/np.squeeze(xWidth); # probability distribution is normalized by the width of the bins
    else:
        ### alternative method with kernel density approximation
        scalingDensity=0.1*np.std(DataIn); # heuristsic value for RBF scaling
        histNTmp=HistcountsFromMarginalLocalizedProbability(histbins,DataIn,scalingDensity)
        pdfN=np.squeeze(histNTmp)/np.squeeze(xWidth);

    return pdfN,histbins
##############################################################################
###################### end ComputeHistogramAdapted ###########################
##############################################################################
 

##############################################################################
################ HistcountsFromMarginalLocalizedProbability ##################
##############################################################################
def HistcountsFromMarginalLocalizedProbability(binEdges, xSample, scaling):
#HistcountsFromMarginalLocalizedProbability:   Compute the number of parts 
#in the given bins with a kernel density approximation.
#
#   Normally the number of parts in a bin is determined by counting the 
#   parts, whose value lies in the interval defined by the bin edges.
#   However, in a high-dimensional space or with a small number of parts 
#   this approach leads to very noisy results. Therefore, in this function 
#   the kernel density approximation is applied, i. e. the number of parts 
#   at x are described by radial basis functions with Gaussian kernel. 
#   Thus, the corresponding number in an interval (bin) can be calculated 
#   by integrating the radial basis functions over the interval. For a 
#   Gaussian kernel the integral can be evaluated analytically, which gives 
#   an error function.
#
#   function input:
#      binEdges: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. Thus, histbins has dimension (nBins+1,1) or (1,nBins+1).
#      xSample: The sample data from which the histogram should be derived. 
#               It has dimension (nSample,1), where nData is the number 
#               of data sets.
#      scaling: The scaling parameter for the Gaussian radial basis 
#               functions. The coordinates x are scaled (divided) by this
#               paremeter.
#
#   function output:
#      partsInBin: The number of parts in the specified bins.
#
#   Exceptions:
#      binEdges not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      length(binEdges)<2: If there are less than 2 bin edges an exception, 
#               no bin can be defined. Therefore an exception is thrown 
#               with the message: 
#                     "The array of bin edges must at least have two 
#                      entries!"
#      xSample empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      xSample not 1d: If the array of sample data is not 1d an exception 
#               is thrown with the message: 
#                     "The array of sample data has to be 1d!"

    ##################### check for correct data format and input parameter
    if np.squeeze(binEdges).ndim>1:
        errStr="Error in HistcountsFromMarginalLocalizedProbability: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(binEdges)
    if nEdges<2:
        errStr="Error in HistcountsFromMarginalLocalizedProbability: The array of bin edges must at least have two entries!"
        raise ValueError(errStr)
    nBins=nEdges-1
    if np.squeeze(xSample).ndim>1:
        errStr="Error in HistcountsFromMarginalLocalizedProbability: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    nSample=np.size(xSample)
    if nSample<1:
        errStr="Error in HistcountsFromMarginalLocalizedProbability: The array of sample data must not be empty!"
        raise ValueError(errStr)
    
    ##################### in case of row vectors
    binEdgesTmp=np.squeeze(binEdges)
    xSampleTmp=np.squeeze(xSample)
        
    ##################### compute the number of parts in the bins with 
    ##################### of Gaussian radial basis functions
    partsSmallerX = np.zeros((nBins+1, 1), float)
    normalizationFactor = 1 / (np.sqrt(2.0) * scaling)    # scaling from Gaussian kernel function
    for n in range(0, nBins+1):
        weights=np.zeros((nSample,1))
        for m in range(0,nSample):
            weights[m]= math.erf((binEdgesTmp[n] - xSampleTmp[m]) * normalizationFactor)   # integral of the Gaussian kernel function
        partsSmallerX[n] = np.sum(weights)
    partsInBin = np.round(0.5 * (partsSmallerX[1: nBins+1] - partsSmallerX[0: nBins]))  # integral over one bin is difference of integrated function at the edges
    return partsInBin
##############################################################################
############# end HistcountsFromMarginalLocalizedProbability #################
##############################################################################


##############################################################################
################## ComputeHistogramWithNGfractionAdapted #####################
##############################################################################
def ComputeHistogramWithNGfractionAdapted(DataIn,ClassLabelsIn,nBins,minCounts,statistcalMethod=0,bAdapted=1):
#ComputeHistogramWithNGfractionAdapted:   Compute histogram and kocal NG 
#fraction in bins for the given data.
#
#   From the given sample data the histogram for the selected parameter is 
#   determined. By default the bin sizes are adapted in such a way that no   
#   bin has lower counts than minCount (see the function HistCountsAdapted for 
#   details). However, this behaviour can be changed by the optional 
#   function input bAdapted (see description below). Furthermore, for this 
#   histogram the local ng fraction for each bin is calculated. Both
#   quantities, histogram and local NG fraction can be evaluated either by
#   simple counting of the parts in the bins or by the more advanced kernel
#   density approximation.
#
#   function input:
#      DataIn: Sample data from which the histogram should be derived. It 
#              has dimension (nData,1) or (1,nData), where nData is the  
#              number of data sets.
#      CLassLabelsIn: Labels for a binary classification of the sample data. 
#                     The label (-1) indicates ng parts, whereas the label 
#                     (+1) indicates good parts. The array must have  
#                     dimension (nData,1) or (1,nData).
#      nBins: Desired number of bins. The true number of bins in the
#             generated histogram might be smaller for pathological cases.
#      minCounts: The allowed minimum number of counts in one bin.  
#                 Obviously, if nData<minCount, it is impossible to fulfill
#                 this requirement.
#      statistcalMethod: This function argument controls the method that is 
#                        used for calculating the histogram and the local NG 
#                        fraction. The following values are allowed:
#                        statistcalMethod<0.5: The parts parts in the bins  
#                                              are counted (default).
#                        statistcalMethod>=0.5: The kernel density 
#                                               approximation is applied 
#                                               (approximation by radial
#                                                basis functions).
#      bAdapted: This function argument controls, if the histogram should have 
#                adapted bin sizes. The following values are allowed:
#                bAdapted<0.5: The bin sizes are equal. In this case the
#                              function input minCounts is ignored.
#                bAdapted>=0.5: The bin sizes are adapted to the number of 
#                               parts in the bins (default).
#
#   function output:
#      pdfN: The probabilty density function (pdf) for each bin of the 
#            histogram. It is defined as the number of parts in the bin 
#            divided by the width of the bin.
#      ngFracBin: The local ng fraction for each bin. It is defined as the 
#                 number of ng parts in the bin divided by the number of 
#                 all parts in the bin. 
#      ngFracBinError: The error of the local ng fraction for each bin. It 
#                      is derived from the assumption that NG parts and 
#                      good parts in each bin are distributed according to 
#                      a binomial distribution. 
#      histbins: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. 
#      ngFracGlobal: The global NG fraction, i. e. the number of all NG
#                    parts divided by the number of all parts.
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an 
#               exception is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      ClassLabelsIn not 1d: If the array for the class labels is not 1d an 
#               exception is thrown with the message: 
#                     "The array of class labels has to be 1d!"
#      nClassLabels~=nData: If the size of the class labels does not fit to
#               the size of the sample data an exception is thrown with the
#               message: 
#                     "The array of sample data must have the same length 
#                      as the array of class labels!"
#      nBins<1: If the desired number of bins for the histogram is smaller 
#               than 1, an exception is thrown with the message: 
#                     "The desired number of bins must be larger than 0!"
#      minCounts>nData: If the allowed minimum number of counts in one bin  
#                is larger than than the number of sample data, the 
#                requirement on minCount can not be fulfilled. In that case
#                an exception is thrown with the message: 
#                      "It is imposible to fulfill the requirment on the 
#                       minimum number of counts in one bin!"

    ##################### check for correct data format and input parameter
    nData=np.size(DataIn)
    if np.squeeze(DataIn).ndim>1:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    if nData<1:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: The array of sample data must not be empty!"
        raise ValueError(errStr)
    nLabels=np.size(ClassLabelsIn)
    if np.squeeze(ClassLabelsIn).ndim>1:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: The array of class labels has to be 1d!"
        raise ValueError(errStr)
    if nLabels!=nData:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: The array of sample data must have the same length as the array of class labels!"
        raise ValueError(errStr)
    if nBins<1:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: The number of bins has to be larger than zero!"
        raise ValueError(errStr)
    if minCounts>nData:
        errStr="Error in ComputeHistogramWithNGfractionAdapted: It is imposible to fulfill the requirment on the minimum number of counts in one bin!"
        raise ValueError(errStr)
    
    ################### compute adapted histogram and corresponding local ng fractions
    if bAdapted>=0.5:
        histN,histbins = HistCountsAdapted(DataIn,nBins,minCounts)
    else:
        histN,histbins = np.histogram(DataIn,nBins)
    nBinsTrue=np.size(histN)
    posNG=np.where(ClassLabelsIn<0)[0]
    ngFracGlobal=np.size(posNG)/nData
    xWidth=histbins[1:nBinsTrue+1]-histbins[0:nBinsTrue]; # width of bins
    if statistcalMethod<0.5:
        ngFracBin,ngFracBinError,ngFracGlobal = ComputeNGfractionInBins(DataIn,ClassLabelsIn,histbins);
        pdfN=np.squeeze(histN)/np.squeeze(xWidth); # probability distribution is normalized by the width of the bins
    else:
        ### alternative method with kernel density approximation
        scalingDensity=0.1*np.std(DataIn); # heuristsic value for RBF scaling
        ngFracBin,ngFracBinError=LocalizedNGfractionInBins(histbins,DataIn,posNG,scalingDensity);
        histNTmp=HistcountsFromMarginalLocalizedProbability(histbins,DataIn,scalingDensity)
        pdfN=np.squeeze(histNTmp)/np.squeeze(xWidth);
    
    return pdfN,histbins,ngFracBin,ngFracBinError,ngFracGlobal
##############################################################################
############### end ComputeHistogramWithNGfractionAdapted ####################
##############################################################################


##############################################################################
################ ComputeHistogramWithNGfractionCategorical ###################
##############################################################################
def ComputeHistogramWithNGfractionCategorical(DataIn,ClassLabelsIn):
#ComputeHistogramWithNGfractionCategorical:   Compute histogram and local 
#NG fraction in bins for the given data.
#
#   From the given sample data the histogram for the selected parameter is 
#   determined. For categorical KPIVs each bin corresponds to one category.
#   Furthermore, for this histogram the local ng fraction for each bin is 
#   calculated. Both quantities, histogram and local NG fraction are 
#   evaluated by simple counting of the parts in the bins. 
#
#   function input:
#      DataIn: Sample data from which the histogram should be derived. It 
#              has dimension (nData,1) or (1,nData), where nData is the  
#              number of data sets.
#      CLassLabelsIn: Labels for a binary classification of the sample data. 
#                     The label (-1) indicates ng parts, whereas the label 
#                     (+1) indicates good parts. The array must have  
#                     dimension (nData,1) or (1,nData).
#
#   function output:
#      pdfN: The number of parts (counts) for each bin of the histogram. 
#            This is different to the continuous case, where the 
#            probability density is used, because there bins can have
#            different widths.
#      ngFracBin: The local ng fraction for each bin. It is defined as the 
#                 number of ng parts in the bin divided by the number of 
#                 all parts in the bin. 
#      ngFracBinError: The error of the local ng fraction for each bin. It 
#                      is derived from the assumption that NG parts and 
#                      good parts in each bin are distributed according to 
#                      a binomial distribution. 
#      ngFracGlobal: The global NG fraction, i. e. the number of all NG
#                    parts divided by the number of all parts.
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an 
#               exception is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      ClassLabelsIn not 1d: If the array for the class labels is not 1d an 
#               exception is thrown with the message: 
#                     "The array of class labels has to be 1d!"
#      nClassLabels~=nData: If the size of the class labels does not fit to
#               the size of the sample data an exception is thrown with the
#               message: 
#                     "The array of sample data must have the same length 
#                      as the array of class labels!"
    
    tolZero=1.0e-12
    nCategoriesMax=1000
    
    ##################### check for correct data format and input parameter
    ##################### code for pandas dataframe
    if isinstance(DataIn,pd.DataFrame) | isinstance(DataIn,pd.Series):
        temp=DataIn.values
        columnTypes=DataIn.dtypes
        if columnTypes.iloc[0].name=='category': # defined as categorical
            DataCat=temp.astype('str')
        else:
            DataCat=temp

    ##################### code for numpy array
    else: 
        DataCat=DataIn

    if np.size(DataCat)<1:
        errStr="Error in ComputeHistogramWithNGfractionCategorical: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(DataCat).ndim>1:
        errStr="Error in ComputeHistogramWithNGfractionCategorical: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    nData=np.size(DataCat)
    shapeData=DataCat.shape
    try: n2 = shapeData[1]
    except: n2 = 1
    if n2==nData:
        DataCat=np.transpose(DataCat)
    nLabels=np.size(ClassLabelsIn)
    shapeData=ClassLabelsIn.shape
    try: n2 = shapeData[1]
    except: n2 = 1
    if n2==nLabels:
        ClassLabelsIn=np.transpose(ClassLabelsIn)
    if np.squeeze(ClassLabelsIn).ndim>1:
        errStr="Error in ComputeHistogramWithNGfractionCategorical: The array of class labels has to be 1d!"
        raise ValueError(errStr)
    if nLabels!=nData:
        errStr="Error in ComputeHistogramWithNGfractionCategorical: The array of sample data must have the same length as the array of class labels!"
        raise ValueError(errStr)
    
    ################### determine parts in categories and corresponding local NG fractions
    # temp=DataCat.value_counts()
    # KPIVCategories=temp.index
    # dummy=temp.iloc[:]
    KPIVCategories=np.unique(DataCat);
    
    nCategories=np.size(KPIVCategories);
    if nCategories<=nCategoriesMax:
        pdfN=np.zeros([nCategories,1])
        ngFracBin=np.zeros([nCategories,1]);
        ngFracBinError=np.ones([nCategories,1]);
        nPartsNGAll=0
        for n in range(0,nCategories):
            posParts=np.argwhere(DataCat==KPIVCategories[n])[:,0]
            pdfN[n]=np.size(posParts)
            posNG=np.argwhere(ClassLabelsIn[posParts]<0)[:,0]
            nPartsNG=np.size(posNG)
            if pdfN[n]>0:
                ngFracBin[n]=nPartsNG/pdfN[n]
            if ngFracBin[n]>=tolZero and ngFracBin[n]<=1.0-tolZero:
                ngFracBinError[n]=6.0*np.sqrt(ngFracBin[n]*(1.0-ngFracBin[n])/pdfN[n]); 
                            # error of NG fraction from variance of Binomial distribution
            # nPartsCat=0
            # nPartsNG=0
            # pdfN[n]=dummy[n]
            # for m in range(0,nData):
            #     if DataCat.iloc[m]==KPIVCategories[n]:
            #         nPartsCat+=1
            #         if ClassLabelsIn[m]<0: # NG part
            #             nPartsNG+=1
            # if nPartsCat>0:
            #     ngFracBin[n]=nPartsNG/nPartsCat
            # if ngFracBin[n]>=tolZero and ngFracBin[n]<=1.0-tolZero:
            #     ngFracBinError[n]=6.0*np.sqrt(ngFracBin[n]*(1.0-ngFracBin[n])/pdfN[n]); 
            #                 # error of NG fraction from variance of Binomial distribution
            nPartsNGAll+=nPartsNG
        ngFracGlobal=nPartsNGAll/nData;
    else: # too much categories => use function for continuous KPIVs
        pdfN,histbins,ngFracBin,ngFracBinError,ngFracGlobal=ComputeHistogramWithNGfractionAdapted(DataIn,ClassLabelsIn,bAdapted=0,minCounts=-1)
    
    return pdfN,ngFracBin,ngFracBinError,ngFracGlobal
##############################################################################
############# end ComputeHistogramWithNGfractionCategorical ##################
##############################################################################


##############################################################################
######################### LocalizedNGfractionInBins ##########################
##############################################################################
def LocalizedNGfractionInBins(binEdges,xSample,posNGSample,scaling):
#LocalizedNGfractionInBins:   Compute the localized NG fraction and its 
#error in the given bins.
#
#   The local NG fraction in a bin is defined as the number of NG parts in
#   this bin divided by the number of all parts in this bin. However, in a 
#   high-dimensional space or with a small number of parts this approach 
#   leads to very noisy results. Therefore, in this function the kernel 
#   density approximation is applied, i. e. the number of NG parts at x and 
#   the number of all parts at x are described by radial basis functions 
#   with Gaussian kernel. Thus, the corresponding number in an interval
#   (bin) can be calculated by integrating the radial basis functions over
#   the interval. For a Gaussian kernel the integral can be evaluated
#   analytically, which gives an error function.
#
#   It is also possible to estimate the error of the local bg fraction. To 
#   this end we assume that the probability for a part to be ng is p. Then,
#   the probability to find K ng parts in a bin with N parts in total can
#   be described by the binomial distribution B(K,N,p). Its standard
#   deviation sqrt(N*p*(1-p)) is proportional to the statistical
#   uncertainty for the number of ng parts found (K). In order to estimate 
#   the uncertainty of the ng fraction (K/N), this has to divided by N. It
#   is convenient to define a multiple of this quantity as the error of the
#   ng fraction. An analogon to the 6 sigma interval of the normal
#   distribution would be the error 6*sqrt(p*(1-p)/N).
#
#   function input:
#      binEdges: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. Thus, histbins has dimension (nBins+1,1) or (1,nBins+1).
#      xSample: The sample data from which the histogram should be derived. 
#               It has dimension (nSample,1), where nData is the number 
#               of data sets.
#      posNGsample: The indices for NG parts in xSample. It has to be 1d, 
#                   either a row or a column vector.
#      scaling: The scaling parameter for the Gaussian radial basis 
#               functions. The coordinates x are scaled (divided) by this
#               paremeter.
#
#   function output:
#      ngFracInBins: Local ng fraction for each bin. It has dimension 
#                    (nBins,1).
#      ngFracError: Error of the ng fraction for each bin (see definition
#                   above). It has dimension (nBins,1).
#
#   Exceptions:
#      binEdges not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      length(binEdges)<2: If there are less than 2 bin edges an exception, 
#               no bin can be defined. Therefore an exception is thrown 
#               with the message: 
#                     "The array of bin edges must at least have two 
#                      entries!"
#      xSample empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      xSample not 1d: If the array of sample data is not 1d an exception 
#               is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      posNGsample not 1d: If the array for of the indices for the NG parts 
#               is not 1d an exception is thrown with the message: 
#                     "The array of the indices for the NG parts has to be 
#                       1d!"
#      posNGsample empty: If there are no indices for the NG parts an  
#               exception is thrown with the message: 
#                     "The array of the indices for the NG parts must not 
#                       be empty!"
#      If some indices for the NG parts are smaller than 1 or larger than 
#               nSample an exception is thrown with the message: 
#                     "Some indices for the NG parts are out of bounds!"

    ##################### check for correct data format and input parameter
    if np.squeeze(binEdges).ndim>1:
        errStr="Error in LocalizedNGfractionInBins: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(binEdges)
    if nEdges<2:
        errStr="Error in LocalizedNGfractionInBins: The array of bin edges must at least have two entries!"
        raise ValueError(errStr)
    nBins=nEdges-1
    if np.squeeze(xSample).ndim>1:
        errStr="Error in LocalizedNGfractionInBins: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    nSample=np.size(xSample)
    if nSample<1:
        errStr="Error in LocalizedNGfractionInBins: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(posNGSample).ndim>1:
        errStr="Error in LocalizedNGfractionInBins: The array of the indices for the NG parts has to be 1d!"
        raise ValueError(errStr)
    nNG=np.size(posNGSample)
    if nNG<1:
        errStr="Error in LocalizedNGfractionInBins: The array of the indices for the NG parts must not be empty!"
        raise ValueError(errStr)
    if nNG>nSample:
        errStr="Error in LocalizedNGfractionInBins: There are more indices for NG parts than samples!"
        raise ValueError(errStr)
    indMin=min(np.squeeze(posNGSample))
    indMax=max(np.squeeze(posNGSample))
    if indMin<0 or indMax>nSample-1:
        errStr="Error in LocalizedNGfractionInBins: Some indices for the NG parts are out of bounds!"
        raise ValueError(errStr)
    
    ##################### in case of row vectors
    binEdgesTmp=np.squeeze(binEdges)
    xSampleTmp=np.squeeze(xSample)
    posNGSampleTmp=np.squeeze(posNGSample)
    
    ##################### compute the localized ng fraction in the bins with 
    ##################### the help of Gaussian radial basis functions
    partsSmallerX=np.zeros((nBins+1,1),float);
    NGpartsSmallerX=np.zeros((nBins+1,1),float);
    normalizationFactor=1.0/(math.sqrt(2.0)*scaling); # scaling from Gaussian kernel function
    for n in range(0,nBins+1):
        weights=np.zeros((nSample,1))
        for m in range(0,nSample):
            weights[m]= math.erf((binEdgesTmp[n] - xSampleTmp[m]) * normalizationFactor)   # integral of the Gaussian kernel function
                    # integral of the Gaussian kernel function (except a factor 0.5)
        partsSmallerX[n]=sum(weights)
        NGpartsSmallerX[n]=sum(weights[posNGSampleTmp])
    partsInBin=0.5*(partsSmallerX[1:nBins+1]-partsSmallerX[0:nBins])
                    # integral over one bin is difference of integrated
                    # function at the edges
                    # the factor 0.5 comes from the analytical integration
    NGpartsInBin=0.5*(NGpartsSmallerX[1:nBins+1]-NGpartsSmallerX[0:nBins])
                    # same as above for the NG parts
    posNonZeroBins=np.squeeze(np.argwhere(np.squeeze(partsInBin)>0)) # find bins with parts in it
    ngFracInBins=np.zeros((nBins,1),float)
    ngFracInBins[posNonZeroBins]=NGpartsInBin[posNonZeroBins]/partsInBin[posNonZeroBins] # definition of local NG fraction
    
    ##################### compute the error of the localized ng fraction in the 
    ##################### bins based on the assumption that they are binomially 
    ##################### distributed 
    ngFracError=np.ones((nBins,1),float);
    tol=1.0e-8;
    posWellBehaved=np.squeeze(np.argwhere(np.logical_and(np.squeeze(ngFracInBins)>tol,np.squeeze(ngFracInBins)<1-tol))) # select only meaningful ng fractions between epsilon and 1-espilon
    ngFracError[posWellBehaved]=6.0*np.sqrt(ngFracInBins[posWellBehaved]*(1.0-ngFracInBins[posWellBehaved])/NGpartsInBin[posWellBehaved])
                                        # error of ng fraction from variance of Binomial distribution
    
    return ngFracInBins,ngFracError
##############################################################################
####################### end LocalizedNGfractionInBins ########################
##############################################################################


##############################################################################
########################### ComputeNGfractionInBins ##########################
##############################################################################
def ComputeNGfractionInBins(DataInput, ClassLabels, histbins):
#ComputeNGfractionInBins:   Compute the local NG fraction in each bin.
#   For each bin of a given histogram the local NG fraction is calculated.
#   It is defined as the number of ng parts in this bin divided by the
#   number of all parts in this bin. If a part is ng, can be determined by
#   its class label. The bins are defined by the array histbins.
#
#   It is also possible to estimate the error of the local bg fraction. To 
#   this end we assume that the probability for a part to be ng is p. Then,
#   the probability to find K ng parts in a bin with N parts in total can
#   be described by the binomial distribution B(K,N,p). Its standard
#   deviation sqrt(N*p*(1-p)) is proportional to the statistical
#   uncertainty for the number of ng parts found (K). In order to estimate 
#   the uncertainty of the NG fraction (K/N), this has to divided by N. It
#   is convenient to define a multiple of this quantity as the error of the
#   NG fraction. An analogon to the 6 sigma interval of the normal
#   distribution would be the error 6*sqrt(p*(1-p)/N).
#
#   function input:
#      DataIn: Sample data that should be evaluated. It has dimension 
#              (nData,1), (nData,) or (1,nData), where nData is the number of data 
#              sets.
#      CLassLabels: Labels for a binary classification of the sample data. 
#                   The label (-1) indicates ng parts, whereas the label 
#                   (+1) indicates good parts. The array must have  
#                   dimension (nData,1), (nData,) or (1,nData).
#      histbins: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. For n bins histbins has dimension (nBins+1,1),  
#                (nBins+1,) or (1,nBins+1).
#
#   function output:
#      ngFracBin: Local NG fraction for each bin. It has dimension 
#                 (nBins,1).
#      ngFracError: Error of the NG fraction for each bin (see definition
#                   above). It has dimension (nBins,1).
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an 
#               exception is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      ClassLabels not 1d: If the array for the class labels is not 1d an 
#               exception is thrown with the message: 
#                     "The array of class labels has to be 1d!"
#      histbins not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      nClassLabels~=nData: If the size of the class labels does not fit to
#               the size of the sample data an exception is thrown with the
#               message: 
#                     "The array of sample data must have the same length 
#                      as the array of class labels!"
#      length(histbins)<2: If the size of bin edges is smaller than 2, no
#               bins can be defined. In that case an exception is thrown 
#               with the message: 
#                          "The array of bin edges must have at least 2 

############# check for valid input
    if np.squeeze(DataInput).ndim>1:
        errStr="Error in ComputeNGfractionInBins: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    nData=np.size(DataInput)
    if nData<1:
        errStr="Error in ComputeNGfractionInBins: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(ClassLabels).ndim>1:
        errStr="Error in ComputeNGfractionInBins: The array of class labels has to be 1d!"
        raise ValueError(errStr)
    nLabels=np.size(ClassLabels)
    if nLabels!=nData:
        errStr="Error in ComputeNGfractionInBins: The array of sample data must have the same length as the array of class labels!"
        raise ValueError(errStr)
    if np.squeeze(histbins).ndim>1:
        errStr="Error in ComputeNGfractionInBins: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(histbins)
    if nEdges<2:
        errStr="Error in ComputeNGfractionInBins: The array of bin edges must have at least 2 elements!"
        raise ValueError(errStr)
       
    nBins = nEdges - 1   # number of bins is one less than the bin boundaries
    posNG=np.where(ClassLabels<0)[0]
    ngFracGlobal=np.size(posNG)/nData

############# reshape arrays to the expected form
    DataInput=np.reshape(DataInput,(nData,))
    ClassLabels=np.reshape(ClassLabels,(nData,))
    histbins=np.reshape(histbins,(nEdges,))

######## compute NG fraction for each bin:
######## number of ng parts in bin/number of all parts in bin
######## Additionally the error of the NG fraction is calculated.
######## Based on the assumption that the ng parts in each bin are distributed according to a Binominal distribution
######## (probability of finding k ng parts in N total parts) the variance sigma^2=N*p*(1-p) of the Binomial
######## distribution is a measure for the squared uncertainty of the number of ng parts. Consequently, the
######## uncertainty of the NG fraction is proportional to sigma/N=(p*(1-p)/N)^(1/2).
######## p is the probability to find a ng part in thins bin, which should be equal to the NG fraction
######## The error is defined as 4*sigma/N (4-sigma confidence interval)
    ngFracBin = np.zeros((nBins, 1), float)
    ngFracError = np.zeros((nBins, 1), float)
    for n in range(0, nBins):
        posBin = np.where(DataInput >= histbins[n], DataInput, histbins[n+1]+3)
        posBin = np.argwhere(posBin < histbins[n+1])    # find parts in bin
        posBinNG = 0
        for i in range(0, len(posBin)):
            if ClassLabels[posBin[i][0]] == -1: posBinNG += 1   # find ng parts in bin
        if len(posBin) > 0:  # calculation is only possible for bins that are not empty
            ngFracBin[n] = posBinNG / len(posBin)
            if ngFracBin[n] != 0 and ngFracBin[n] != 1:
                ngFracError[n] = 4*np.sqrt(ngFracBin[n] * (1.0 - ngFracBin[n]) / len(posBin))   # error of NG fraction from variance of Binomial distribution
            else:
                ngFracError[n] = 1
    return ngFracBin, ngFracError, ngFracGlobal
##############################################################################
######################## end ComputeNGfractionInBins #########################
##############################################################################



##############################################################################
######################### PlotHistogramWithNGfraction ########################
##############################################################################
def PlotHistogramWithNGfraction(histN, histbins, ngFracBin, ngFracError, FeatureName,bShowErrorBars=1,countDensity=1,bSaveFig=-1,SaveFigDestination="/charts"):
#PlotHistogramWithNGfraction:   Plot a histogram and the local NG fraction 
#for each bin.
#
#   A diagram with the given histogram data is shown together with the
#   local NG fraction for each bin. The counts are scaled by the bin
#   width. The plot of the local NG fraction can optionally complemented by
#   its error bars.
#
#   function input:
#      histN: Number of parts in each bin. It has dimension (nBins,1) or 
#             (1,nBins), where nBins is the number of bins. 
#      histbins: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. Thus, histbins has dimension (nBins+1,1) or (1,nBins+1).
#      ngFracBin: Local NG fraction for each bin. It has dimension 
#                 (nBins,1) or (1,nBins).
#      ngFracError: Error of the NG fraction for each bin. It has 
#                   dimension (nBins,1) or (1,nBins).
#      FeatureName: A string with the name of the selected parameter for the 
#                   histogram.
#      bShowErrorBar: This function argument controls a certain aspect of the 
#                     optional plotting. If bShowErrorBars>0 the error bars 
#                     for the NG fraction will be shown, otherwise not. The 
#                     default value is +1.
#      countDensity: This function argument controls whether the count density 
#                    (number of counts/width of the bin) or the probability 
#                    density (count density/nData) will be plotted for the 
#                    histogram. If countDensity is smaller than 0 the count 
#                    density will be shown, otherwise the probability density. 
#                    The default value is +1.
#      bSaveFig: THis function argument controls if the figure should be saved 
#                as a png-file. If bSaveFig>0 the plot will be saved, otherwise 
#                not. The default value is -1.
#      SaveFigDestination: This function argument specifies the file path, 
#                          where the figure should be saved. Its default value 
#                          is "./charts" 
#
#   function output:
#      This function produces no output besides a diagram.
#
#   Exceptions:
#      histN not 1d: If the array for the hist counts is not 1d an 
#               exception is thrown with the message: 
#                     "The array of hist counts has to be 1d!"
#      histN empty: If there are no hist counts an exception is thrown 
#               with the message: 
#                     "The array of hist counts must not be empty!"
#      histbins not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      length(histbins)~=nBins+1: If the size of histogram counts does not  
#               fit to the size of the bin edges an exception is thrown 
#               with the message: 
#                     "The bin edges must have one element more than 
#                      the counts for the bins"
#      ngFracBin not 1d: If the array for local NG fraction is not 1d an 
#               exception is thrown with the message: 
#                     "The array of the local NG fraction has to be 1d!"
#      length(ngFracBin)~=nBins: If the size of local NG fraction does not 
#               fit to the size of the bins an exception is thrown with the
#               message: 
#                     "The local NG fraction must have the same length as 
#                      the counts for the bins"
#      ngFracError not 1d: If the array for the error of the local ng  
#               fraction is not 1d an exception is thrown with the message: 
#                     "The array for the error of the local NG fraction has
#                      to be 1d!"
#      length(ngFracError)~=nBins: If the size of local NG fraction does not 
#               fit to the size of the bins an exception is thrown with the
#               message: 
#                     "The error of the local NG fraction must have the  
#                      same length as the counts for the bins"

############# check for valid input
    if np.squeeze(histN).ndim>1:
        errStr="Error in PlotHistogramWithNGfraction: The array of hist counts has to be 1d!"
        raise ValueError(errStr)
    nBins=np.size(histN)
    if nBins<1:
        errStr="Error in PlotHistogramWithNGfraction: The array of hist counts must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(histbins).ndim>1:
        errStr="Error in PlotHistogramWithNGfraction: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(histbins)
    if nEdges!=nBins+1:
        errStr="Error in PlotHistogramWithNGfraction: The bin edges must have one element more than the counts for the bins!"
        raise ValueError(errStr)
    if np.squeeze(ngFracBin).ndim>1:
        errStr="Error in PlotHistogramWithNGfraction: The array of the local NG fraction has to be 1d!"
        raise ValueError(errStr)
    n1=np.size(ngFracBin)
    if n1!=nBins:
        errStr="Error in PlotHistogramWithNGfraction: The local NG fraction must have the same length as the counts for the bins!"
        raise ValueError(errStr)
    if np.squeeze(ngFracError).ndim>1:
        errStr="Error in PlotHistogramWithNGfraction: The array for the error of the local NG fraction has to be 1d!"
        raise ValueError(errStr)
    n1=np.size(ngFracError)
    if n1!=nBins:
        errStr="Error in PlotHistogramWithNGfraction: The error of the local NG fraction must have the same length as the counts for the bins!"
        raise ValueError(errStr)
       
    nBins = len(histbins)-1  # number of bins is one less than the bin boundaries
    binPos=0.5*(histbins[0:nBins]+histbins[1:nBins+1])
    binWidth=histbins[1:nBins+1]-histbins[0:nBins]
    h1, ax1 = plt.subplots(figsize=(10, 5))   # open new diagram

    if countDensity<0:
        ax1.bar(binPos,np.divide(histN,binWidth),width=binWidth)
        ax1.set_ylabel("count density [a.u.]", fontsize=18)    # label for the left y-axis
    else:
        nData=np.sum(histN)
        ax1.bar(binPos,np.divide(histN,binWidth)/nData,width=binWidth)
        ax1.set_ylabel("probability density [a.u.]", fontsize=18)    # label for the left y-axis

    ax2 = ax1.twinx()   # second plot has y-axis at the right side
    ax2.plot(binPos, ngFracBin*100, 'ro')    # plot NG fraction at bin centers
    ###########axLimits = ax2.axis()
    if bShowErrorBars>0:
        ax2.errorbar(binPos, ngFracBin[:, 0]*100, 100*ngFracError[:, 0], 0, 'ro')  # plot error bar for NG fraction
        axLimits = ax2.axis()
        ax2.set_ylim(axLimits[2], axLimits[3])  # use same y-axis scaling as for NG fraction
    ax1.set_xlabel("x [a.u.]", fontsize=18)  # label for x-axis
    ax2.set_ylabel(r"$\mathregular{f_n}$$\mathregular{_g}$ [#]", fontsize=18)   # label for the right y-axis
    ax1.set_title('fraction of ng parts in dependence of ' + FeatureName, fontsize=14)  # title of the diagram
    ax1.grid()
    ax2.grid()

    plt.subplots_adjust(left=0.125, right=0.875, top=0.88, bottom=0.12)
    
    if bSaveFig>0:
        cwd=os.getcwd()
        DirToCreate=os.path.normpath(cwd+SaveFigDestination)
        if (os.path.exists(DirToCreate))==False:
            os.mkdir(DirToCreate)
        FileNameTmp="/NGfraction_" + FeatureName + ".png"
        FileName=os.path.normpath(DirToCreate+FileNameTmp)
        plt.savefig(FileName)
    plt.show()
##############################################################################
###################### end PlotHistogramWithNGfraction #######################
##############################################################################
   


##############################################################################
################################## JoinBins ##################################
##############################################################################
def JoinBins(histCountsIn, binEdgesIn, binPos):
#JoinBins:  Join the specified bins of a histogram
#   Join the bins with index binPos and binPos+1, i. e. they are replaced 
#   by one bin. If binPos is the index for the last bin in the histogram, 
#   all bins remain unchanged.
# 
#   The left boundary of the joined bin is taken from binPos and the right 
#   boundary from binPos+1. The number of counts in the new bin is the sum 
#   of the counts in the two joined bins.
#
#   function input:
#      histCountsIn: Number of parts in each bin. It has dimension (nBins,)
#                    (nBins,1) or (1,nBins), where nBins is the number of bins. 
#      binEdgesIn: Values for the consecutive bin edges, i. e. 
#                  binEdgesIn[n] is the left edge of bin n, whereas 
#                  binEdgesIn[n+1] is its right edge. Thus, binEdgesIn has 
#                  dimension (nBins+1,), (nBins+1,1) or (1,nBins+1). 
#      binPos: Index of the bin that will be joined with its right 
#              neighbour (binPos+1).
#
#   function output:
#      histCountsOut: New number of parts in each bin. It has dimension 
#                    (nBins-1,).
#      binEdgesOut: New values for the consecutive bin edges. It has
#                   dimension (nBins,).
#
#   Exceptions:
#      histCountsIn not 1d: If the array for the hist counts is not 1d an 
#               exception is thrown with the message: 
#                     "The array of hist counts has to be 1d!"
#      binEdgesIn not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      nBins<2: If there are less than 2 bins, it is not possible to join
#               them. In that case an exception is thrown with the message: 
#                     "There have to be at least 2 bins in order to join 
#                      them!"
#      binPos<0: If binPos<0, the specified index is out of the bounds of
#                the histogram. In that case an exception is thrown with 
#                the message: 
#                      "The index of the bin that should be joined is 
#                       smaller than 1!"
#      binPos>nBins-1: If binPos>nBins-1, the specified index is out of the 
#                      bounds of the histogram. In that case an exception is  
#                      thrown with the message: 
#                            "The index of the bin that should be joined is 
#                             larger than the number of bins!"
#      len(binEdges)!=nBins+1: If the size of histogram counts does not  
#                    fit to the size of the bin edges an 
#                    exception is thrown with the message: 
#                          "The bin edges must have one element more than 
#                           the counts for the bins"

############# check for valid input
    if np.squeeze(histCountsIn).ndim>1:
        errStr="Error in JoinBins: The array of hist counts has to be 1d!"
        raise ValueError(errStr)
    nBinsIn=np.size(histCountsIn)
    if nBinsIn<1:
        errStr="Error in JoinBins: The array of bins must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(binEdgesIn).ndim>1:
        errStr="Error in JoinBins: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(binEdgesIn)
    if nBinsIn<2:
        errStr="Error in JoinBins: There have to be at least 2 bins in order to join them!"
        raise ValueError(errStr)
    if binPos<0:
        errStr="Error in JoinBins: The index of the bin that should be joined is smaller than 0!"
        raise ValueError(errStr)
    if binPos>nBinsIn-1:
        errStr="Error in JoinBins: The index of the bin that should be joined is larger than the number of bins!"
        raise ValueError(errStr)
    if nEdges!=nBinsIn+1:
        errStr="Error in JoinBins: The bin edges must have one element more than the counts for the bins!"
        raise ValueError(errStr)
############# reshape arrays to the expected form
    histCountsIn=np.reshape(histCountsIn,(nBinsIn,))
    binEdgesIn=np.reshape(binEdgesIn,(nEdges,))

############# join bin counts
    histCountsOut = np.zeros((nBinsIn-1, 1), float)[:,0]
    if binPos != 0 and binPos<nBinsIn: histCountsOut[0:binPos] = histCountsIn[0:binPos]    # all bins before the specified bin remain unchanged
    if binPos < nBinsIn-1:
        histCountsOut[binPos] = histCountsIn[binPos] + histCountsIn[binPos+1]   # add counts for the specified bins
        histCountsOut[binPos+1:nBinsIn] = histCountsIn[binPos+2:nBinsIn+1]  # all bins after the specified bin remain unchanged
    else: return histCountsIn, binEdgesIn

############# join bin edges
    binEdgesOut = np.zeros((nBinsIn, 1), float)[:,0]
    binEdgesOut[0:binPos+1] = binEdgesIn[0:binPos+1]    # all bins before the specified bin remain unchanged
    if binPos < nBinsIn-1:
        binEdgesOut[binPos+1] = binEdgesIn[binPos+2]    # new right boundary for the specified bin
        if binPos+1<nBinsIn:
            binEdgesOut[binPos+2:nBinsIn] = binEdgesIn[binPos+3:nBinsIn+1]  # all bins after the specified bin remain unchanged
    else: return histCountsIn, binEdgesIn
    return histCountsOut, binEdgesOut
##############################################################################
############################### end JoinBins #################################
##############################################################################



##############################################################################
################################## SplitBin ##################################
##############################################################################
def SplitBin(DataIn, histCountsIn, binEdgesIn, binPos):
#SplitBin:  Split the specified bin of a histogram
#   Split the bin with index binPos, i. e. it is replaced by two bins. 
# 
#   The spedified bin is divided into two bins by introducing a new bin 
#   edge in the center of the existing bin at 
#   binEdgeNew=0.5*(binEdgesIn[binPos]+binEdgesIn[binPos+1]). Thus, the 
#   left new bin has bin edges [binEdgesIn[binPos],binEdgeNew), whereas the
#   right new bin has bin edges [binEdgeNew,binEdgesIn[binPos+1]). The
#   corresponding counts for the histogram are determined from DataIn.
#
#   function input:
#      DataIn: Sample data from which the histogram has been derived. It 
#              has dimension (nData,1) or (1,nData), where nData is the  
#              number of data sets.
#      histCountsIn: Number of parts in each bin. It has dimension 
#                    (nBins,1), (nBins,) or (1,nBins), where nBins is the  
#                    number of bins. 
#      binEdgesIn: Values for the consecutive bin edges, i. e. 
#                  binEdgesIn[n] is the left edge of bin n, whereas 
#                  binEdgesIn[n+1] is its right edge. Thus, binEdgesIn 
#                  has dimension (nBins+1,1), (nBins+1,) or (1,nBins+1).
#      binPos: Index of the bin that will be split into two bins. 
#
#   function output:
#      histCountsOut: New number of parts in each bin. It has dimension 
#                    (nBins+1,).
#      binEdgesOut: New values for the consecutive bin edges. It has
#                   dimension (nBins+2,).
#
#   Exceptions:
#      DataIn not 1d: If the array for the sample data is not 1d an exception 
#               is thrown with the message: 
#                     "The array of sample data has to be 1d!"
#      DataIn empty: If there are no sample data an exception is thrown 
#               with the message: 
#                     "The array of sample data must not be empty!"
#      histCountsIn not 1d: If the array for the hist counts is not 1d an 
#               exception is thrown with the message: 
#                     "The array of hist counts has to be 1d!"
#      binEdgesIn not 1d: If the array for the bin edges is not 1d an 
#               exception is thrown with the message: 
#                     "The array of bin edges has to be 1d!"
#      nBins<1: If there are no bins in the histogram an exception is 
#               thrown with the message: 
#                     "The array of bins must not be empty!"
#      binPos<1: If binPos<1, the specified index is out of the bounds of
#                the histogram. In that case an exception is thrown with 
#                the message: 
#                      "The index of the bin that should be split is 
#                       smaller than 1!"
#      binPos>nBins: If binPos>nBins, the specified index is out of the 
#                    bounds of the histogram. In that case an exception is  
#                    thrown with the message: 
#                          "The index of the bin that should be split is 
#                           larger than the number of bins!"
#      length(binEdges)!=nBins+1: If the size of histogram counts does not  
#                    fit to the size of the bin edges an 
#                    exception is thrown with the message: 
#                          "The bin edges must have one element more than 
#                           the counts for the bins"

############# check for valid input
    if np.squeeze(DataIn).ndim>1:
        errStr="Error in SplitBin: The array of sample data has to be 1d!"
        raise ValueError(errStr)
    if np.size(DataIn)<1:
        errStr="Error in SplitBin: The array of sample data must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(histCountsIn).ndim>1:
        errStr="Error in SplitBin: The array of hist counts has to be 1d!"
        raise ValueError(errStr)
    nBinsIn=np.size(histCountsIn)
    if nBinsIn<1:
        errStr="Error in SplitBin: The array of bins must not be empty!"
        raise ValueError(errStr)
    if np.squeeze(binEdgesIn).ndim!=1:
        errStr="Error in SplitBin: The array of bin edges has to be 1d!"
        raise ValueError(errStr)
    nEdges=np.size(binEdgesIn)
    if binPos<0:
        errStr="Error in SplitBin: The index of the bin that should be split is smaller than 0!"
        raise ValueError(errStr)
    if binPos>nBinsIn-1:
        errStr="Error in SplitBin: The index of the bin that should be split is larger than the number of bins!"
        raise ValueError(errStr)
    if nEdges!=nBinsIn+1:
        errStr="Error in SplitBin: The bin edges must have one element more than the counts for the bins!"
        raise ValueError(errStr)

############# reshape arrays to the expected form
    histCountsIn=np.reshape(histCountsIn,(nBinsIn,))
    binEdgesIn=np.reshape(binEdgesIn,(nEdges,))

############# split bin edges
    binEdgesOut = np.zeros((nBinsIn+2, 1), float)[:, 0]
    binEdgesOut[0:binPos+1] = binEdgesIn[0:binPos+1]    # all bins before the specified bin remain unchanged
    binEdgesOut[binPos+1] = 0.5*(binEdgesIn[binPos] + binEdgesIn[binPos+1])  # new boundary is in the center of the specified bin
    binEdgesOut[binPos+2:nBinsIn+3] = binEdgesIn[binPos+1:nBinsIn+2]    # all bins after the specified bin remain unchanged

############# split bin counts
    histCountsOut = np.zeros((nBinsIn+1, 1), float)[:, 0]
    if binPos != 0: histCountsOut[0:binPos] = histCountsIn[0:binPos]    # all bins before the specified bin remain  unchanged

    posTmp = np.where(DataIn >= binEdgesOut[binPos], DataIn, binEdgesOut[binPos+1]+3)
    posTmp = np.argwhere(posTmp < binEdgesOut[binPos+1])    # find parts in the left part of the splitted bin
    histCountsOut[binPos] = len(posTmp)
    posTmp = np.where(DataIn >= binEdgesOut[binPos+1], DataIn, binEdgesOut[binPos + 2] + 3)
    posTmp = np.argwhere(posTmp < binEdgesOut[binPos + 2]+(binPos==nBinsIn-1))  # find parts in the left part of the splitted bin
    histCountsOut[binPos+1] = len(posTmp)

    histCountsOut[binPos+2:nBinsIn+2] = histCountsIn[binPos+1:nBinsIn+1]  # all bins after the specified bin remain unchanged
    return histCountsOut, binEdgesOut
##############################################################################
############################### end SplitBin #################################
##############################################################################



