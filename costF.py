import win32com.client as win32
import csv
import os
import numpy as np


def costF(parameters):

    DS1, LFe, PW, N = parameters

    # Rounding
    def rounding(x, base):
        return base * round(x/base)

    DS1 = rounding(DS1, 5)
    LFe = rounding(LFe, 5)
    PW = round(PW)
    N = round(N)

    # Filling factor penalty
    ## 333.84 = clear slot area
    ## 0.692 = wire radius with insulation
    fillFact = PW * 3.14159 * 0.692**2 * N / 333.84
    if fillFact > 0.85:
        return 100.0

    DS1str = str(DS1) + "mm"
    LFEstr = str(LFe) + "mm"
    PWstr = str(PW)
    Nstr = str(N)

    oAnsoftApp = win32.Dispatch("Ansoft.ElectronicsDesktop")
    oDesktop = oAnsoftApp.GetAppDesktop()
    oDesktop.RestoreWindow()

    path = os.getcwd()

    try:
        oProject = oDesktop.SetActiveProject("Test")
    except:
        oDesktop.OpenProject(path+"\Test.aedt")
    oProject = oDesktop.SetActiveProject("Test")
    oDesign = oProject.SetActiveDesign("RMxprtDesign1")


    oProject.ChangeProperty(["NAME:AllTabs",["NAME:ProjectVariableTab",
            ["NAME:PropServers", "ProjectVariables"], ["NAME:ChangedProps",
            ["NAME:$DS1", "Value:=", DS1str]]]])

    oProject.ChangeProperty(["NAME:AllTabs",["NAME:ProjectVariableTab",
            ["NAME:PropServers", "ProjectVariables"], ["NAME:ChangedProps",
            ["NAME:$LFE", "Value:=", LFEstr]]]])

    oProject.ChangeProperty(["NAME:AllTabs",["NAME:ProjectVariableTab",
            ["NAME:PropServers", "ProjectVariables"], ["NAME:ChangedProps",
            ["NAME:$PW", "Value:=", PWstr]]]])

    oProject.ChangeProperty(["NAME:AllTabs",["NAME:ProjectVariableTab",
            ["NAME:PropServers", "ProjectVariables"], ["NAME:ChangedProps",
            ["NAME:$N", "Value:=", Nstr]]]])


    # Analyze
    oDesign.Analyze("Setup1")

    # Export results to Results.csv
    oModule = oDesign.GetModule("ReportSetup")
    filename = "temp"


    pars = [
        "$DS1:="		, [DS1str],
        "$LFE:="	    , [LFEstr],
        "$PW:="		    , [PWstr],
        "$N:="		    , [Nstr]
    ]


    oModule.CreateReport(filename, "RMxprt", "Data Table", "Setup1 : Performance",
    	["Domain:=", "Parameter"],
        pars,
    	["X Component:=", "$DS1",
        "Y Component:=", ["EfficiencyParameter"]
    	])
    oModule.AddTraces(filename, "Setup1 : Performance",
    	["Domain:=", "Parameter"],
    	pars,
    	["X Component:=", "$DS1",
        "Y Component:=", ["PowerFactorParameter"]
    	])


    oModule.ExportToFile(filename, path+"/"+filename+".csv")
    oModule.DeleteAllReports()

    eff = np.genfromtxt(filename+".csv", delimiter=",", skip_header=1)[1]
    pf = np.genfromtxt(filename+".csv", delimiter=",", skip_header=1)[2]

    os.remove(filename+".csv")

    #oAnsoftApp.Quit()

    # Price calculation
    sheetPrice = 0.08 * DS1 - 22
    ## specific weight of 1.25 wire = 11.006kg/km
    wirePrice = 0.005503 * 0.150
    ## 2*LFe because sheet thickness is 0.5mm
    ## number of stator slots = 48
    price = ( PW * N * wirePrice * 48 + sheetPrice ) * 2 * LFe
    ## price conversion to <0,1> via custom function
    #prc = -2e-20*price**5 + 4e-16*price**4 - 2e-12*price**3 + 7e-9*price**2 - 5e-6*price - 7e-4
    threshold = 11500
    if price < threshold:
        prc = 0
    else:
        prc = 1.15**((price-threshold)*1e-3)**2 - 1

    # Efficiency to <0,1>
    eff = float(eff)/100

    # Cost value calculation
    cost = 3*(1-eff) + (1-pf) + prc

    return cost
