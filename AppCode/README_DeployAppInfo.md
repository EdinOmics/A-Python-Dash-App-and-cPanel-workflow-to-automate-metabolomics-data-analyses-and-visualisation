# Structure and details of files required to deploy our Dash App reports
These can be viewed and downloaded from the `ExampleHomeDirectoryForApp` folder

```
ExampleHomeDirectoryForApp:
├── AccessDetails.txt                         #Store username and password details for each user account
├── app.py                                    #Startup file and entry point for Dash Application
├── ExampleData-MetabolomicsResults.csv       #Example of entire metabolomics dataset (tidied up from Mass Profiler annotated output)
├── ExampleData-SamplesAndLabels.csv          #For each dataset, have a file with only the sample names and group labels
├── passenger_wsgi.py                         #Web Server Gateway Interface: Requirement only for deployment via cPanel 
├── ReportDescriptiveText.py                  #Read by methods scripts as a reference to commonly cited protocol steps
├── ReportFunctions.py                        #Read by results scripts to access functions to load, normalise, process, and download a user's data
├── requirements.txt                          #Modules and versions required in your Python environment to run this app
├── assets                                    #Images and external styling files read by app.py
│   ├── EdinOmics_Logo_Transparent.png
│   ├── favicon.ico
│   ├── style.css
│   ├── typography.css
│   └── university-of-edinburgh-logo.png
├── pages
│   ├── ExampleUser_MethodPage.py             #Typical layout of a methods report
│   ├── ExampleUser_ResultsPage.py            #Typical layout of a results report
│   ├── ExampleUser_UserHomePage.py           #Central home page for each user, where users are initially directed to upon logging in to access their reports
│   ├── login.py                              #Home directory in app.py. Initially prompts user to log in to access their data
│   └── logout.py                             #Ensure successful logging out of a profile
└── README_DeployAppInfo.md
```

# Steps to set up and initially deploy this Python Dash App via cPanel
### Note: As some files are overwritten during this process, ensure that you have copies of app.py and passenger_wsgi.py in separate directories before you start these steps. 

1) Set up the home directory for your Dash App within `public_html`
2) Nagivate to the "Setup Python App" option within the "Software" tab
3) Select "CREATE APPLICATION"
4) Set up the app environment with the following settings:
   * Python version = 3.9.19
   * Application root = public_html/ExampleHomeDirectoryForApp
   * Application URL = {leave blank}
   * Startup file = app.py
   * Entry point = app
   * Passenger log file = /home/{user_home_directory}/logs/passenger.log
5) Select "CREATE"
6) Perform initial checks
   * Select "OPEN" to view your app
   * Should have a printed output `It works!` alongside the Python version
   * cPanel automatically creates additional files in our directory and overwrites app.py and passenger_wsgi.py
7) Select "STOP APP"
8) Return to the cPanel File Manager page and refresh it
9) Re-upload your app.py file to overwrite the app.py added in by cPanel
    * View app.py to ensure that your one has successfully overwritten cPanel's app.py
10) Return to the Python app tab
11) In the "Configuration files" section type `requirements.txt` and press the "Enter" key on your keyboard
    * This has uploaded the requirements.txt file
12) Select "Run Pip Install", which will drop down `requirements.txt` as an option to select
13) Select `requirements.txt` and wait until the modules have been successfully installed
    * Sometimes, specifying the module versions in `requirements.txt` can cause error messages to occur at this stage but the modules have still been installed successfully
    * You can navigate to the environment's terminal and use `pip freeze` to check that all the required modules have been installed before progressing
14)  Select "START APP"
15)  Return to the cPanel File Manager page and refresh it
16)  Upload your `passenger_wsgi.py` to overwrite the one put in by cPanel
17)  Return to your Python app tab
18)  Select "RESTART" to restart the app with these changes
19)  Select "OPEN"
     * You should now be able to view your app's home page
     * Interact with the app to make sure that it works properly
       
# Steps to update the Dash App to upload additional users/reports
    
