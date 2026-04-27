```
ExampleHomeDirectoryForApp:
├── AccessDetails.txt #Store username and password details for each user account
├── app.py #Startup file and entry point for Dash Application
├── ExampleData-MetabolomicsResults.csv #Example of entire metabolomics dataset (tidied up from Mass Profiler annotated output)
├── ExampleData-SamplesAndLabels.csv #For each dataset, have a file with only the sample names and group labels
├── passenger_wsgi.py #Web Server Gateway Interface: Requirement only for deployment via cPanel 
├── ReportDescriptiveText.py #Read by methods scripts as a reference to commonly cited protocol steps
├── ReportFunctions.py #Read by results scripts to access functions to load, normalise, process, and download a user's data
├── requirements.txt #Modules and versions required in your Python environment to run this app
├── assets #Images and external styling files read by app.py
│   ├── EdinOmics_Logo_Transparent.png
│   ├── favicon.ico
│   ├── style.css
│   ├── typography.css
│   └── university-of-edinburgh-logo.png
├── pages
│   ├── ExampleUser_MethodPage.py #Typical layout of a methods report
│   ├── ExampleUser_ResultsPage.py #Typical layout of a results report
│   ├── ExampleUser_UserHomePage.py #Central home page for each user, where users are initially directed to upon logging in to access their reports
│   ├── login.py
│   └── logout.py
└── README_DeployAppInfo.md
```
