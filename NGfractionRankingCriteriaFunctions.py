import numpy as np
import DataScienceUtilityFunctions as Utility

##############################################################################
#################### NGfractionRankingCriteriaContinuous #####################
##############################################################################
def NGfractionRankingCriteriaContinuous(pdfN,ngFracBin,ngFracBinError,binEdges,ngFracGlobal,nSelected):
#NGfractionRankingCriteriaContinuous:   Calculate several KPIV ranking 
#criteria based on the local ng fraction (only for continuous KPIVs).
#
#   Attention: This only works for continuous KPIVs!!!!!!!!!!!!!!!!
#              If you apply the algorithm to categorical KPIVs, the results
#              will not be reliable. Categorical KPIVs have to be treated 
#              separately.
#
#   From the properties of the histogram and the properties of the 
#   corresponding local NG fraction several criteria are derived, which can 
#   distinguish good from bad performance of the production. They are based 
#   on the form of the two curves (histogram and local NG fraction) and 
#   their alignment. They are collected in a Matlab structure, which is the 
#   output of this function. A detailed description of the different 
#   ranking criteria can be found below in the description of this 
#   structure.
#
#   function input:
#      pdfN: The probabilty density function (pdf) for each bin of the 
#            histogram. It is defined as the number of parts in the bin 
#            divided by the width of the bin. It has dimension (nBins,1) or 
#            (1,nBins), where nBins is the number of bins.
#      ngFracBin: The local ng fraction for each bin. It is defined as the 
#                 number of ng parts in the bin divided by the number of 
#                 all parts in the bin. The array must have dimension 
#                 (nBins,1) or (1,nBins).
#      ngFracBinError: The error of the local ng fraction for each bin. It 
#                      is derived from the assumption that NG parts and 
#                      good parts in each bin are distributed according to 
#                      a binomial distribution. The array must have 
#                      dimension (nBins,1) or (1,nBins).
#      binEdges: Values for the consecutive bin edges, i. e. histbins[n] is
#                the left edge of bin n, whereas histbins[n+1] is its right
#                edge. Thus, histbins has dimension (nBins+1,1) or 
#                (1,nBins+1).
#      ngFracGlobal: The global NG fraction, i. e. the number of all NG
#                    parts divided by the number of all parts.
#      nSelected: Thew number of central bins that should be taken into 
#                 account for the determination of the ranking criteria. If 
#                 it is larger than nBins, all bins will be selected. If it
#                 is smaller than 2, 2 bins will selected.
#
#   function output:
#       RankingCriteria: A Matlab structure that collects different ranking
#           criteria. The following quantities are contained:
#           CentralNGfracStd: The standard deviation of the local NG 
#               fraction derived from the nSelected central bins of the 
#               histogram divided by the global NG fraction.
#           CentralDiffNGfracStd: The difference between the maximum and 
#               the minimum local NG fraction for the nSelected central 
#               bins divided by the global NG fraction.
#           RatioStdPXandNGfrac: The standard deviation of the KPIV's 
#           	histogram divided by the standard deviation of the local 
#               NG fraction.
#           WeightedAverageNGfrac: The weighted average of the local NG 
#               fraction with the reciprocal of the square of the bin count
#               as weights. This average is normalized by the global NG 
#               fraction.
#           ShiftPXandNGfracExtrema: The difference between the position of
#               the maximum of the histogram and the position of the 
#               minimum of the local NG fraction. For a better 
#               normalization this value is divided by the standard
#               deviation of the local NG fraction.
#           RatioWidthPXandNGfrac: The standard deviation of the KPIV's 
#           	histogram divided by the standard deviation of the local 
#               NG fraction.
#           ShiftPXandNGfracMean: The difference between the expectation 
#               value of the KPIV and the expectation value of the local NG
#               fraction. Again, for a better normalization this value is 
#               divided by the standard deviation of the local NG fraction.
#
#   Exceptions:
#      pdfN not 1d: If the array for the histogram probability density is  
#               not 1d an exception is thrown with the message: 
#                     "The array of the histogram probability density has to be 1d!"
#      pdfN empty: If there are no histogram data an exception is thrown 
#               with the message: 
#                     "The array of the histogram probability density must not be empty!"
#      ngFracBin not 1d: If the array for the local NG fraction is not 1d 
#               an exception is thrown with the message: 
#                     "The array of local NG fractions has to be 1d!"
#      length(ngFracBin)~=nBins: If the size of the local NG fraction does  
#               not fit to the size of the histogram bins an exception is 
#               thrown with the message: 
#                     "The array of local ng fractions must have the same  
#                      length as the array of the histogram probability density!"
#      ngFracBinError not 1d: If the array for the local NG fraction error  
#               is not 1d an exception is thrown with the message: 
#                     "The array of local NG fraction errors has to be 1d!"
#      length(ngFracBinError)~=nBins: If the size of the local NG fraction 
#               error does not fit to the size of the histogram bins an 
#               exception is thrown with the message: 
#                     "The array of local ng fractions errors must have the same  
#                      length as the array of the histogram probability density!"
#      binEdges not 1d: If the array for the bin edges is not 1d an  
#               exception is thrown with the message: 
#                     "The array of the bin edges has to be 1d!"
#      length(binEdges)~=nBins+1: If the size of the bin edges does not  
#               fit to the size of pdfN an exception is thrown with the 
#               message: 
#                     "The bin edges must have one element more than the 
#                      counts for the bins!"


    RankingCriteria = {
        "CentralNGfracStd": 0,
        "CentralDiffNGfracStd": 0,
        "RatioStdPXandNGfrac": 0,
        "WeightedAverageNGfrac": 0,
        "ShiftPXandNGfracExtrema": 0,
        "ShiftPXandNGfracMean": 0,
        "RatioWidthPXandNGfrac": 0
    }

    ############# check for correct data format and input parameter
    nBinsTrue=np.size(pdfN)
    if np.squeeze(pdfN).ndim>1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of the histogram probability density has to be 1d!"
        raise ValueError(errStr)
    if nBinsTrue<1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of the histogram probability density must not be empty!"
        raise ValueError(errStr)
    n1=np.size(ngFracBin)
    if np.squeeze(ngFracBin).ndim>1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of local NG fractions has to be 1d!"
        raise ValueError(errStr)
    if n1!=nBinsTrue:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of local ng fractions must have the same length as the array of the histogram probability density!"
        raise ValueError(errStr)
    n1=np.size(ngFracBinError)
    if np.squeeze(ngFracBinError).ndim>1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of local NG fraction errors has to be 1d!"
        raise ValueError(errStr)
    if n1!=nBinsTrue:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of local ng fraction errors must have the same length as the array of the histogram probability density!"
        raise ValueError(errStr)
    n1=np.size(binEdges)
    if np.squeeze(binEdges).ndim>1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The array of the bin edges has to be 1d!"
        raise ValueError(errStr)
    if n1!=nBinsTrue+1:
        errStr="Error in NGfractionRankingCriteriaContinuous: The bin edges must have one element more than the counts for the bins!"
        raise ValueError(errStr)

    ##################### choose default values for inappropriate function input
    if nSelected<2:
        nSelected=2
    if nSelected>nBinsTrue:
        nSelected=nBinsTrue

    ################## prepare arrays that will be used
    xCenter=0.5*(binEdges[0:nBinsTrue]+binEdges[1:nBinsTrue+1]); # center of bins
    xWidth=(binEdges[1:nBinsTrue+1]-binEdges[0:nBinsTrue]); # width of bins
    ngFracUpperBound=ngFracBin+ngFracBinError;
    ngFracMax=max(ngFracUpperBound);

    ############# standard deviation of the nSelected 5 central bins
    ############# divided by the global ng fraction
    idx = np.argsort(-pdfN)    # Get the indices of pdfN which would sort pdfN in descending order
    upperInd = nSelected    # select the nSelected bins with the largest counts
    if len(idx) < upperInd:
        upperInd = len(idx)
    posSelected = np.argwhere(np.squeeze(ngFracBinError[idx[0:upperInd]])/np.squeeze(ngFracBin[idx[0:upperInd]])<0.5)    # only select bins whose error is not too large
    if np.size(posSelected)<1:
        posSelected=np.array(range(upperInd))
    RankingCriteria["CentralNGfracStd"] = np.std(ngFracBin[idx[posSelected]], ddof=0) * np.sqrt(len(posSelected) / nSelected) / ngFracGlobal
                            # the factor np.sqrt(len(posSelected) / nSelected) scales the parameter with less than
                            # nSelected bins, so that they are not weighted stronger than the others

    ############# difference between maximum and minimum ng fraction for
    ############# the nSelected central bins divided by the global ng fraction
    RankingCriteria["CentralDiffNGfracStd"] = ((max(ngFracBin[idx[posSelected]]) - min(ngFracBin[idx[posSelected]])) / ngFracGlobal)

    ############# ration of the standard deviation of the KPIV and the
    ############# standard deviation of the local ng fraction
    stdHist = np.sqrt(np.sum(pdfN*xCenter**2*xWidth) / np.sum(pdfN*xWidth))
#    stdNGfrac = np.sqrt(np.sum((1-ngFracBin)*xCenter**2*xWidth) / np.sum((1-ngFracBin)*xWidth))
    stdNGfrac=np.sqrt(np.sum((ngFracMax-ngFracUpperBound)*xCenter**2*xWidth)/np.sum((ngFracMax-ngFracUpperBound)*xWidth));
                                # here we have to use 1-ngFracBins as probability distribution, because ngFracBin
                                # has not the properties of a probability distribution, especially it does
                                # not go to zero for x --> infinity
    RankingCriteria["RatioStdPXandNGfrac"] = stdHist / stdNGfrac

    ############# weighted average of the local ng fraction with the
    ############# reciprocal of the square of the bin count as weights
    ############# normalized by the global ng fraction
    posNonzero = np.argwhere(pdfN!=0)    # only select bins with a certain amount of bin counts
    avgNgFrac = np.sum(1 / (pdfN[posNonzero]*xWidth[posNonzero])**2 * ngFracBin[posNonzero]) / np.sum(1 / (pdfN[posNonzero]*xWidth[posNonzero])**2)   # new weight ^2
    #avgNgFrac = np.sum(pdfN**3*ngFracBin) / np.sum(pdfN**3)   # old weight ^3
    RankingCriteria["WeightedAverageNGfrac"] = avgNgFrac / ngFracGlobal

    ############# difference between the maximum of the histogram and the
    ############# minimum of the local ng fraction divided by the standard
    ############# deviation of the local ng fraction
    ExpecNGfrac=np.sum((ngFracMax-ngFracBin)*xCenter*xWidth)/np.sum((ngFracMax-ngFracBin)*xWidth); # evaluation for NG fraction
                    # here we have to use ngFracMax-ngFracBin as probability distribution, because ngFracBin 
                    # has not the properties of a probability distribution, especially it does 
                    # not go to zero for x->infinity
#    ExpecNGfrac = np.sum((1-ngFracBin) * xCenter*xWidth) / np.sum((1-ngFracBin)*xWidth)
                            # here we have to use 1-ngFracBin as probability distribution, because ngFracBin
                            # has not the properties of a probability distribution (see above)
    ExpecHist = np.sum(pdfN*xCenter*xWidth) / np.sum(pdfN*xWidth)
    RankingCriteria["ShiftPXandNGfracMean"] = abs(ExpecNGfrac - ExpecHist) / stdNGfrac
    
    ############# difference between the maximum of the histogram and the
    ############# minimum of the local ng fraction divided by the standard
    ############# deviation of the local ng fraction
    indMaxHistMultiple=Utility.FindLocalMinima(-pdfN);
    minimumNGfracError = min(ngFracBinError[indMaxHistMultiple])
    indMaxHistTmp=np.where(ngFracBinError[indMaxHistMultiple] == minimumNGfracError)[0][0]
    indMaxHist=indMaxHistMultiple[indMaxHistTmp]
 #   indMinNGMultiple=Utility.FindLocalMinima(ngFracBin);
    indMinNGMultiple=Utility.FindLocalMinima(ngFracUpperBound);
    minimumNGfracError = min(ngFracBinError[indMinNGMultiple])
    indMinNGTmp=np.where(ngFracBinError[indMinNGMultiple] == minimumNGfracError)[0][0]
    indMinNG=indMinNGMultiple[indMinNGTmp]
    posMaxHist = xCenter[indMaxHist]  # center of bin with maximum
    posMinNG =xCenter[indMinNG]  # center of bin with minimum
    stdCentralNGfrac=np.sqrt(np.sum((ngFracMax-ngFracUpperBound)*(xCenter-ExpecNGfrac)**2*xWidth)/np.sum((ngFracMax-ngFracUpperBound)*xWidth));
    RankingCriteria["ShiftPXandNGfracExtrema"] = abs(posMaxHist - posMinNG) / stdCentralNGfrac

    ################## ratio of the width of the KPIV distribution and the 
    ################## width of the local ng fraction
    if nBinsTrue>2:
        widthHist=Utility.DetermineWidthOfMaximum(xCenter,pdfN,indMaxHist,0.66)
        widthNG=Utility.DetermineWidthOfMaximum(xCenter,-ngFracUpperBound,indMinNG,0.66)
    else:
        widthHist=-1
        widthNG=-1
    if widthHist>0.0 and widthNG>0.0:
        RankingCriteria["RatioWidthPXandNGfrac"]=widthHist/widthNG
    else:
        RankingCriteria["RatioWidthPXandNGfrac"]=0.0

    return RankingCriteria
##############################################################################
################## end NGfractionRankingCriteriaContinuous ###################
##############################################################################


##############################################################################
#################### NGfractionRankingCriteriaCategorical ####################
##############################################################################
def NGfractionRankingCriteriaCategorical(pdfN,ngFracBin,ngFracBinError,ngFracGlobal):
#NGfractionRankingCriteriaCategorical:   Calculate several KPIV ranking 
#criteria based on the local ng fraction (only for categorical KPIVs).
#
#   Attention: This only works for categorical KPIVs!!!!!!!!!!!!!!!!
#              If you apply the algorithm to continuous KPIVs, the results
#              will not be reliable. Continuous KPIVs have to be treated 
#              separately.
#
#   From the properties of the histogram and the properties of the 
#   corresponding local NG fraction several criteria are derived, which can 
#   distinguish good from bad performance of the production. They are based 
#   on the variation of the NG fraction. In order to be consistent with 
#   continuous KPIVs, they are collected in the same Matlab structure. 
#   However, only the first two criteria (slightly modified) are used for
#   categorical KPIVs.
#
#   function input:
#      pdfN: The number of parts (counts) for each bin of the histogram. 
#            This is different to the continuous case, where the 
#            probability density is used, because there bins can have
#            different widths. It has dimension (nBins,1) or (1,nBins), 
#            where nBins is the number of bins.
#      ngFracBin: The local ng fraction for each bin. It is defined as the 
#                 number of ng parts in the bin divided by the number of 
#                 all parts in the bin. The array must have dimension 
#                 (nBins,1) or (1,nBins).
#      ngFracBinError: The error of the local ng fraction for each bin. It 
#                      is derived from the assumption that NG parts and 
#                      good parts in each bin are distributed according to 
#                      a binomial distribution. The array must have 
#                      dimension (nBins,1) or (1,nBins).
#      ngFracGlobal: The global NG fraction, i. e. the number of all NG
#                    parts divided by the number of all parts.
#
#   function output:
#       RankingCriteria: A Matlab structure that collects different ranking
#           criteria. The following quantities are contained:
#           CentralNGfracStd: The standard deviation of the local NG 
#               fraction derived from the nSelected central bins of the 
#               histogram divided by the global NG fraction. For
#               categorical KPIVs all bins are selected.
#           CentralDiffNGfracStd: The difference between the maximum and 
#               the minimum local NG fraction for the nSelected central 
#               bins divided by the global NG fraction. For categorical 
#               KPIVs all bins are selected.
#           RatioStdPXandNGfrac: The standard deviation of the KPIV's 
#           	histogram divided by the standard deviation of the local 
#               NG fraction.
#           WeightedAverageNGfrac: The weighted average of the local NG 
#               fraction with the reciprocal of the square of the bin count
#               as weights. This average is normalized by the global NG 
#               fraction.
#           ShiftPXandNGfracExtrema: The difference between the position of
#               the maximum of the histogram and the position of the 
#               minimum of the local NG fraction. For a better 
#               normalization this value is divided by the standard
#               deviation of the local NG fraction.
#           RatioWidthPXandNGfrac: The standard deviation of the KPIV's 
#           	histogram divided by the standard deviation of the local 
#               NG fraction.
#           ShiftPXandNGfracMean: The difference between the expectation 
#               value of the KPIV and the expectation value of the local NG
#               fraction. Again, for a better normalization this value is 
#               divided by the standard deviation of the local NG fraction.
#
#   Exceptions:
#      pdfN not 1d: If the array for the histogram probability density is  
#               not 1d an exception is thrown with the message: 
#                     "The array of the histogram probability density has to be 1d!"
#      pdfN empty: If there are no histogram data an exception is thrown 
#               with the message: 
#                     "The array of the histogram probability density must not be empty!"
#      ngFracBin not 1d: If the array for the local NG fraction is not 1d 
#               an exception is thrown with the message: 
#                     "The array of local NG fractions has to be 1d!"
#      length(ngFracBin)~=nBins: If the size of the local NG fraction does  
#               not fit to the size of the histogram bins an exception is 
#               thrown with the message: 
#                     "The array of local ng fractions must have the same  
#                      length as the array of the histogram probability density!"
#      ngFracBinError not 1d: If the array for the local NG fraction error  
#               is not 1d an exception is thrown with the message: 
#                     "The array of local NG fraction errors has to be 1d!"
#      length(ngFracBinError)~=nBins: If the size of the local NG fraction 
#               error does not fit to the size of the histogram bins an 
#               exception is thrown with the message: 
#                     "The array of local ng fractions errors must have the same  
#                      length as the array of the histogram probability density!"

    RankingCriteria = {
        "CentralNGfracStd": 0,
        "CentralDiffNGfracStd": 0,
        "RatioStdPXandNGfrac": 0,
        "WeightedAverageNGfrac": 0,
        "ShiftPXandNGfracExtrema": 0,
        "ShiftPXandNGfracMean": 0,
        "RatioWidthPXandNGfrac": 0
    }

    ############# check for correct data format and input parameter
    nBins=np.size(pdfN)
    if np.squeeze(pdfN).ndim>1:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of the histogram probability density has to be 1d!"
        raise ValueError(errStr)
    if nBins<1:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of the histogram probability density must not be empty!"
        raise ValueError(errStr)
    n1=np.size(ngFracBin)
    if np.squeeze(ngFracBin).ndim>1:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of local NG fractions has to be 1d!"
        raise ValueError(errStr)
    if n1!=nBins:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of local NG fractions must have the same length as the array of the histogram probability density!"
        raise ValueError(errStr)
    n1=np.size(ngFracBinError)
    if np.squeeze(ngFracBinError).ndim>1:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of local NG fraction errors has to be 1d!"
        raise ValueError(errStr)
    if n1!=nBins:
        errStr="Error in NGfractionRankingCriteriaCategorical: The array of local NG fraction errors must have the same length as the array of the histogram probability density!"
        raise ValueError(errStr)

    ################## only select bins whose error is not too large
    posSelected=np.argwhere(ngFracBinError/ngFracBin<0.5)[:,0]; 
    if np.size(posSelected)<1:
        posSelected=np.array(range(0,nBins));
    
    ################## standard deviation of the selected bins divided by the 
    ################## global NG fraction
    RankingCriteria["CentralNGfracStd"] = np.std(ngFracBin[posSelected], ddof=0) * np.sqrt(len(posSelected) / nBins) / ngFracGlobal
     
    ################## difference between maximum and minimum NG fraction for 
    ################## the selected bins divided by the global NG fraction
    RankingCriteria["CentralDiffNGfracStd"] = ((max(ngFracBin[posSelected]) - min(ngFracBin[posSelected])) / ngFracGlobal)
    
    ################## the remaining criteria are initialized with default
    ################## values (negative value to indicate that it should not be
    ################## used)
    RankingCriteria["RatioStdPXandNGfrac"]=-1.0;
    RankingCriteria["WeightedAverageNGfrac"]=-1.0;
    RankingCriteria["ShiftPXandNGfracExtrema"]=-1.0;
    RankingCriteria["RatioWidthPXandNGfrac"]=-1.0;
    RankingCriteria["ShiftPXandNGfracMean"]=-1.0;
    
    return RankingCriteria
##############################################################################
################## end NGfractionRankingCriteriaCategorical ##################
##############################################################################


##############################################################################
################## NGfractionRankingCriteriaArrayToStructure #################
##############################################################################
def NGfractionRankingCriteriaArrayToStructure(CriteriaArray):
#NGfractionRankingCriteriaArrayToStructure:   Copy numerical 2d array of
#ranking criteria to structure (only for continuous KPIVs).
#
#   The ranking criteria that have been defined for continuous KPIVs are
#   stored in a Matlab structure. If we do this for every KPIV, we get a 1d
#   array of this structure. Sometimes it is convenient to use instead a
#   normal numerical 2d array, which afterwards has to be converted back
#   to the ranking criteria structure.
#
#   function input:
#       CriteriaArray: The ranking criteria for each KPIV as a 2d numerical
#                      array. It has dimension (nPar,7).
#
#   function output:
#      CriteriaStructure: 1d array of the ranking criteria structure. It
#                         has dimension (nPar,1).
#
#   Exceptions:
#      CriteriaArray empty: If there are no ranking criteria data an
#               exception is thrown with the message:
#                     "The input array must not be empty!"
#      CriteriaArray has wrong format: If the second dimension of the
#               array has not the size of the existing ranking criteria, an
#               exception is thrown with the message:
#                     "The input array has the wrong format!"

    #################### check for correct data format and input parameter
    shapeCriteriaArray = np.shape(CriteriaArray)
    nPar = shapeCriteriaArray[0]
    if len(shapeCriteriaArray)>1:        # If CriteriaArray is a column vector shapeCriteriaArray[1] doesn't exist
        nCriteria = shapeCriteriaArray[1]
    else:
        nCriteria = 1
    if nPar<1:
        errStr='NGfractionRankingCriteriaArrayToStructure:invalidInput: The input array must not be empty!'
        raise ValueError(errStr)
    if nCriteria!=7:
        errStr='NGfractionRankingCriteriaArrayToStructure:invalidInput: The input array has the wrong format!'
        raise ValueError(errStr)

    #################### copy numerical array to structure array
    CriteriaStructureArray = np.array([])
    for i in range(nPar):
        CriteriaStructureArray = np.append(CriteriaStructureArray, [np.array([{}])])     # Create array that don't override every entry

    for n in range(nPar):
        CriteriaStructureArray[n]["CentralNGfracStd"] = CriteriaArray[n, 0]
        CriteriaStructureArray[n]["CentralDiffNGfracStd"] = CriteriaArray[n, 1]
        CriteriaStructureArray[n]["RatioStdPXandNGfrac"] = CriteriaArray[n, 2]
        CriteriaStructureArray[n]["WeightedAverageNGfrac"] = CriteriaArray[n, 3]
        CriteriaStructureArray[n]["ShiftPXandNGfracExtrema"] = CriteriaArray[n, 4]
        CriteriaStructureArray[n]["ShiftPXandNGfracMean"] = CriteriaArray[n, 5]
        CriteriaStructureArray[n]["RatioWidthPXandNGfrac"] = CriteriaArray[n, 6]
    return CriteriaStructureArray
##############################################################################
################ end NGfractionRankingCriteriaArrayToStructure ###############
##############################################################################


##############################################################################
################## NGfractionRankingCriteriaStructureToArray #################
##############################################################################
def NGfractionRankingCriteriaStructureToArray(CriteriaStructure, weightingFactor=None):
#NGfractionRankingCriteriaStructureToArray:   Copy structure of ranking
#criteria to numerical 2d array (only for continuous KPIVs).
#
#   The ranking criteria that have been defined for continuous KPIVs are
#   stored in a Matlab structure. If we do this for every KPIV, we get a 1d
#   array of this structure. Sometimes it is convenient to convert this to
#   a normal numerical 2d array. During this procedure the ranking criteria
#   for each KPIV might optionally be multiplied with a weighting factor.
#
#   function input:
#      CriteriaStructure: 1d array of the ranking criteria structure. It
#                         has dimension (nPar,1) or (1,nPar).
#      There are additional optional input arguments collected in varargin.
#      weightingfactor=varargin{1}: A weightingfactor for each KPIV that is
#                      multiplied with its ranking criteria. The dimension
#                      has to be (1,nPar) or (nPar,1).
#
#   function output:
#       CriteriaArray: The ranking criteria for each KPIV as a 2d numerical
#                      array. It has dimension (nPar,7).
#
#   Exceptions:
#      CriteriaStructure empty: If there are no ranking criteria data an
#               exception is thrown with the message:
#                     "The array of the structure for the ranking criteria must not be empty!"
#      CriteriaStructure has wrong format: If some of the required fields
#               in the structure of the ranking criteria is missing, an
#               exception is thrown with the message:
#                     "The structure array has the wrong format!"

    #################### check for correct data format and input parameter
    nPar = CriteriaStructure.size
    if nPar<1:
        errStr = 'NGfractionRankingCriteriaStructureToArray:invalidInput: The array of the structure for the ranking criteria must not be empty!'
        raise ValueError(errStr)
    bFirst = "CentralNGfracStd" in CriteriaStructure[0] and "CentralDiffNGfracStd" in CriteriaStructure[0] and "RatioStdPXandNGfrac" in CriteriaStructure[0] and "WeightedAverageNGfrac" in CriteriaStructure[0]    # check if the first 4 required fields exist
    bSecond = "ShiftPXandNGfracExtrema" in CriteriaStructure[0] and "ShiftPXandNGfracMean" in CriteriaStructure[0] and "RatioWidthPXandNGfrac" in CriteriaStructure[0]  # check if the remaining required fields exist
    if not(bFirst and bSecond):
        errStr = 'NGfractionRankingCriteriaStructureToArray:invalidInput: The structure array has the wrong format!'
        raise ValueError(errStr)

    #################### check for optional function input
    if weightingFactor is not None:
        temp = weightingFactor
        if temp.size != nPar:
            weightingFactor = np.ones((nPar, 1), int)   # default is 1
    else:
        weightingFactor = np.ones((nPar, 1), int)   # default is 1

    #################### copy structure array to normal numerical array
    CriteriaArray = np.zeros((nPar, 7), float)
    for n in range(nPar):
        CriteriaArray[n, 0] = CriteriaStructure[n]["CentralNGfracStd"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 1] = CriteriaStructure[n]["CentralDiffNGfracStd"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 2] = CriteriaStructure[n]["RatioStdPXandNGfrac"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 3] = CriteriaStructure[n]["WeightedAverageNGfrac"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 4] = CriteriaStructure[n]["ShiftPXandNGfracExtrema"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 5] = CriteriaStructure[n]["ShiftPXandNGfracMean"]*weightingFactor[n]
    for n in range(nPar):
        CriteriaArray[n, 6] = CriteriaStructure[n]["RatioWidthPXandNGfrac"]*weightingFactor[n]
    return CriteriaArray
##############################################################################
################ end NGfractionRankingCriteriaStructureToArray ###############
##############################################################################
