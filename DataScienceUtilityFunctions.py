import numpy as np

##############################################################################
############################## FindLocalMinima ###############################
##############################################################################
def  FindLocalMinima(DataIn):
#FindLocalMinima:   Determine all local minima of a given data array. 
#
#   Find all local minima of an array of discrete data. Local minima are
#   postions, hwere the two adjacent values have higher values. The first
#   and the last point have to be treated separately, because it can not be
#   judged, if they are local minima. Instead we count one of them as a 
#   local minimum, if it is a global minimum. Thus, at least one value is
#   returned, because without a local minimum inside the values have to be
#   either monotonically decreasing or increasing, so that a global minimum
#   has to occur at the boundaries.
#
#   function input:
#      DataIn: Data array whose minima should bet determined. It has to be 
#              1d, i. e. it has dimension (nData,1) or 
#              (1,nData).
#
#  function output:
#      minPos: 1d array with the indices of the local minima.
#
#   Exceptions:
#      DataIn not 1d: If the data array is not 1d an exception is thrown 
#               with the message: 
#                     "The array of the data has to be 1d!"
#      DataIn empty: If there are no data an exception is thrown with the 
#               message: 
#                     "The array of the data must not be empty!"

    ##################### check for correct data format
    if np.squeeze(DataIn).ndim>1:
        errStr="Error in FindLocalMinima: The array of the data has to be 1d!"
        raise ValueError(errStr)
    nData=np.size(DataIn)
    if nData<1:
        errStr="Error in FindLocalMinima: The array of the data must not be empty!"
        raise ValueError(errStr)
    
    #################### initialize variable
    minPos = []
    counter = 0

    #################### check interior points for local minima
    for n in range(1, nData-1):
        if DataIn[n-1]>=DataIn[n] and DataIn[n+1]>=DataIn[n]:   # condition for local minimum
            if len(minPos) == 0:
                minPos.append(None)
                minPos[counter] = n
                counter += 1
            else:
                if minPos[counter-1] != (n-1):  # point immediately before is already minimum
                                                # --> this point can't be additional minimum
                    minPos.append(None)
                    minPos[counter] = n
                    counter += 1

    #################### first and last point are counted as local minima, if
    #################### they are global minima
    minimum = min(DataIn)
    globalMinInd = np.where(DataIn == minimum)[0][0]
    if globalMinInd==0 or globalMinInd==(nData-1):
        minPos.append(None)
        minPos[counter] = globalMinInd
    return minPos
##############################################################################
############################ end FindLocalMinima #############################
##############################################################################


##############################################################################
########################## DetermineWidthOfMaximum ###########################
##############################################################################
def  DetermineWidthOfMaximum(x,y,maxPos,WidthNiveau=0.5, minVal=None):
#FindLocalMinima:   Determine the width of a local maximum of a a given 
#data array.
#
#   Find The width of a given local maximum. The width will be determined
#   at the function value fw=fmin+niveau*(fmax-fmin), i. e. at a certain
#   fraction between minimum and maximum value. The minimum value will
#   either be detrmined automatically or specified by the user. If on one
#   side of the maximum no intersection point can be detected, two times
#   the width of the other side will be taken as total width, If no
#   intersection points can be detected, it is impossible to quantify the
#   width, which is signaled by a negative return value.
#
#   function input:
#      x: Data array with x-values of the curve. It has to be 1d, i. e. it 
#         has dimension (nData,1) or (1,nData).
#      y: Data array with y-values of the curve. It has to be 1d, i. e. it 
#         has dimension (nData,1) or (1,nData).
#      maxPos: The index of the position, where the maximum occurs. It will
#              not be checked, if this is truly a local maximum.
#      There are additional optional input arguments collected in varargin.
#      WidthNiveau=varargin{1}: This function argument specifies the
#                  fraction of the function span (maximum - minimum), where 
#                  the width will be determined. Its default value is 0.5.
#      minVal=varargin{2}: This parameter specifies the minimum of the
#                  function span. It allows to use the same minimum for 
#                  different curves, which is sometimes convenient. By
#                  default the global minimum of y is taken.
#
#  function output:
#      widthOut: The width of the local maximum at the specified 
#                WidthNiveau.
#
#   Exceptions:
#      x not 1d: If the data array for x is not 1d an exception is thrown 
#               with the message: 
#                     "The array of the x-values has to be 1d!"
#      nData<3: If there are less than 3 x-values an exception is thrown 
#               with the message: 
#                     "The array of the x-Values must have at least 2 elements!"
#      y not 1d: If the data array for y is not 1d an exception is thrown 
#               with the message: 
#                     "The array of the y-values has to be 1d!"
#      ny~=nx: If the size of the x-values does not fit to the size of the 
#               y-values an exception is thrown with the
#               message: 
#                     "The array of y-values must have the same length as 
#                      the array of the x-values!"
#      maxPos<1 || maxPos>nData: If the index of the maximum is not within  
#               the bounds of the array for the y-values, an exception is 
#               thrown with the message: 
#                     "The index of the maximum is not within the bounds of 
#                      the array for the y-values!"

    ##################### check for correct data format
    if np.squeeze(x).ndim>1:
        errStr="Error in DetermineWidthOfMaximum: The array of the x-values has to be 1d!"
        raise ValueError(errStr)
    nData=np.size(x)
    if nData<3:
        errStr="Error in DetermineWidthOfMaximum: The array of the x-Values must have at least 2 elements!"
        raise ValueError(errStr)
    if np.squeeze(y).ndim>1:
        errStr="Error in DetermineWidthOfMaximum: The array of the y-values has to be 1d!"
        raise ValueError(errStr)
    n2=np.size(y)
    if nData!=n2:
        errStr="Error in DetermineWidthOfMaximum: The array of y-values must have the same length as the array of the x-values!"
        raise ValueError(errStr)
    if maxPos<0 or maxPos>nData-1:
        errStr="Error in DetermineWidthOfMaximum: The index of the maximum is not within the bounds of the array for the y-values!"
        raise ValueError(errStr)
    
    ##################### check for function arguments and prepare some
    ##################### variables
    if WidthNiveau<0 or WidthNiveau>1:
        WidthNiveau=0.5
    maxVal=y[maxPos]
    if minVal is not None:
        if minVal>=maxVal:
            minVal = min(y)
    else:
        minVal = min(y)

    funHeight=maxVal-minVal # span of the function values
    funIntersectionVal=minVal+WidthNiveau*funHeight # function value for the desired width
    
    ##### search left sided width
    indLower = maxPos
    while indLower>-1 and y[indLower]>funIntersectionVal:
        indLower -= 1
    if indLower>-1:  # intersection with function has been found on left side
        leftVal = x[indLower] + (funIntersectionVal-y[indLower]) * (x[indLower+1]-x[indLower])/(y[indLower+1]-y[indLower])
                        # linear interpolation
        bLeft = 1.0
    else:
        bLeft = -1.0

    ##### search right sided width
    indUpper = maxPos
    while indUpper<nData and y[indUpper]>funIntersectionVal:
        indUpper += 1
    if indUpper<nData:    # intersection with function has been found on right side
        rightVal = x[indUpper-1]+(funIntersectionVal-y[indUpper-1]) * (x[indUpper]-x[indUpper-1])/(y[indUpper]-y[indUpper-1])
                        # linear interpolation
        bRight = 1.0
    else:
        bRight = -1.0

    ##### determine width from left- and right-sided values
    if bLeft>0:
        if bRight>0:
            widthOut = rightVal-leftVal
        else:
            widthOut = 2*abs(leftVal)   # assume symmetry
    else:
        if bRight>0:
            widthOut = 2*abs(rightVal)  # assume symmetry
        else:
            widthOut = -1   # negative value signals failure

    return widthOut
##############################################################################
######################## end DetermineWidthOfMaximum #########################
##############################################################################


##############################################################################
####################### FitTwoConnectedLinearCurves ##########################
##############################################################################
def FitTwoConnectedLinearCurves(x,y):
#FitTwoConnectedLinearCurves: Fit two connected curves of different slope
#to find the optimum connection point.
#
#   A curve that consists of two linear functions with different slope, 
#   which are connected at an unknown point, is fitted by linear
#   regression. This is achieved by fitting two connected linear functions
#   with a given connection point, where all input points (x_n,y_n) are
#   successively used as connection points. The one with the smallest mean
#   square error is the searched connection point.
#
#   function input:
#      x: The x-values of the curve that should be fitted. It has dimension
#         (nSamples,1) or (1,nSamples).
#      y: The y-values of the curve that should be fitted. It has dimension
#         (nSamples,1) or (1,nSamples).
#
#   function output:
#      yFit: y-values of the fitted curve at x. It has dimension 
#            (nSamples,1) or (1,nSamples). 
#      meanSquaredError: The mean squared error of the fitted curve at x,
#            i. e. sum((y_n-y(x_n)^2).
#      IndexConnected: The index of the input data (x,y) that gives the
#            lowest mean squared error, when used as connection point.
#      RegressionCoefficients: The coeffcients that describe the fitted
#            curve. It has dimension (3,1) with:
#                  RegressionCoefficients(1)=a_1 
#                  RegressionCoefficients(2)=b_1 
#                  RegressionCoefficients(3)=b_2 
#
#   Exceptions:
#      x not 1d: If the array for the x-values is not 1d, an exception is 
#               thrown with the message: 
#                     "The array of the x-values must be a 1d array!"
#      x empty: If there are no x-values, an exception is thrown with the 
#               message: 
#                     "The array of the x-values must not be empty!"
#      length(y)~=nSamples: If the size of the y-values does not fit to the 
#               size of x-values, an exception is thrown with the message: 
#                     "The array of y-values must have the same length as 
#                      the array of x-values!"
#      y not 1d: If the array for the y-values is not 1d, an exception is 
#               thrown with the message: 
#                     "The array of the y-values must be a 1d array!"

    ##################### check for correct data format and input parameter
    shapeData=np.shape(x)
    nSamples=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if nSamples==1 and n2>1: # x is a row vector
        nSamples=n2;
        n2=1;
    if nSamples<1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the x-values must not be empty!"
        raise ValueError(errStr)
    if nSamples>1 and n2>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the x-values must be a 1d array!"
        raise ValueError(errStr)
    xTmp=np.reshape(x,(nSamples,1));
    shapeData=np.shape(y)
    n1=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if n1==1 and n2>1: # y is a row vector
        n1=n2;
        n2=1;
    if n1!=nSamples:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of y-values must have the same length as the array of x-values!"
        raise ValueError(errStr)
    if n1>1 and n2>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the y-values must be a 1d array!"
        raise ValueError(errStr)
    yTmp=np.reshape(y,(nSamples,1));
   
    ##################### fit succesively two connected linear functions for
    ##################### different connection points
    mse=np.zeros((nSamples-2,1))
    for n in range(1,nSamples-1): # first and last points are excluded, because at least 
                       # two points are necessary for a linear fit
        _,mse[n-1,0],_=LinearRegressionTwoConnectedLines(xTmp,yTmp,xTmp[n,0],xTmp);
    
    ##################### minimum of mean squared error gives the optimum
    ##################### connection point
    IndexConnected=np.argmin(mse);
    IndexConnected=IndexConnected+1; # in mse index 1 denotes the second point,
                                     # because the first point has been omitted.
                                     # This has to be corrected.
    
    ##################### repeat fit for the optimum connection point, in order
    ##################### to determine the coefficients of the linear functions
    yFit,meanSquaredError,RegressionCoefficients=LinearRegressionTwoConnectedLines(xTmp,yTmp,xTmp[IndexConnected,0],xTmp);
    
    return yFit,meanSquaredError,IndexConnected,RegressionCoefficients
##############################################################################
##################### end FitTwoConnectedLinearCurves ########################
##############################################################################


##############################################################################
#################### LinearRegressionTwoConnectedLines #######################
##############################################################################
def LinearRegressionTwoConnectedLines(x,y,xConnected,xEval):
#LinearRegressionTwoConnectedLines: Linear regression with two connected 
#curves of different slope.
#
#   Sometimes it is convenient to fit a curve that consists of two linear 
#   functions that are connected at known position $x_c$. In other words it 
#   might be described by
#   y(x)=a_1+b_1*x for x<= x_c
#        a_2+b_2*x for x>x_c.
#   Continuity at x=x_c leads to the requirement
#   a_1+b_1*x_c=a_2+b_2*x_c,
#   which allows to eliminate a_2
#   a_2=a_1+(b_1-b_2)*x_c.
#   Thus, the equation for the desired curve becomes
#   y(x)=a_1+b_1*x for x<= x_c
#        a_1+(b_1-b_2)*x_c+b_2*x for x>x_c.
#   Given data (x_n,y_n) the unknown coefficients can be determined by a 
#   singular value decomposition of the design matrix
#   A=(1,x_n,0
#       ...
#      1,x_m,0
#      1,x_c,x_{m+1}-x_c
#       ...
#      1,x_c,x_N-x_c)
#   where x_m<=x_c<x_{m+1}. From the singular value decomposition
#   A=U*S*V^T
#   the unknown coefficients can be computed by the formula
#   (a_1,b_1,b_2)=V*(S^{-1}*(U^T*y)),
#   where y=(y_1,...,y_N)^T is the vector of y-values.
#
#   function input:
#      x: The x-values of the curve that should be fitted. It has dimension
#         (nSamples,1) or (1,nSamples).
#      y: The y-values of the curve that should be fitted. It has dimension
#         (nSamples,1) or (1,nSamples).
#      xConnected: The x-coordinate, where the two linear curves are
#                  connected. It has to be a scalar.
#      xEval: The x-values, where the fitted curve should be evaluated. 
#             It has dimension (nEval,1) or (1,nEval).
#
#   function output:
#      yFit: y-values of the fitted curve at xEval. It has dimension 
#            (nEval,1) or (1,nEval). 
#      meanSquaredError: The mean squared error of the fitted curve at x,
#            i. e. sum((y_n-y(x_n)^2).
#      RegressionCoefficients: The coeffcients that describe the fitted
#            curve. It has dimension (3,1) with:
#                  RegressionCoefficients(1)=a_1 
#                  RegressionCoefficients(2)=b_1 
#                  RegressionCoefficients(3)=b_2 
#
#   Exceptions:
#      x not 1d: If the array for the x-values is not 1d, an exception is 
#               thrown with the message: 
#                     "The array of the x-values must be a 1d array!"
#      x empty: If there are no x-values, an exception is thrown with the 
#               message: 
#                     "The array of the x-values must not be empty!"
#      length(y)~=nSamples: If the size of the y-values does not fit to the 
#               size of x-values, an exception is thrown with the message: 
#                     "The array of y-values must have the same length as 
#                      the array of x-values!"
#      y not 1d: If the array for the y-values is not 1d, an exception is 
#               thrown with the message: 
#                     "The array of the y-values must be a 1d array!"
#      xConnected not a scalar: If xConnected is not a scalar, an exception 
#               is thrown with the message: 
#                     "The connection point xc must be a scalar value!"
#      xEval not 1d: If the array for the x-values of the evaluation points 
#               is not 1d, an exception is thrown with the message: 
#                     "The array of the x-values for evaluation points 
#                      must be a 1d array!"

    ##################### check for correct data format and input parameter
    shapeData=np.shape(x)
    nSamples=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if nSamples==1 and n2>1: # x is a row vector
        nSamples=n2;
        n2=1;
    if nSamples<1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the x-values must not be empty!"
        raise ValueError(errStr)
    if nSamples>1 and n2>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the x-values must be a 1d array!"
        raise ValueError(errStr)
    xTmp=np.reshape(x,(nSamples,1));
    shapeData=np.shape(y)
    n1=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if n1==1 and n2>1: # y is a row vector
        n1=n2;
        n2=1;
    if n1!=nSamples:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of y-values must have the same length as the array of x-values!"
        raise ValueError(errStr)
    if n1>1 and n2>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the y-values must be a 1d array!"
        raise ValueError(errStr)
    yTmp=np.reshape(y,(nSamples,1));
    if np.size(xConnected)>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The connection point xc must be a scalar value!"
        raise ValueError(errStr)
    shapeData=np.shape(xEval)
    nEval=shapeData[0]
    try: n2 = shapeData[1]
    except: n2 = 1
    if nEval==1 and n2>1: # nEval is a row vector
        nEval=n2;
        n2=1;
    if nEval>1 and n2>1:
        errStr="Error in LinearRegressionTwoConnectedLines: The array of the x-values for evaluation points must be a 1d array!"
        raise ValueError(errStr)
    xEvalTmp=np.reshape(xEval,(nEval,1));
   
    ##################### fit curves by singular value decomposition
    dropTol=1.0e-12; # relative tolerance for neglecting very small singular values
    indConnected=SearchIndexFromField(xConnected,x,1); # search index for the connection point
    MatDesign=np.zeros([nSamples,3]); # generate design matrix (details see description above)
    MatDesign[:,0]=1.0;
    MatDesign[0:indConnected+1,1]=xTmp[0:indConnected+1,0];
    MatDesign[indConnected+1:nSamples,1]=xConnected;
    MatDesign[indConnected+1:nSamples,2]=xTmp[indConnected+1:nSamples,0]-xConnected;
    U,S,V=np.linalg.svd(MatDesign); # singular value decomposition
    sMax=S[1]; # largest singular bvalue
    Sinv=np.zeros([3,nSamples]); # create diagonal matrix of reciprocal singular values
    for l in range(0,3):
        if S[l]>dropTol*sMax: # neglect singular values that are too small
            Sinv[l,l]=1/S[l]; # reciprocal of singular values on diagonal
    RegressionCoefficients=V.transpose() @ (Sinv @ (U.transpose() @ yTmp)); # use singular value decomposition 
                                      # to solve equation for the coefficients
    
    ##################### determine mean squared error
    meanSquaredError=np.sum((MatDesign @ RegressionCoefficients-yTmp)**2)/nSamples;
    
    ##################### compute fitted curve at the evaluation points
    if np.size(xEval)<1: # do this only if xEval is not empty
        yFit=[];
    else:
        yFit=np.zeros([nEval,1]);
        posFirst=np.nonzero(xEvalTmp<=xConnected);
        yFit[posFirst[0],0]=RegressionCoefficients[0]+RegressionCoefficients[1]*xEvalTmp[posFirst[0],0];
        posSecond=np.nonzero(xEvalTmp>xConnected);
        yFit[posSecond[0],0]=RegressionCoefficients[0]+(RegressionCoefficients[1]-RegressionCoefficients[2])*xConnected+RegressionCoefficients[2]*xEvalTmp[posSecond[0],0];
        
    return yFit,meanSquaredError,RegressionCoefficients
##############################################################################
################### end LinearRegressionTwoConnectedLines ####################
##############################################################################


##############################################################################
########################## SearchIndexFromField ##############################
##############################################################################
def SearchIndexFromField(value,field,sign):
# Search the index for the largest fieldvalue lower than or equal to value
# value: value to compare; field: field to search; sign: ordering of field
    number=np.size(field);
    if sign>=0:
        if value<field[0]:
            erg=-1;
            return -1;
        if value>field[number-1]:
            erg=number-1;
            return erg;
        erg=np.max(np.nonzero(field<=value));
        return erg;
    if sign<0:
        if value>field[0]:
            erg=-1;
            return erg;
        if value<field[number-1]:
            erg=number-1;
            return erg;
        erg=np.max(np.nonzero(field>value))+1;
        return erg;
##############################################################################
######################## end SearchIndexFromField ############################
##############################################################################


