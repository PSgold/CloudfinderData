import requests
from datetime import datetime

#Global definitions
postURL = "https://api.cloudfinder.com/j_spring_security_check"
providerURL = "https://api.cloudfinder.com/api/organization/providers/"

#function to take cloudfinder creds and return the raw account/user data (also returns provider list array dict)
def getCdfrData(creds):
    authResponse = ""
    with requests.Session() as session:
        authResponse = session.post(postURL,data=creds)
        if authResponse.ok == True:
            print("\nSuccessfully Authenticated\n")
            providerList=[]
            cdfrDataList=[]
            providerData = session.get(providerURL)
            if providerData.ok == False:
                return -2
            print("Successfully received Provider Data\nCreating provider object array")
            for provider in providerData.json()["providers"]:
                if "_links" in provider.keys():
                    providerDict = {
                        "providerId":provider["providerId"],
                        "providerConfigId":provider["providerConfigId"],
                        "numberOfSelectedUsers":provider["numberOfSelectedUsers"]
                    }
                    providerList.append(providerDict)
            print("Successfully created provider object array\nCreating data array")
            
            for provider in providerList:
                dataURL = providerURL+provider["providerId"]+"/"+provider["providerConfigId"]+"/containers/?pageSize=500&"
                cdfrData = session.get(dataURL)
                cdfrDataList.append(cdfrData)
            print("Successfully created data array")
            return 1,providerList,cdfrDataList
        else:
            return -1

#function to filter for requested data and write said data to csv file
def processCdfrData(cdfrDataList,providerList):
    print("Processing data array and creating csv")
    reportName = providerList[0]["providerConfigId"]+"_CDFRreport_"
    dateTime = datetime.strftime(datetime.today(),"%d.%m.%Y_%H_%M")
    reportName+=dateTime
    reportName+=".csv"
    report = open(reportName,"w")
    report.write(providerList[0]["providerConfigId"])
    report.write("\n")
    report.write("Provider,Name,Description,Status,Provider_licensed,,,TotalProviderSelectedUsers\n")
    cdfdrDListIndex = 0
    for provider in providerList:
        report.write(provider["providerId"]+",,,,,,,"+str(provider["numberOfSelectedUsers"])+"\n")
        for user in (((cdfrDataList[cdfdrDListIndex].json())["containers"])):
            if user["shouldScan"]==True:
                report.write(
                    ","+
                    user["name"]+","+
                    user["description"]+","+
                    user["status"]+","+
                    str(user["licensed"])+"\n"
                )
        cdfdrDListIndex+=1
        report.write("\n")
    report.close()
    print("Successfully created csv report")
    input("\nPress enter to exit: ")


#Start of execution
creds = {"j_username":"","j_password":""}
creds["j_username"] = input("Please type the username: ")
creds["j_password"] = input("Please type the password: ")
returnCode, providerList,cdfrDataList = getCdfrData(creds)
if returnCode==1:
    processCdfrData(cdfrDataList,providerList)
elif returnCode==-1:
    print("\nFailed to authenticate!\n")
elif returnCode==-2:
    print("\nFailed to receive Provider data!\n")