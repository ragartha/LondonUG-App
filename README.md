# LondonUG-App
Application that generates the shortest path between two stations in the London Underground network. This app is a simple python implementation using basic libraries only. This project was my submission for the System Design and Programming module as part of my course: MSc AI and Data Analytics at Keele University.

#Summary
The LU app designed here is for users who wish to find the shortest path between two stations in the 
London Underground network. This app lets users remove stations out of service and close lines. Line 
and station closure are considered for generating results. The source code for the app is in 
“LU_App.py”. All references are directly cited as comments in the code.


Requirements analysis
The application we are creating is intended for users who wish to travel between stations and need to 
know the fastest route. The functional requirements are:
- Design a simple GUI.
- Allow the user to select a departure and destination from an existing list of stations. 
- Allow the user to indicate that a station is out of service and/or that a line is closed.
- Show results for the fastest route between two stations while only considering the travel time 
between stations.
Constraints
The app is designed in respect to the following guidelines:
- Use modules supported by a simple Python3 installation.
- Implement network graph representation and associated algorithm.
- Extract information from existing files.
- Meet design goals of Flexibility, Extensibility, Maintainability, Robustness, Performance and 
Usability.
- Meet appropriate levels of abstraction, partitioning, decoupling, and maximisation of functional 
cohesion.

