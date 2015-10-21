#CircularRegressionHelper.py

#----------------------------------------------------------
import sys, math
#constants
degToRad = math.pi/180.0
radToDeg = 180.0/math.pi
#----------------------------------------------------------
def circleMake(aPnt,aRadius,gp):
  #create a circle from a point [X,Y] and radius
  #returns a list of points representing the circle as an Ngon
  X0,Y0=aPnt[0],aPnt[1]
  X1,Y1=X0+aRadius,Y0
  circPnts=[[X1,Y1]]
  for i in range(1,360):
    X=X0+math.cos(degToRad*i)*aRadius
    Y=Y1+math.sin(degToRad*i)*aRadius
    circPnt=[X,Y]
    circPnts.append(circPnt)
  del circPnt
  return circPnts
#---------------------------------------------------------------
def GaussianElim(A):
  SigLevel = 1.0E-15
  N = len(A); M = len(A[0])
  xList = []; OutList = []
  for row in range(0,N):     #ensure floating point numbers
    for col in range(0,M):
      A[row][col]=float(A[row][col])
  for row in range(0,N):
    Factor=A[row][row]
    if (abs(Factor) < SigLevel) :
      for i in range(row+1,N):
        if(abs(A[i][row]) > SigLevel) :
          for j in range(0,M):
            tmp = A[row][j]
            aVal = A[i][j]
            A[row][j] = aVal
            A[i][j] = tmp
          Factor = A[row][row]
      if abs(Factor) < SigLevel:#There is no solution
        print "Gaussian Elimination def...No solution"
        sys.exit()
    for i in range(0,M):
      aVal=A[row][i]
      A[row][i] = aVal/Factor
    for i in range(0, N):
      if(i != row) :
        Factor = A[i][row]
        for j in range(0, M):
          aVal = A[i][j]
          bVal = A[row][j]
          A[i][j] = (aVal - (Factor*bVal))
  for i in range(0, N):
    OutList.append(A[i][M-1])
  return OutList
#----------------------------------------------------------
def pntXY(pnt):
  #Gets X,Y coordinates given a point object 
  #  Returns a list
  XY= [pnt.X, pnt.Y]
  return XY
#-------------------------------------------------------------
def pntXYString(pnt):
  #Gets X,Y coordinates given a point object
  #  Returns a string
  XY= str(pnt.X) + ", " + str(pnt.Y)
  return XY
#-------------------------------------------------------------
def polyFromPoints (outFC, outType, SR, outPntsList, theFields, gp):
  #Requires
  #  outFC        output feature class name "c:/temp/myfile.shp"
  #  outType      output type "Polygon" or "Polyline"
  #  SR           Spatial reference from input feature class
  #  outPntsList  a list of lists of points
  #                eg [ [10,10], [12,15], [7,3] ]
  #  theFields    the fields to add and their format
  #  gp           the Geoprocessor Object
  #Create the output filename and feature class, use the Spatial Reference
  #  of the input feature class
  import os, sys    #required if used in other modules
  fullName = os.path.split(outFC)
  outFolder = fullName[0].replace("\\","/")
  outFName =  fullName[1].replace(" ", "_")
  outFullName = outFolder + "/" + outFName
  #Create a polygon shapefile
  try:
    gp.CreateFeatureclass_management(outFolder, outFName, outType, "#", "Disabled", "Disabled", SR)
    gp.AddMessage("\n" + "Creating " + str(outFullName) + "\n\t" + str(SR) + "\n")
  except:
    gp.AddMessage("Failed to create feature class" + "\n" + gp.GetMessages())
    sys.exit()
  #
  #Add any required fields fields
  #
  if len(theFields) != 0:
    for i in range(0, len(theFields)):
      aField = theFields[i]
      try:
        gp.AddField_management(outFullName, aField[0], aField[1], aField[2], aField[3])
      except:
        gp.AddMessage("cannot add field " + str(aField[0]) + "\n" + gp.GetMessages())
  try:
    cur = gp.InsertCursor(outFC)
  except:
    gp.AddMessage("failed to create cursor")
    del gp
    sys.exit()
  anID=0
  polyArray = gp.CreateObject("Array")
  aPnt = gp.CreateObject("Point")
  for i in range(0,len(outPntsList)):
    outShape = outPntsList[i][0]
    anID = outPntsList[i][1]
    for aPair in outShape:
      aPnt.x = aPair[0]
      aPnt.y = aPair[1]
      polyArray.add(aPnt)
    feat = cur.NewRow()
    feat.shape = polyArray
    feat.id = anID
    if len(theFields) != 0:
      for j in range(0, len(theFields)):
        aField = theFields[j]
        feat.setvalue(aField[0],outPntsList[i][j+1])
    cur.InsertRow(feat)
    polyArray.RemoveAll()
    anID=anID+1
  del cur
  del polyArray
  del aPnt
#----------------------------------------------------------
def RegressCircLinear(thePnts):
  N = len(thePnts)
  theXLst = []
  theYLst = []
  for i in thePnts:
    X = i[0]; Y = i[1]
    theXLst.append(X); theYLst.append(Y)
  #
  #Get the points and form the matrix
  A_00 = 0.0; A_01 = 0.0; A_02 = 0.0; A_03 = 0.0
  A_10 = 0.0; A_11 = 0.0; A_12 = 0.0; A_13 = 0.0
  A_20 = 0.0; A_21 = 0.0; A_22 = 0.0; A_23 = 0.0
  #
  for i in range(0,N):
    X = theXLst[i]; Y = theYLst[i]
    Z = (X**2)+(Y**2)
    A_00 = A_00 + (Z**2)
    A_01 = A_01 + (Z*X)
    A_02 = A_02 + (Z*Y)
    A_03 = A_03 + (Z)
    A_11 = A_11 + (X**2)
    A_12 = A_12 + (X*Y)
    A_13 = A_13 + (X)
    A_22 = A_22 + (Y**2)
    A_23 = A_23 + (Y)
  
  A_10 = A_01; A_20 = A_02; A_21 = A_12
  #
  aMatrix = [ [A_00, A_01, A_02, A_03],
            [A_10, A_11, A_12, A_13],
            [A_20, A_21, A_22, A_23]
            ]
  #
  theReturned = GaussianElim(aMatrix)   #run Gaussian Elimination
  B0 = theReturned[0]; B1 = theReturned[1]; B2 = theReturned[2]
  Xo = (-B1)/(2.0*B0)
  Yo = (-B2)/(2.0*B0)
  Ro = abs( math.sqrt(abs((4.0*B0) + (B1**2) + ((B2**2)))) / (2*B0))
  #
  aReport = "Circle X,Y and radius" + "\n" + \
          "Xo: " + str(Xo) + "\n" + \
          "Yo: " + str(Yo) + "\n" + \
          "Ro : " + str(Ro)  + "\n" + "\n" + \
          "Matrix Values"+ "\n" + \
          str(A_00) + ", " + str(A_01) + ", " + \
          str(A_02) + ", " + str(A_03) + "\n" + \
          str(A_10) + ", " + str(A_11) + ",  " + \
          str(A_12) + ", " + str(A_13) + "\n" + \
          str(A_20) + ", " + str(A_21) + ", " + \
          str(A_22) + ", " + str(A_23) + "\n" + "\n" + \
          "Matrix Solution"+ "\n" + \
          "b0: " + str(B0) + "\n" + \
          "b1: " + str(B1) + "\n" + \
          "b2: " + str(B2)
  #print aReport
  return [aReport,Xo,Yo,Ro ]
#----------------------------------------------------------
def RegressCircNonLinear(thePnts,Xo,Yo,Ro):
  # thePnts  a list of points
  # Xo       estimate of circle center X
  # Yo       estimate of circle center X
  # Ro       estimate of circle radius
  N = len(thePnts)
  SumX = 0.0; SumY = 0.0
  for aPnt in thePnts:
    SumX = SumX + aPnt[0]
    SumY = SumY + aPnt[1]
  theAvgX = SumX/N; theAvgY = SumY/N
  theXs=[]; theYs=[]
  for aPnt in thePnts:
    theXs.append(aPnt[0] - theAvgX)
    theYs.append(aPnt[1] - theAvgY)
  Xo = Xo - theAvgX
  Yo = Yo - theAvgY
  rA, rB, rC = None, None, None
  aStep=0
  theDiff=999999999
  aTolerance=0.00000001   #tolerance in the X, Y and/or R values
  aReport="Circular Non-Linear Regression results" + "\n"
  while aStep < 11:
    if abs(theDiff) < aTolerance:
      break
    aStep=aStep+1
    #
    #Get the points and form the matrix
    A_00=0.0;  A_01=0.0;  A_02=0.0;  A_03=0.0
    A_10=0.0;  A_11=0.0;  A_12=0.0;  A_13=0.0
    A_20=0.0;  A_21=0.0;  A_22=0.0;  A_23=0.0
    for i in range(0, N):
      X = theXs[i];  Y = theYs[i]
      Bott=math.sqrt( (X**2)-(2.0*X*Xo)+(Y**2)-(2.0*Yo*Y)+(Xo**2)+(Yo**2) )
      K1 = math.sqrt(((X-Xo)**2)+((Y-Yo)**2))
      A = (Xo-X)/Bott
      B = (Yo-Y)/Bott
      C = (-1.0)
      K =(0.0-(K1-Ro))    
      #                     Equation form
      A_00 = A_00+(A**2)  # A*Sum(A**2)+B*2Sum(AB) +C*Sum(AC) +Sum(AK) =0
      A_01 = A_01+(A*B)  # A*Sum(AB) +B*2Sum(B**2)+C*Sum(BC) +Sum(BK) =0
      A_02 = A_02+(A*C)  # A*Sum(AC) +B*2Sum(BC) +C*Sum(C**2)+Sum(-K) =0
      A_03 = A_03+(A*K)
      A_11 = A_11+(B**2)
      A_12 = A_12+(B*C)
      A_13 = A_13+(B*K)
      A_22 = A_22+(C**2)
      A_23 = A_23+(-K)
    #
    A_10=A_01;  A_11=A_11;  A_20=A_02;  A_21=A_12
    #
    theArray=[ [A_00, A_01, A_02, A_03],
               [A_10, A_11, A_12, A_13],
               [A_20, A_21, A_22, A_23]
             ]
    #
    #Perform the Gaussian Elimination
    #
    theReturned=GaussianElim(theArray)
    A=theReturned[0]
    B=theReturned[1]
    C=theReturned[2]
    theBiggest = max([max([abs(A),abs(B)]), abs(C)])
    theDiff = min([theDiff, theBiggest])
    Xo = Xo + A;  Yo = Yo + B;  Ro = Ro + C
    #
    aReport=aReport + "\n" + \
            "Iteration " + str(aStep) + "\n" + \
            "Xo: "+ str(Xo+theAvgX) + "\n" + \
            "Yo: "+ str(Yo+theAvgY) + "\n" + \
            "R : "+ str(Ro) + "\n" + \
            "Matrix Values  " + "\n" + \
            str(A_00) + ", " + str(A_01) + ", " + \
            str(A_02) + ", " + str(A_03) + "\n" + \
            str(A_10) + ", " + str(A_11) + ", " + \
            str(A_12) + ", " + str(A_13) + "\n" + \
            str(A_20) + ", " + str(A_21) + ", " + \
            str(A_22) + ", " + str(A_23) + "\n" + \
            "Delta X: " + str(A) + "\n" + \
            "Delta Y: " + str(B) + "\n" + \
            "Delta R: " + str(C) + "\n"
    rA = A
    rB = B
    rC = C
  Xo = Xo + theAvgX
  Yo = Yo + theAvgY
  return [aReport, Xo, Yo, Ro, str(rA), str(rB), str(rC)]
#-------------------------------------------------------------
def shapeToPoints(aShape,theType,gp):
  #Purpose:  Converts a shape to points, the shape and its type
  #  are passed by the calling script
  #Requires:  def pntXY(pnt)
  outList=[]
  i = 0
  if theType == "Multipoint":      #multipoint
    while i < aShape.PartCount:
      pnt = aShape.GetPart(i)
      XY=pntXY(pnt)
      if XY not in outList:
        outList.append(XY)
      i = i + 1
  else:                            #polylines or polygons
    while i < aShape.PartCount:    #cycle through the parts of the shape
      anArray = aShape.GetPart(i)
      numVertices = anArray.count  #number of vertices or null points
      if theType == "Polyline":
        dupCheck = 1
      else:
        dupCheck = 2
      anArray.Reset()
      pnt=anArray.Next()
      j = 0
      while j < (numVertices-dupCheck):   #cycle through the points of the shape
        pnt = anArray.GetObject(j)
        XY = pntXY(pnt)            #call pntXY
        if XY not in outList:
          outList.append(XY)
        #check for null point (rings/donuts check)
        pnt = anArray.GetObject(j + 1)
        if not pnt:                #null point identifying donut
          j = j + 1
        else:
          XY = pntXY(pnt)
          if XY not in outList:
            outList.append(XY)
        j = j + 1
      i = i + 1
  return outList
#-------------------------------------------------------------
