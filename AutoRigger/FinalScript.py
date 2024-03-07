'''
Vehicle autorigger
Group NAG - Noah Pereria, Ash Li, Graham Connell
Version 0.5

changelog:
* added hydraulic rig controls
* added basic global control creation section
* Added wheel rig UI and functions
* Added annotations for wheel UI

To do:
* Edit look of Hydrolics section
* Edit global section to link it to the rest of the controls better
* Add explainer text and annotations to UI elements
* Clean up UI to make it consistent
'''

import maya.cmds as cmds

#Global variables
windowHandle = "vehicleAutoRigger"
locatorsList = []
jointList = []
newControls = []
savedJoints = []
savedControls = []
savedTreads = []

#-----------------------------------------------------------------------------------------
#Functions start -------------------------------------------------------------------------

#Arm functions ---------------------------------------------------------------------------
def modifyArmUI(UIElement):
    match UIElement:
        case "Step 1 ON":
            cmds.frameLayout(UI_armStep1, edit=True, enable=True)
        case "Step 1 OFF":
            cmds.frameLayout(UI_armStep1, edit=True, enable=False)
        case "Step 2 ON":
            cmds.frameLayout(UI_armStep2, edit=True, enable=True)
        case "Step 2 OFF":
            cmds.frameLayout(UI_armStep2, edit=True, enable=False)
        case "IK/FK switch":
            isIK = cmds.optionMenuGrp( UI_IKFKSwitch, query=True, value=True)
            if isIK == "IK":
                cmds.columnLayout(UI_FKControls, edit=True, visible=False)
                cmds.columnLayout(UI_IKControls, edit=True, visible=True)
            else:
                cmds.columnLayout(UI_IKControls, edit=True, visible=False)
                cmds.columnLayout(UI_FKControls, edit=True, visible=True)
                
        case "IK/FK Layout ON":
            cmds.columnLayout(UI_IKFIKLayout, edit=True, enable=True)
        case "IK/FK Layout OFF":
            cmds.columnLayout(UI_IKFIKLayout, edit=True, enable=False)

        case "Create joints ON":
            cmds.button(UI_createJoints, edit=True, enable=True)
        case "Create joints OFF":
            cmds.frameLayout(UI_armStep2, edit=True, enable=False)
            cmds.button(UI_createJoints, edit=True, enable=False)
        
        case "Set button Create joints":
            cmds.button(UI_createJoints, edit=True, label="Create joints")
        case "Set button Edit joints":
            cmds.button(UI_createJoints, edit=True, label="Edit joints")

        case "Create FK ON":
            cmds.button(UI_IKCreateButton, edit=True, enable=True)    
        case "Create FK OFF":
            cmds.button(UI_IKCreateButton, edit=True, enable=False)  
        
        case "Save rig ON":
            cmds.button(UI_saveRig, edit=True, enable=True)
        case "Save rig OFF":
            cmds.button(UI_saveRig, edit=True, enable=False)  

def makeLocators():
    
    jointQuantity = cmds.intSliderGrp( numSegments, query=True, value=True) + 1
    global locatorsList

    #Replaces existing locators if no joints have been created for error prevention
    if locatorsList:
        cmds.select(locatorsList)
        cmds.delete()

    locatorsList = []
    
    for locatorNum in range( 1,jointQuantity + 1 ):
        locatorsList.append( cmds.spaceLocator(name="Locator0%s"%locatorNum, position=(0,0,(locatorNum-1)*3) )[0] )
        cmds.scale(2,2,2)
        cmds.CenterPivot()
    
    modifyArmUI("IK/FK Layout ON")
    #Confirmation for next step
    cmds.confirmDialog(message="Place locator where the joints should go", button="Ok")

    modifyArmUI("Step 1 OFF")
    modifyArmUI("Step 2 OFF")
    modifyArmUI("Create joints ON")

def resetTool():
    global newControls

    if locatorsList:
        cmds.select(locatorsList)
        cmds.delete()
        locatorsList.clear()
    if jointList:
        cmds.delete(jointList)
        jointList.clear()

    if newControls:
        cmds.select(newControls)
        cmds.delete()
        newControls = None

    #Disable later UI steps
    modifyArmUI("Set button Create joints")
    modifyArmUI("Create FK OFF")
    modifyArmUI("Create joints ON")    
    modifyArmUI("IK/FK Layout OFF")
    modifyArmUI("Save rig OFF")
    modifyArmUI("Step 1 ON")
    modifyArmUI("Step 2 ON")
    
def saveRig():
    global savedJoints, savedControls, newControls, jointList

    if jointList:
        savedJoints.append(jointList)
    
    if newControls:
        savedControls.append(newControls)
    
    jointList.clear()
    newControls.clear()
    cmds.select(clear=True)

    modifyArmUI("Set button Create joints")
    modifyArmUI("Save rig OFF")
    cmds.confirmDialog(title="Rig saved!", message="Rig successfully saved.\nYou may create additional rigs.", button="Ok")

def saveLocators():
    global locatorPosition
    locatorPosition = []
    
    for locator in locatorsList:
        locatorPosition.append(cmds.getAttr(locator+".wp")[0])
    
def createRig(isIK):
    saveLocators() #Get locator positions
    global jointList

    #Removes joints and resets the 'create joints' button after user enters edit joints mode
    if cmds.button(UI_createJoints, query=True, label=True) == "Edit joints" and isIK:
        cmds.delete(jointList)
        jointList.clear()
        modifyArmUI("Set button Create joints")
        modifyArmUI("Create FK OFF")
        return

    jointList = []
    global jointName
    jointName = cmds.textFieldGrp(UI_jointName, query=True, text=True)
    
    cmds.select(clear=True)
    for i in range(len(locatorPosition)):
        jointList.append(cmds.joint(name=jointName + "_" + str(i+1), position=locatorPosition[i]))
        
    if isIK:
        cmds.confirmDialog(message="Select your first and last joint for IK rig", button="OK")
    print(jointList)

    modifyArmUI("Set button Edit joints")
    modifyArmUI("Create FK ON")
        
def createIK():
    global newControls
    selectedJoints = []
    selectedJoints = cmds.ls( sl=True )

    #Error catching wrong number of joints selected
    if len(selectedJoints) != 2:
        cmds.confirmDialog(title="Error - Joint selection", message="There must be exactly 2 joints selected.\nPlease select only 2 joints and try the 'Create IK' button again", button="Ok")
        cmds.select(clear=True)
        return
    
    newIK = cmds.ikHandle(name="IKCT", sj=selectedJoints[0], ee=selectedJoints[1], snapCurve=False)
    newControls = cmds.circle(name=jointName + "_Ctrl", radius=4, nr=(0,1,0))
    cmds.matchTransform(newControls, newIK, position=True, rotation=True)
    cmds.select(newControls)
    cmds.FreezeTransformations()
    cmds.parentConstraint(newControls, newIK[0], mo=True)
    
    #Delete locators
    if locatorsList:
        cmds.select(locatorsList)
        cmds.delete()
        locatorsList.clear()
    
    modifyArmUI("Create FK OFF")
    modifyArmUI("Save rig ON")
    modifyArmUI("Set button Create joints")
    modifyArmUI("IK/FK Layout OFF")
    
def createFK(): 
    createRig(False)
    global newControls
    newControls = []

    #Create joints for FK rig
    for i in range(len(jointList)-1):
        newControls.append(cmds.circle(name=jointName + "_" + str(i+1) + "_Ctrl", radius=4, nr=(0,1,0))[0])
        cmds.matchTransform(newControls[i], jointList[i], position=True, rotation=True)
        cmds.FreezeTransformations()
        cmds.parentConstraint(newControls[i], jointList[i], mo=True)
    
    #Create controls for FK rig
    for j in range(len(newControls)-1):
        cmds.parent(newControls[j+1], newControls[j], relative=True)

    #Delete locators
    if locatorsList:
        cmds.select(locatorsList)
        cmds.delete()
        locatorsList.clear()

    modifyArmUI("Save rig ON")
    modifyArmUI("IK/FK Layout OFF")

#Tread functions -------------------------------------------------------------------------
def treadUI():
    global UI_MainLayout
    global UI_treadLayout
    UI_treadLayout = cmds.columnLayout("primaryLayout", margins=2, parent=UI_MainLayout)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(450,50) )
    cmds.text(label="Creates treads with a rig using a selected object for a tread segment, or a default component", wordWrap=True, width=450, align="left")
    treadUI.resetButton = cmds.button(label="Reset", width=50, c='resetAll()',en=False, annotation="Deletes all unsaved progress to start over")
    cmds.setParent(UI_treadLayout)

    #Step 1: Initialize
    treadUI.UI_step1 = cmds.frameLayout(label="Step 1 - Create locators", collapsable=True, width=500, backgroundColor=(0.27,0.27,0.27))
    cmds.text(label="Creates locators, place these at the bounds you want the tread to be within.", wordWrap=True, width=200, align="left")
    treadUI.initButton=cmds.button(l="Initialize",c="initFunc()", width=80)
    cmds.separator(w=500)
    cmds.setParent(UI_treadLayout)

    #Step 2: Create curve
    treadUI.UI_step2 = cmds.frameLayout(label="Step 2 - Create curve", collapsable=True, enable=False, width=500, collapse=True, backgroundColor=(0.27,0.27,0.27))
    cmds.text(label="Creates circle curve between locators. Edit the path vertices to change the tread shape.", wordWrap=True, width=200, align="left")
    treadUI.MakeCurveBTN=cmds.button(label="Make Tread Curve",command="MakeCurve()",enable=True)
    cmds.separator(w=500)
    cmds.setParent(UI_treadLayout)

    #Step 3: Select tread object
    treadUI.UI_step3 = cmds.frameLayout(label="Step 3 - Select tread object", collapsable=True, enable=False, width=500, collapse=True, backgroundColor=(0.27,0.27,0.27))
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(350,50) )
    treadUI.ObjText=cmds.textFieldButtonGrp(bl="Use selected object",bc="selectTreadObject()",ed=False)
    treadUI.UI_createTreadSegment = cmds.button(label="Use default", command="createTreadSegment()")
    cmds.setParent(treadUI.UI_step3)
    treadUI.UI_step3Continue = cmds.button(label="Continue", command="step3Continue()", enable=False)
    cmds.separator(w=500)
    cmds.setParent(UI_treadLayout)

    #Step 4: Create tread
    treadUI.UI_step4 = cmds.frameLayout(label="Step 4 - Create tread", collapsable=True, enable=False, width=500, collapse=True, backgroundColor=(0.27,0.27,0.27))
    cmds.text(label="Set number of tread segments along the curve", wordWrap=True, width=200, align="left")
    treadUI.CopyNum=cmds.intSliderGrp(min=10,v=25,cc="numChange()",f=True)
    #treadUI.makeTread=cmds.button(l="MakeTread",c="MakeTankTread()")
    treadUI.finalizeTread=cmds.button(l="Finalize",c="finalizeTread()")
    cmds.separator(w=500)
    cmds.setParent(UI_treadLayout)

    #Options
    treadUI.UI_optionsLayout = cmds.frameLayout(label="Options", collapsable=False, enable=False, width=500, backgroundColor=(0.27,0.27,0.27))
    cmds.text(label="Duplicate will create copies of the tread in the menu.\nMirror will mirror the current tread in the menu.\nNOTE: Mirrored treads cannot be duplicated.", wordWrap=True, width=200, align="left")
    #treadUI.UI_saveButton = cmds.button(label="Save", command="saveTread()")

    #Mirror/Copy options
    #cmds.setParent(UI_treadLayout)
    treadUI.UI_modifyLayout = cmds.rowColumnLayout("UI_modifyLayout", w=500, numberOfColumns=2, enable=False)
    treadUI.UI_treadSelectMenu = cmds.optionMenu(label="Tread to modify" )
    #cmds.setParent(treadUI.UI_optionsLayout)
    treadUI.UI_duplicateButton = cmds.button(label="Duplicate", command="duplicateTread()")
    treadUI.UI_radioMirrorPlane = cmds.radioButtonGrp(label="Mirror plane", labelArray3=('xy','xz','yz'),numberOfRadioButtons=3, columnWidth4=(140,40,40,40), select=3)
    treadUI.UI_mirrorButton = cmds.button(label="Mirror tread", command="mirrorTread()")

def editTreadUI(UIelement, UIbool):
    match UIelement:
        case "Reset button":
            cmds.button(treadUI.resetButton, edit=True, enable=UIbool)
        case "Step 1":
            cmds.frameLayout(treadUI.UI_step1, edit=True, enable=UIbool, collapse=not UIbool)
        case "Step 2":
            cmds.frameLayout(treadUI.UI_step2, edit=True, enable=UIbool, collapse=not UIbool)
        case "Step 3":
            cmds.frameLayout(treadUI.UI_step3, edit=True, enable=UIbool, collapse=not UIbool)
        case "Step 3 continue":
            cmds.button(treadUI.UI_step3Continue, edit=True, enable=UIbool)
        case "Step 4":
            cmds.frameLayout(treadUI.UI_step4, edit=True, enable=UIbool, collapse=not UIbool)
        case "Options layout":
            cmds.frameLayout(treadUI.UI_optionsLayout, edit=True, enable=UIbool, collapse=not UIbool)
        case "Modify layout":
            cmds.rowColumnLayout(treadUI.UI_modifyLayout, edit=True, enable=UIbool)
        case "Segment selector":
            cmds.textFieldButtonGrp(treadUI.ObjText, edit=True, text=UIbool)

def resetAll():
    #Edit visible UI
    editTreadUI("Reset button", False)
    editTreadUI("Step 1", True)
    editTreadUI("Step 2", False)
    editTreadUI("Step 3", False)
    editTreadUI("Segment selector", "")
    editTreadUI("Step 4", False)
    editTreadUI("Options layout", False)

    #Delete objects if they exist, ignore if not
    try: cmds.delete("LocGRP")
    except: pass
    try: cmds.delete("TreadCurve")
    except: pass
    try: cmds.delete("TreadSegmentDefault")
    except: pass
    try: cmds.select(selectedOBJ)
    except: pass
    cmds.DeleteMotionPaths()
    try: cmds.delete("TreadSSGroup")
    except: pass

def initFunc():
    cmds.spaceLocator(n="CircleLocFront")
    cmds.move(0,0,6)
    cmds.scale(5,5,5)
    cmds.spaceLocator(n="CircleLocBack")
    cmds.move(0,0,-6)
    cmds.scale(5,5,5)
    #we are grouping the locators for easier access and alignment
    cmds.group("CircleLocFront","CircleLocBack",n="LocGRP")
    cmds.confirmDialog(m="now you have 2 locators. placed them where the two ends of your tread want to be")
    
    #Edit visible UI
    editTreadUI("Reset button", True)
    editTreadUI("Step 1", False)
    editTreadUI("Step 2", True)

def MakeCurve():
    #here we take the distance of the two locators 
    FrontLocPos=cmds.getAttr("CircleLocFront.translateZ")
    BackLocPos=cmds.getAttr("CircleLocBack.translateZ")
    print ("CLF z is: %s" %FrontLocPos + "BLF z is: %s" %BackLocPos)
    locDistance=abs(FrontLocPos - BackLocPos)
    CurveCenter=locDistance/2
    cmds.select("LocGRP")
    cmds.CenterPivot()
    treadCurve=cmds.circle(n="TreadCurve",r=CurveCenter,nr=(1,0,0))
    cmds.select(treadCurve,r=True)
    cmds.select("LocGRP",add=True)
    cmds.align(z="mid", atl=True)
    cmds.select(treadCurve,r=True)
    cmds.FreezeTransformations()
    
    editTreadUI("Step 2", False)
    editTreadUI("Step 3", True)
    cmds.select(clear=True)
    
def selectTreadObject():
    global selectedOBJ
    selectedOBJ=cmds.ls(sl=True,objectsOnly=True)
    #If selection is empty, or doesn't contain an object throw an error
    if not selectedOBJ:
        #Offer to use the default tread in error, or if user wants to retry selecting object (returns function with no action)
        UI_selectionError = cmds.confirmDialog(t="Error - no selected object", m="Must select an object to use as a tread segment", b=['Select new object','Use default tread segment'], cb='No')
        if UI_selectionError == "Use default tread segment":
            createTreadSegment()
            editTreadUI("Step 3 continue", True)
            return selectedOBJ
        else:
            return
    #print (selectedOBJ[0])
    cmds.textFieldButtonGrp(treadUI.ObjText,e=True,tx=selectedOBJ[0])
    editTreadUI("Step 3 continue", True)
    return selectedOBJ
    
def numChange():
    global updateCopyNum
    updateCopyNum=cmds.intSliderGrp(treadUI.CopyNum,q=True,v=True)
    print ("current number is: %s" %updateCopyNum)
    cmds.delete("TreadSSGroup")
    MakeTankTread()
    return updateCopyNum

def createTreadSegment():
    global selectedOBJ

    if cmds.objExists("TreadSegmentDefault"):
        cmds.textFieldButtonGrp(treadUI.ObjText,e=True,tx="TreadSegmentDefault")
        selectedOBJ = cmds.select("TreadSegmentDefault")
        return
    
    selectedOBJ = cmds.polyCube(name="TreadSegmentDefault", h=0.3, w=2, d=1, sh=2, sw=5, sd=3)
    #cmds.select ("TreadSegmentDefault.f[11]", r=True)
    #cmds.extrude(et = 0, d= (1, 0, 0), l= 5)
    selectTreadObject()

def step3Continue():
    global updateCopyNum
    updateCopyNum = 25

    editTreadUI("Step 3 continue", False)
    editTreadUI("Step 3", False)
    editTreadUI("Step 4", True)
    MakeTankTread()

def MakeTankTread():
    #step 1 animate selected object along the curve
    #cmds.select(selectedOBJ, r=True)
    #cmds.select("TreadCurve", add=True)

    #Adjust updateCopyNum so the correct number of tread segments are built
    global updateCopyNum
    updateCopyNum+=1
    cmds.pathAnimation(selectedOBJ,curve="TreadCurve",fractionMode=True,follow=True,followAxis="z",upAxis="y",worldUpType="object",wu=(0,1,0),inverseFront=False,inverseUp=True,bank=False,startTimeU=1,endTimeU=updateCopyNum)
    cmds.select(selectedOBJ,r=True)
    cmds.selectKey('motionPath1_uValue',time=(1,updateCopyNum))
    cmds.keyTangent(itt="linear",ott="linear")
    cmds.snapshot(n="TreadSS",i=1,ch=False,st=1,et=updateCopyNum-1,u="animCurve") #remove 1 from updateCopyNum to ensure no overlapping segments are created
    cmds.DeleteMotionPaths()
    
def finalizeTread():
    #now we combine all objects of snapshot and delete the snapshot node
    cmds.select("TreadSSGroup",r=True)
    cmds.polyUnite(n="TreadFull",ch=False)
    cmds.delete("TreadSSGroup")
    cmds.delete("LocGRP")
    # here we create a wire deformer function

    cmds.select("TreadFull")
    wireOBJ=cmds.ls(sl=True,o=True)[0]
    cmds.select("TreadCurve")
    wirecurve=cmds.ls(sl=True,o=True)[0]
    wire=cmds.wire(wireOBJ,w=wirecurve,n='_wire')
    finalizeTread.wirenode=wire[0]
    cmds.setAttr(finalizeTread.wirenode+'.dropoffDistance[0]',40)

    cmds.hide(selectedOBJ)

    editTreadUI("Step 4", False)
    editTreadUI("Save button", True)
    editTreadUI("Options layout", True)
    saveTread()

def createWire(treadGrp, treadCurve):
    cmds.select(treadGrp[0])
    wireOBJ=cmds.ls(sl=True,o=True)[0]
    cmds.select(treadCurve)
    wirecurve=cmds.ls(sl=True,o=True)[0]
    wire=cmds.wire(wireOBJ,w=wirecurve,n='_wire')
    finalizeTread.wirenode=wire[0]
    cmds.setAttr(finalizeTread.wirenode+'.dropoffDistance[0]',40)

def saveTread():
    treadNumber = str(len(savedTreads)+1)

    cmds.select("TreadFull", replace=True)
    cmds.rename("TreadMesh_"+treadNumber)
    savedTread = cmds.ls(sl=True)[0]
    cmds.CenterPivot()
    cmds.select("TreadCurve", replace=True)
    cmds.rename("TreadCurve_"+treadNumber)
    savedCurve = cmds.ls(sl=True)[0]
    cmds.select("TreadCurveBaseWire", replace=True)
    cmds.rename("TreadCurveBaseWire_"+treadNumber)
    savedTreadWire = cmds.ls(sl=True)[0]

    newGroup = cmds.group(savedTread,savedCurve,savedTreadWire, name='treadGrp_'+treadNumber)
    
    #RotateControl
    rotateControl = cmds.circle(name=newGroup+"_RotateCTRL", normal=(1,0,0))
    cmds.color(rotateControl, rgb=(0,1,0))
    cmds.parent(rotateControl, newGroup)
    cmds.matchTransform(rotateControl, newGroup)
    cmds.FreezeTransformations()
    cmds.parentConstraint(rotateControl, savedTread, skipTranslate=["x","y","z"])

    savedLocatorGroup = createLocators(savedCurve, newGroup)
    savedControlGroup = createControls(savedLocatorGroup)
    cmds.parent(savedControlGroup, newGroup)
    #save a new dictionary with tread values
    addSavedTread('treadGrp_'+treadNumber, savedTread, savedCurve, savedTreadWire)

    resetAll()
    editTreadUI("Save button", False)
    editTreadUI("Modify layout", True)
    editTreadUI("Options layout", True)

def mirrorTread():
    #Get tread from selection menu and get position
    selectedTreadIndex = cmds.optionMenu(treadUI.UI_treadSelectMenu, query=True, select=True)
    treadGrp = cmds.optionMenu(treadUI.UI_treadSelectMenu, query=True, itemListShort=True)[selectedTreadIndex-1]
    currentPosition = cmds.getAttr(treadGrp+".translate")[0]

    #Mirror over xy, xz, yz planes
    match cmds.radioButtonGrp(treadUI.UI_radioMirrorPlane, query=True, select=True):
        case 1:
            cmds.setAttr(treadGrp+".translateZ", -currentPosition[2] )
            currentScale = cmds.getAttr(treadGrp+".scaleZ")
            cmds.setAttr(treadGrp+".scaleZ", -1*currentScale)
        case 2:
            cmds.setAttr(treadGrp+".translateY", -currentPosition[1] )
            currentScale = cmds.getAttr(treadGrp+".scaleY")
            cmds.setAttr(treadGrp+".scaleY", -1*currentScale)
        case 3:
            cmds.setAttr(treadGrp+".translateX", -currentPosition[0] )
            currentScale = cmds.getAttr(treadGrp+".scaleX")
            cmds.setAttr(treadGrp+".scaleX", -1*currentScale)

def addSavedTread(groupName, savedTread, savedCurve, savedTreadWire):
    newTread = {
        'group': groupName,
        'mesh': savedTread,
        'curve': savedCurve,
        'wire': savedTreadWire
    }

    savedTreads.append(newTread)

    cmds.menuItem(savedTreads[len(savedTreads)-1]['group'], parent=treadUI.UI_treadSelectMenu)

def duplicateTread():

    #Get index of selected tread in UI_treadSelectMenu
    selectedTreadIndex = cmds.optionMenu(treadUI.UI_treadSelectMenu, query=True, select=True)
    #Get tread group from the index
    selectedTreadObject = cmds.optionMenu(treadUI.UI_treadSelectMenu, query=True, itemListShort=True)[selectedTreadIndex-1]

    #Error prevention for mirrored treads
    axes = ["z","y","x"]
    axisError = ""
    index = 0
    scale = cmds.getAttr(selectedTreadObject+".scale")[0]
    for axis in scale:
        print(axes)
        print(index)
        if axis < 0:
            axisError+=axes.pop()+", "
        index+=1
    print(axisError)
    if len(axisError) != 0:
        axisError = axisError[:-2]
        cmds.confirmDialog(title="Error - Negative scale value", message="Duplicate is unavailable on treads that have been mirrored. Remove negative scale on the following axes:\n%s"%axisError, button="Ok")
        return

    #Get tread position and create a new empty group, place group in the same location
    originalTreadPosition = cmds.getAttr(selectedTreadObject+".translate")[0]
    newGroup = cmds.group(name=selectedTreadObject, empty=True)
    cmds.setAttr(newGroup+".translate", originalTreadPosition[0],originalTreadPosition[1],originalTreadPosition[2])
    cmds.CenterPivot(newGroup)

    #Save control positions
    originalControlPositions = saveTreadHandlePositions(selectedTreadObject+"_TreadHandles")

    deleteOriginalHandles(selectedTreadObject+"_TreadHandles")
    
    #Create new tread object and curve
    newObjectList = []
    iterator = 0
    print(cmds.listRelatives(selectedTreadObject, children=True))
    for object in cmds.listRelatives(selectedTreadObject, children=True):
        if iterator < 2:
            newObjectList.append(cmds.duplicate(object))
            cmds.parent(newObjectList[-1][0],newGroup)
        iterator+=1

    #Create new wire deformer
    createWire(newObjectList[0], newObjectList[1])

    #Create new locators and controls for them
    newLocators = createLocators(newObjectList[1], newGroup)
    newControls = createControls(newLocators, True, originalControlPositions)
    cmds.parent(newControls, newGroup)
    cmds.setAttr(newControls+".translate", 0,0,0 )

    #Reset original tread handles and reparent them
    originalHandles = createControls(selectedTreadObject+"Locators", True, originalControlPositions)
    cmds.parent(originalHandles, selectedTreadObject)
    cmds.setAttr(originalHandles+".translate", 0,0,0 )
    
    # Renaming base wire curve
    cmds.select(cmds.listRelatives(newGroup, children=True)[2])
    newObjectList.append(cmds.rename("TreadCurveBaseWire_"+str(len(savedTreads)+1)))

    addSavedTread(newGroup, newObjectList[0], newObjectList[1], newObjectList[2])

    #RotateControl
    rotateControl = cmds.circle(name=newGroup+"_RotateCTRL", normal=(1,0,0))
    cmds.color(rotateControl, rgb=(0,1,0))
    cmds.parent(rotateControl, newGroup)
    cmds.matchTransform(rotateControl, newObjectList[1])
    cmds.FreezeTransformations()
    cmds.parentConstraint(rotateControl, newObjectList[0][0], skipTranslate=["x","y","z"])

    currentMenuSelection = cmds.optionMenu(treadUI.UI_treadSelectMenu, query=True, numberOfItems=True)
    cmds.optionMenu(treadUI.UI_treadSelectMenu, edit=True, select=currentMenuSelection)

    cmds.select(newGroup)

def createLocators(curve, treadGroup):
    cmds.select(curve)
    selectedCurve = cmds.ls(sl=True)
    editPointList = cmds.ls(selectedCurve[0]+".ep[*]", fl=True)

    locatorGroupName = treadGroup+"Locators"
    locatorList = []

    skipEditPoint = 0
    for editPointIndex in editPointList:
        if skipEditPoint % 2 == 0:
            cmds.select(editPointIndex, replace=True)
            cmds.pointCurveConstraint()
            cmds.CenterPivot()
            locatorList.append(cmds.rename(locatorGroupName+"_1"))
        skipEditPoint+=1

    cmds.select(locatorList)
    cmds.group(name=locatorGroupName)
    cmds.parent(locatorGroupName, treadGroup)
    #cmds.select(selectedCurve)
    return locatorGroupName

def createControls(locatorGroupName, resetHandle=False, originalControlPositions = []):
    newControls = []
    cmds.select(locatorGroupName)
    locatorGroup = cmds.listRelatives(children=True)

    #Iterate through contrained locators and parent constrain them to curves for controls
    iterator = 1
    for locator in locatorGroup:
        newControls.append(cmds.circle(name=locatorGroupName.split("Locators")[0]+"TreadHandle_1", normal=(1,0,0))[0])
        cmds.DeleteHistory()
        cmds.select(locator, add=True)
        cmds.matchTransform()
        cmds.parentConstraint(weight=1)
        cmds.hide(locator)
        iterator+=1
    
    if resetHandle == True:
            resetHandlePositions(newControls, originalControlPositions)

    cmds.select(newControls)
    return cmds.group(name=locatorGroupName.split("Locators")[0] + "_TreadHandles")

def saveTreadHandlePositions(handleGroup):
    treadHandlePositions = []

    handleList = cmds.listRelatives(handleGroup, children=True)
    for handle in handleList:
        treadHandlePositions.append(cmds.getAttr(handle+".translate"))

    return treadHandlePositions

def deleteOriginalHandles(handleGroup):
    cmds.delete(handleGroup)
    '''handleList = cmds.listRelatives(handleGroup, children=True)

    for handle in handleList:
        cmds.delete(handle)'''

def resetHandlePositions(newControls, originalControlPositions):
    iterator = 0
    for control in newControls:
        #Get original handle position
        controlPosition = originalControlPositions[iterator][0]
        cmds.setAttr(control+".translate", float(controlPosition[0]), float(controlPosition[1]), float(controlPosition[2]))
        iterator+=1

#Hydrolic functions ----------------------------------------------------------------------
def hydraulicUI():
    global UI_MainLayout
    global UI_hydraulicLayout

    UI_hydraulicLayout = cmds.columnLayout("Hydrolic rig", margins=2, parent=UI_MainLayout)

    cmds.frameLayout(label="Aim contraints", width=500, collapsable=False)
    cmds.text("Locks rotation of 2 objects to point at eachother. Useful for hydraulic pistons.\n\nSelect 2 objects to aim at eachother", align="left")
    cmds.rowLayout(height=50, rowAttach=(1,"top",0))
    cmds.button(label="Create aim constraint", command="hydraulicAim()")
    cmds.setParent("..")

    cmds.setParent(UI_hydraulicLayout)
    cmds.frameLayout(label="Translation constraints", width=500, collapsable=False)
    cmds.text("Locks movement of one object to another. Useful when a hydraulic end is anchored to a translating segment of the machine.\n\nSelect parent, then child object to constrain movement", align="left", wordWrap=True)
    cmds.rowLayout(height=50, rowAttach=(1,"top",0))
    cmds.button(label="Create point constraint", command="hydraulicPoint()")
    cmds.setParent("..")

    cmds.setParent(UI_hydraulicLayout)
    cmds.frameLayout(label="Parent constraints", width=500, collapsable=False)
    cmds.text("Used for parenting hydraulics to the machine, allows the hydraulics to rotate freely, but locks their translation to the parent object.\n\nSelect parent, then child object to set contraint for movement", align="left", width=500, wordWrap=True)
    cmds.rowLayout(height=50, rowAttach=(1,"top",0))
    cmds.button(label="Create parent constraint", command="hydraulicParent()")
    cmds.setParent("..")

def hydraulicAim():
    selectedhydraulics = cmds.ls(sl=True)

    if len(selectedhydraulics) != 2:
        cmds.confirmDialog(title="Selection error", message="Please select exactly 2 objects to point at eachother, you may repeat to add additional constraints", button="Ok")
        return
    
    cmds.aimConstraint(selectedhydraulics[0], selectedhydraulics[1], maintainOffset=True)
    cmds.aimConstraint(selectedhydraulics[1], selectedhydraulics[0], maintainOffset=True)

def hydraulicPoint():
    selectedhydraulics = cmds.ls(sl=True)

    if len(selectedhydraulics) != 2:
        cmds.confirmDialog(title="Selection error", message="Please select exactly 2 objects to point at eachother, you may repeat to add additional constraints", button="Ok")
        return
    
    cmds.pointConstraint(selectedhydraulics[0], selectedhydraulics[1], maintainOffset=True)

def hydraulicParent():
    selectedhydraulics = cmds.ls(sl=True)

    if len(selectedhydraulics) != 2:
        cmds.confirmDialog(title="Selection error", message="Please select exactly 2 objects to constrain, you may repeat this action to add additional constraints", button="Ok")
        return
    
    cmds.parentConstraint(selectedhydraulics[0], selectedhydraulics[1], maintainOffset=True, skipRotate=("x","y","z"))

#Wheel functions -------------------------------------------------------------------------
def wheelUI():
    global UI_MainLayout
    global UI_wheelLayout

    UI_wheelLayout = cmds.columnLayout("Wheel rig", margins=2, parent=UI_MainLayout)

    cmds.frameLayout(label="Movement settings", width=500, collapsable=False, annotation="Create a control for spinning wheels based on translation of a control")
    cmds.text("Wheel size will be used to calculate accurate rotation based on vehicle movement with a default of a 1:1 relationship (like car tires to a road)\n\nWheels should be aligned to roll in Z axis", align="left", wordWrap=True)
    wheelUI.UI_wheelRadius = cmds.floatSliderButtonGrp(label="Wheel radius:", value=20, field=True, min=0.001, max=200, buttonLabel="Get selected radius", buttonCommand="getSelectedRadius()", annotation="Set size of wheels for accurate rotation-based movement")
    wheelUI.UI_wheelRatio = cmds.floatSliderGrp(label="Wheel rotation factor:", min=0.001, max=10, value=1, field=True,annotation="Set multiplier for wheel rotation, useful when creating a belt/gear driven system")
    wheelUI.UI_controlNormal = cmds.radioButtonGrp(label="Control orientation:", labelArray2=('x','y'),numberOfRadioButtons=2, columnWidth3=(140,40,40), select=2, annotation="Sets orientation of movement control to face X or Y axis")
    
    cmds.rowLayout( numberOfColumns=2, columnWidth2=(140, 75))
    cmds.separator()
    cmds.button(label="Create movement control", command="wheelMovementControl()", annotation="Creates control for translation to rotate wheels on their X axis")

    #-----------------------------------------------------------------------------
    #Steering wheel settings
    cmds.setParent(UI_wheelLayout)
    cmds.frameLayout(label="Steering settings", width=500, collapsable=False)
    cmds.text("Steering wheel settings --- Pick an object as a steering wheel control", align="left", wordWrap=True)
    wheelUI.UI_steeringObject = cmds.textFieldButtonGrp(label="Steering object:", editable=False, buttonLabel="Set selected", buttonCommand="setSteeringWheel()", annotation="Sets the object to be used for steering wheels")
    wheelUI.UIsteeringAxis = cmds.radioButtonGrp(label="Steering axis:", labelArray3=('x','y','z'),numberOfRadioButtons=3, columnWidth4=(140,40,40,40), select=2, annotation="Sets axis for wheels to follow")
    
    cmds.rowLayout( numberOfColumns=1, columnWidth1=(500))
    cmds.text("Wheel settings --- Selected objects will turn based on the steering wheel with the settings and limits below.", align="left", wordWrap=True)
    cmds.setParent("..")
    wheelUI.UIwheelRotationLimit = cmds.floatSliderGrp(label="Wheel rotation limit (+/-)", min=0, max=90, value=45, field=True, annotation="Max/min rotation amount (degrees) for wheels. steering wheel is unlimited.")
    wheelUI.UIwheelSteeringAxis = cmds.radioButtonGrp(label="Wheel pivot axis:", labelArray3=('x','y','z'),numberOfRadioButtons=3, columnWidth4=(140,40,40,40), select=2, annotation="Axis wheels will rotate on")
    wheelUI.UIwheelPivotInvert = cmds.checkBoxGrp(label="Invert wheel pivot:", numberOfCheckBoxes=1, value1=False, annotation="Inverts the rotation of the wheels, turning opposite to the steering")

    #Create steering wheel buttons
    cmds.rowLayout( numberOfColumns=2, columnWidth2=(140, 75))
    cmds.separator()
    cmds.text("Select wheels to link to steering wheel, then press the button below", align="left", wordWrap=True)
    cmds.setParent("..")
    wheelUI.UI_linkSteering = cmds.rowLayout( numberOfColumns=2, columnWidth2=(140, 75), enable=False)
    cmds.separator()
    cmds.button(label="Link wheels to steering", command="linkSteering()", enable=True)
    
def modifyWheelUI(UIelemnt, UIBool):
    match UIelemnt:
        case "Link steering":
            cmds.rowLayout(wheelUI.UI_linkSteering, edit=True, enable=UIBool)

def getSelectedRadius():

    radiusList = []
    selectedWheels = cmds.ls(sl=True)

    if not selectedWheels:
        cmds.warning("No wheel selected, please select one wheel")
        return
    
    for wheel in selectedWheels:
        radiusList.append(findRadius(getBoundingBoxSize(wheel)))

    if all(x == radiusList[0] for x in radiusList):
        cmds.floatSliderButtonGrp(wheelUI.UI_wheelRadius, edit=True, value=radiusList[0])
    else:
        cmds.floatSliderButtonGrp(wheelUI.UI_wheelRadius, edit=True, value=radiusList[0])
        cmds.warning("Inconsistent radius, it's best to run once for each set of wheels of the same size for proper rotation based movement. Using first radius value")
    
#Returns bounding box dimensions rounded to roundAmount[4] decimal places
def getBoundingBoxSize(selectedObject):
    #Bounding box is in world space

    roundAmount = 3 #Sets precision of bounding box value, too high a value could cause issues due to float math precision
    bboxDimensions = []
    bbox = cmds.exactWorldBoundingBox(selectedObject)

    bboxDimensions.append(round(abs(bbox[0] - bbox[3]),roundAmount))
    bboxDimensions.append(round(abs(bbox[1] - bbox[4]),roundAmount))
    bboxDimensions.append(round(abs(bbox[2] - bbox[5]),roundAmount))

    return bboxDimensions

#Accepts list of bounding box values and returns value that matches in 2 dimensions
#If dimensions aren't a match, Z is used by default
def findRadius(listValues):

    if len(listValues) != 3:
        cmds.warning("Radius cannot be found")
        return

    if listValues[0] == listValues[1]:
        print("Matched X and Y")
        return listValues[0]/2
    elif listValues[0] == listValues[2]:
        print("Matched X and Z")
        return listValues[0]/2
    elif listValues[1] == listValues[2]:
        print("Matched Y and Z")
        return listValues[1]/2
    else:
        cmds.warning("Cannot find radius, using Z dimension as radius")
        return listValues[2]/2

def wheelMovementControl():
    #Get and set variables
    wheelRadius = cmds.floatSliderButtonGrp(wheelUI.UI_wheelRadius, query=True, value=True)
    global selectedWheels
    selectedWheels=cmds.ls(sl=True)
    wheelRotationFactor = str(cmds.floatSliderGrp(wheelUI.UI_wheelRatio,q=True,v=True))

    bboxDimensions = getBoundingBoxSize(selectedWheels)
    
    if len(selectedWheels)==0:
        cmds.confirmDialog(m="No objects selected as wheels\nPlease select at least 1 wheel object")
    else:
        WheelsGRP = cmds.group(n="WheelsGRP#")
        
        WheelCTRL = createArrowShape(bboxDimensions[0], bboxDimensions[1], bboxDimensions[2])
        
        cmds.select(WheelsGRP,add=True)
        cmds.align(x="mid",y="min",z="mid",atl=True)
        #now we need to go through all the wheels in the group and make their rotation follow the arrow
        for wheel in selectedWheels:
            #Set 2 locators for finding wheel direction
            #Get wheel position and a position just in front of it
            wheelLocation = cmds.getAttr(wheel+".translate")[0]
            locator2Position = (wheelLocation[0], wheelLocation[1], wheelLocation[2]+20)
            
            #Set two locators at the current position, and slightly in front
            locator1 = cmds.spaceLocator(name=f"{wheel}Loc#")[0]
            cmds.move(wheelLocation[0],wheelLocation[1],wheelLocation[2],locator1)
            locator2 = cmds.spaceLocator(name=f"{wheel}Loc#")[0]
            cmds.move(locator2Position[0],locator2Position[1],locator2Position[2], locator2)
            cmds.parent(locator1, locator2, WheelsGRP)
            
            cmds.makeIdentity(wheel, rotate=True, apply=True) #objects with transformations can have unexpected movements when function runs, this fixes that
            cmds.expression(n="wheelRotationEXP#",s=wheelExpressionMEL(wheel, wheelRadius, wheelRotationFactor, WheelsGRP,locator1, locator2, WheelCTRL ))

            ''' Old expression
            f"{wheel}.rotateX=(WheelCTRL.translateZ/{wheelRadius}) * 57.2957795*{wheelRotationFactor};"
            '''
        cmds.parentConstraint(WheelCTRL, WheelsGRP,mo=True)

        #Rename new groups so function can run multiple times
        '''cmds.rename("WheelsGRP", "WheelsGRP#")
        cmds.rename("WheelCTRL", "WheelCTRL#")'''
    return selectedWheels

def createArrowShape(arrowScaleX = 1, arrowScaleY = 1, arrowScaleZ = 1):
    normalAxis = ['X','Y','Z']
    controlNormalSelection = cmds.radioButtonGrp(wheelUI.UI_controlNormal, query=True, select=True)
    

    WheelCTRL = cmds.curve(n="WheelCTRL#",d=1,p=[(-10,0,-30),(10,0,-30),(10,0,30),(20,0,30),(0,0,50),(-20,0,30),(-10,0,30),(-10,0,-30),],k=[0,1,2,3,4,5,6,7])
    if controlNormalSelection == 1:
        cmds.setAttr("WheelCTRL.rotateZ", 90)
    elif controlNormalSelection == 2:
        pass
    elif controlNormalSelection == 3:
        cmds.setAttr("WheelCTRL.rotateX", 90)

    cmds.CenterPivot()
    cmds.scale((arrowScaleX*4)/80,(arrowScaleY*2)/80,(arrowScaleZ*1.7)/80,WheelCTRL) #Set to roughly the right size based on the selection

    return WheelCTRL

def setSteeringWheel():
    selectedObjects = cmds.ls(sl=True)

    if not selectedObjects:
        cmds.confirmDialog(title="Selection error", message="No object selected, please select a steering object and try again.", button="Ok")

    cmds.textFieldButtonGrp(wheelUI.UI_steeringObject, edit=True, text=selectedObjects[0])
    modifyWheelUI("Link steering", True)

def linkSteering():
    axis = ['X','Y','Z']
    selectedObjects = cmds.ls(sl=True)

    if not selectedObjects:
        cmds.confirmDialog(title="Selection error", message="No object selected, please select wheels to link to steering", button="Ok")

    #Get steering wheel axis
    steeringObject = cmds.textFieldButtonGrp(wheelUI.UI_steeringObject, query=True, text=True)
    steeringAxisIndex = cmds.radioButtonGrp(wheelUI.UIsteeringAxis, query=True, select=True) - 1
    steeringAxis = axis[steeringAxisIndex]

    wheelRotationLimit = cmds.floatSliderGrp(wheelUI.UIwheelRotationLimit, query=True, value=True)
    #Get wheel pivot axis
    wheelPivotIndex = cmds.radioButtonGrp(wheelUI.UIwheelSteeringAxis, query=True, select=True) - 1
    wheelPivotAxis = axis[wheelPivotIndex]

    invertSteering = cmds.checkBoxGrp(wheelUI.UIwheelPivotInvert, query=True, value1=True)

    linkSteeringToWheels(steeringObject, selectedObjects, steeringAxis, wheelRotationLimit, wheelPivotAxis, invertSteering)

    '''
    Disabled for now, I don't think these are actually needed, it works better if these are left in place once first used so they can be used again
    cmds.textFieldButtonGrp(wheelUI.UI_steeringObject, edit=True, text="")
    modifyWheelUI("Link steering", False)
    '''

def linkSteeringToWheels(steeringObject, selectedWheels, steeringAxis, wheelRotationLimit, wheelPivotAxis, invertSteering):

    if invertSteering:
        steeringMultiplier = -1
    else:
        steeringMultiplier = 1

    for wheel in selectedWheels:
            
            match wheelPivotAxis:
                case "X":
                    cmds.transformLimits(wheel, rotationX=(-wheelRotationLimit,wheelRotationLimit), enableRotationX=(True,True))
                case "Y":
                    cmds.transformLimits(wheel, rotationY=(-wheelRotationLimit,wheelRotationLimit), enableRotationY=(True,True))
                case "Z":
                    cmds.transformLimits(wheel, rotationZ=(-wheelRotationLimit,wheelRotationLimit), enableRotationZ=(True,True))

            cmds.expression(n="steeringEXP#",s=f"{wheel}.rotate{wheelPivotAxis}={steeringObject}.rotate{steeringAxis}*{steeringMultiplier};")

#returns the MEL expression for rotating the wheels based on movement of the control
def wheelExpressionMEL(wheel, wheelRadius, wheelRotationFactor,wheelGrp, locator1, locator2, WheelCTRL):

    wheelExpression = f'''float ${wheel}wheelRadius = {wheelRadius};\n

    // Get positions of locators 1 and 2, and wheel group location
    vector ${wheel}_oldPosition = `xform -q -ws -t "{locator1}"`;\n
    vector ${wheel}_newPosition = `xform -q -ws -t "{wheelGrp}"`;\n
    vector ${wheel}_directionPosition = `xform -q -ws -t "{locator2}"`;\n

    // Find wheel direction
    vector ${wheel}_direction = (${wheel}_directionPosition - ${wheel}_newPosition);\n
    vector ${wheel}_movement = (${wheel}_newPosition - ${wheel}_oldPosition);\n\n

    // Find magnitude of wheel direction
    float ${wheel}_distance = mag(${wheel}_movement);\n
    ${wheel}_dotProduct = dotProduct(${wheel}_movement, ${wheel}_direction, 1);\n

    // Update rotation



    {wheel}.rotateX= {wheel}.rotateX + 360/(6.283*{wheelRadius})*{wheelRotationFactor} * (${wheel}_dotProduct * ${wheel}_distance);\n

    // Move old position locator to new position
    matchTransform {locator1} {wheelGrp};\n

    // Force update in the viewport
    $temp = {WheelCTRL}.translateZ;'''

    return wheelExpression.replace("    ","")

#Global control functions ----------------------------------------------------------------

#Builds global control UI
def globalControlUI():
    global UI_MainLayout
    global UI_globalLayout

    UI_globalLayout = cmds.columnLayout("Global rig", margins=2, parent=UI_MainLayout)

    cmds.text("Select all the controls you want to parent together under a main control for moving the rig.", align="left", wordWrap=True, width=500)
    globalControlUI.UI_globalControlShape = cmds.radioButtonGrp( label="Global control shape:", labelArray2=['Circle', 'Box'], numberOfRadioButtons=2, columnWidth3=[140,50,50], select=2 )


    cmds.rowLayout( numberOfColumns=2, columnWidth2=(140, 75))
    cmds.separator()
    cmds.button(label="Create global control", command="globalControl()")

    cmds.setParent(UI_globalLayout)
    globalAdvancedLayout = cmds.frameLayout(label="Advanced settings", width=500, collapsable=True, collapse=True, annotation="Advanced settings for global controls")
    cmds.text("Set a substring that will be used to parent constrain controls that require movement to control mesh. Example includes wheel rotation controls based on control movement", align="left", wordWrap=True)
    cmds.textFieldGrp(label="Constraint substring:", editable=True, text="WheelCTRL", annotation="Sets a substring to use a parent constrain instead of normal parenting to maintain movement based controls for rig")

#Creates global control
def globalControl():
    selectedControls = cmds.ls(sl=True)

    if not selectedControls:
        cmds.warning("No controls selected!")
        return

    shapeSize = boundingBoxMaxSize(selectedControls) #Get largest dimension to set size of global control

    controlSelect = int(cmds.radioButtonGrp(globalControlUI.UI_globalControlShape, query=True, select=True))

    #Get 2 lists for contraint items, and all others
    constraintControlList, otherControlList = separateSelectedLists(selectedControls, "WheelCTRL")

    #Create global control for circle or box
    match controlSelect:
        case 1:
            globalCTRL = cmds.circle(name="Main_CRTL", normal=(0,1,0), radius=(shapeSize*1.2/2))
            cmds.color(rgbColor=(0,1,0.5))
        case 2:
            globalCTRL = cmds.circle(name="Main_CRTL", normal=(0,1,0), degree=1, radius=(shapeSize*1.2/2), sections=4)
            cmds.color(rgbColor=(0,1,0.5))
            cmds.rotate(0,45,0,globalCTRL)
            cmds.FreezeTransformations()
    
    #Contrain and group existing controls to new group
    parentConstrainObjectsInList(globalCTRL, constraintControlList)
    cmds.parent(otherControlList, globalCTRL)
    cmds.group(globalCTRL, constraintControlList, name="GlobalCTRLgrp")

#Get maximum size of bounding box for a group of selected controls
def boundingBoxMaxSize(selectedControls):
    bbox = cmds.exactWorldBoundingBox(selectedControls)

    xSize = abs(bbox[0] - bbox[3])
    ySize = abs(bbox[1] - bbox[4])
    zSize = abs(bbox[2] - bbox[5])

    if xSize >= ySize and xSize >= zSize:
        return xSize
    elif ySize >= xSize and ySize >= zSize:
        return ySize
    else:
        return zSize

#Accepts list and substring, returns 2 lists, 1st with list items that contain the substring, second list with all other list items
def separateSelectedLists(originalList, substring):
    constraintsList = []
    otherControlList = []

    #check if object containst substring, if yes add to constraints list, otherwise add to otherControlList
    for item in originalList:
        if str(item).find(substring) != -1:
            constraintsList.append(item)
        else:
            otherControlList.append(item)

    return constraintsList, otherControlList

#Takes parent and list of children to parent constrain to an object/control
def parentConstrainObjectsInList(parent, children):
    for child in children:
        cmds.parentConstraint(parent, child, maintainOffset=True)
#End functions -------------------------------------------------------------------
#---------------------------------------------------------------------------------

#script start --------------------------------------------------------------------

#Delete window if already present
if cmds.window(windowHandle, query=True, exists=True):
    cmds.deleteUI(windowHandle)

#Create new window
cmds.window(windowHandle, title="Vehicle Auto Rigger", width=400, height=500, sizeable=False)
UI_MainLayout = cmds.tabLayout()

#Start arm UI --------------------------------------------------------------------
UI_armTab = cmds.columnLayout()
cmds.text("Arm rigger - Allows creation of skeleton and controls for an arm of a construction vehicle in FK or IK setup.", align="left", wordWrap=True, width=500)

#Arm step 1
UI_armStep1 = cmds.frameLayout(label="Step 1: Set joint details", marginHeight=4, marginWidth=4, width=500, backgroundShade=True, backgroundColor=(0.2,0.2,0.2))
numSegments = cmds.intSliderGrp(label="Number of segments", field=True, min=1, max=15, value=3)
UI_jointName = cmds.textFieldGrp(label="Joint name:", text="Arm")
#cmds.columnLayout(adjustableColumn=True)

#Arm step 2
cmds.setParent(UI_armTab)
cmds.columnLayout()
UI_armStep2 = cmds.frameLayout(label="Step 2: Set joint position", marginHeight=4, marginWidth=4, width=500, backgroundShade=True, backgroundColor=(0.2,0.2,0.2))
cmds.button(label="Initialize pieces",annotation="Creates locators to place where you'd like joints to be placed", c="makeLocators()")

#Arm step 3
cmds.setParent(UI_armTab)
UI_IKFIKLayout = cmds.columnLayout(enable=False)
cmds.frameLayout(label="Step 3: Set control type", marginHeight=4, marginWidth=4, width=500, backgroundShade=True, backgroundColor=(0.2,0.2,0.2) )
UI_IKFKSwitch = cmds.optionMenuGrp(label="Control type:", cc="modifyArmUI('IK/FK switch')", annotation="Select inverse kinematic\nor forward kinematic rig")
cmds.menuItem( label='IK', annotation="Inverse kinematic" ) 
cmds.menuItem( label='FK', annotation="Forward kinematic" ) 

UI_IKControls = cmds.columnLayout()
UI_createJoints = cmds.button(label="Create joints", command="createRig(True)")
UI_IKCreateButton = cmds.button(label="Create IK rig", command="createIK()", enable=False)

cmds.setParent("..")
UI_FKControls = cmds.columnLayout( visible=False)
cmds.separator(height=23)
cmds.button(label="Create FK rig", command="createFK()")

#Arm save/restart
cmds.setParent(UI_armTab)
cmds.separator(height=30)
cmds.rowLayout(numberOfChildren=2, numberOfColumns=2, generalSpacing=4, columnWidth2=(200,200), columnAttach2=("both","both"))
cmds.button(label="Restart", annotation="Deletes all the current joints, locators, and controls", command="resetTool()")
UI_saveRig = cmds.button(label="Save rig", annotation="Saves the rig and allows you to create additional joints and controls.\nAvailable after step 3.", command="saveRig()", enable=False)
cmds.setParent("..")
#End Arm UI------------------------------------------------------------------

#Create tread, hydraulic, wheel, and global tab UI
treadUI()
hydraulicUI()
wheelUI()
globalControlUI()

cmds.tabLayout(UI_MainLayout, edit=True, tabLabel=((UI_armTab, "Arm rig"),(UI_treadLayout,"Tread rig"),(UI_hydraulicLayout,"Hydrolic rig"),(UI_wheelLayout,"Wheel rig"),(UI_globalLayout, "Global rig")))

cmds.showWindow()
