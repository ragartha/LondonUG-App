#importing CSV to open and read csv files
import csv
import sys
import heapq
#default dict allowsUsing list as the default_factory to group a sequence of key-value
#pairs into a dictionary of lists https://docs.python.org/3/library/collections.html#collections.defaultdict
from collections import defaultdict
#tkinter to construct the GUI
import tkinter as tk
from tkinter import *
from tkinter import ttk


#-----Creating a list to store lines and stations out of service, will be used for both the GUI and handling station/line closure
closedstation_list = []
closedline_list = []

#-----Importing lines' names and ids into a dictionary
with open('londonlines.csv') as lines:
    reader = csv.reader(lines)
    headerline = next(reader)
    london_lines_nameID = {int(rows[0]):rows[1] for rows in reader}

#-----Importing stations' names and ids into a dictionary
with open('londonstations.csv') as stations:
    reader = csv.reader(stations)
    headerst = next(reader)
    london_stations_namesid = {int(rows[0]):rows[3] for rows in reader}

#---------Creating the Graphical User Interface, adapted from: Shipman J.,"Tkinter 8.5 reference: a GUI for Python" and practical 4
#  Creating the main window
def main_window(root: Tk): 
    #create frame to place widgets
    frame1 = ttk.Frame(root) 
    frame1.pack(fill = BOTH, expand = True) 
    frame1.bind('<Button-1>', lambda e: frame1.focus()) #bring focus out of button on a click event in the frame
    #Creating widgets
    ttk.Label(frame1, text = "welcome to London Undergroup App!", font = ("Didot", 14,'bold')).pack()
    ttk.Label(frame1, text = "Select an Option:").pack(padx = 5, pady = 5)
    ttk.Button(frame1,width = 20, text  = " \nGet fastest route\n ", command = fastest_route, cursor = 'hand2').pack(padx = 5, pady = 5)
    ttk.Button( frame1, width = 20,  text  = " \nClosed Line\nStation out of service\n ",command = closed_line_station, cursor = 'hand2').pack(padx = 5, pady = 5)
    ttk.Button(frame1, text = "Quit", command = root.quit, cursor = 'hand2').pack(side = RIGHT)

#---------Functions for the buttons----------------------
# 1- Function for the Button Get Fastest Route
def fastest_route(): 
    #Set the widgets we're going to update as global variables
    global to_station
    global from_station
    global errorlabel
    global result
    global label_result
    global total_time

    stvalues = list(sorted(london_stations_namesid.values())) #sort the list alphabetically since the search option is disabled in the combobox
#remove the closed stations from the combobox, since closing a station doesn't affect the lines, this won't affect the network data    
    if closedstation_list:
        for st in closedstation_list:
            stvalues.remove(st)

#Open a new window for generating the route
    route_window = Toplevel(root, bg = '#bfb5b2') 
    route_window.geometry("400x600")
    route_window.title = ("Get Fastest Route")
    route_window.bind('<Button-1>', lambda e: route_window.focus())

#create an empty label for error messages
    errorlabel = ttk.Label(route_window)
    errorlabel.pack()
    #Widgets:
    ttk.Label(route_window, text = "Select starting station:").pack(padx = 5, pady = 5)
    from_station = ttk.Combobox(route_window, state = "readonly",values = stvalues) 
    from_station.bind("<<ComboboxSelected>>",lambda e: route_window.focus()) #Remove the focus from the combobox
    from_station.current(0) # show the first option in the box (it shows Acton Town)
    from_station.pack(padx = 5, pady = 5)

    ttk.Label(route_window, text = "Select destination:").pack(padx = 5, pady = 5)

    to_station = ttk.Combobox(route_window, state = "readonly", values = stvalues)
    to_station.bind("<<ComboboxSelected>>",lambda e: route_window.focus())  
    to_station.current(0)
    to_station.pack(padx = 5, pady = 5)

    ttk.Button(route_window, text = " \nGet route\n ", command = fastest_route_dijkstra_button, cursor  = 'hand2').pack(padx = 5, pady = 5)

    label_result = ttk.Label(route_window)
    label_result.pack(padx = 5, pady = 5)

    result = tk.Message(route_window,font = ('corbel', 12,'bold', 'italic'), width = 300, background = "white")
    result.pack(padx = 5, pady = 5)
    total_time= ttk.Label(route_window, font=('corbel', 12,'bold', 'italic'))
    total_time.pack()

    #disable the first window to avoid errors and fixating the window size
    route_window.grab_set()
    route_window.resizable(False, False) 

#---Function for the Button Get Route
def fastest_route_dijkstra_button():
    #Empty the message box
    result.config(text = '')
    total_time.config(text = '')
    #Get the departure and destination:
    departure_name = from_station.get()
    destination_name = to_station.get()
    departure = get_key_from_value(london_stations_namesid , departure_name )
    destination = get_key_from_value(london_stations_namesid , destination_name )
    #Error handling: match destination and departure names:
    if departure_name  ==  destination_name:
        errorlabel.config(text = "Error! Departure and destination are identitcal", font = ('corbel',14,'bold'), foreground = '#5e3c58')
        result.config(text = "")
        label_result.config(text = '')

    else:
    #Return the shortest path as the message box:
        label_result.config(text = 'Shortest path between the selected stations is:')
        errorlabel.config(text = "")
        try:
            path, travel = pathfromdeptodest(departure, destination)
            result.config(text =  ' > '.join([london_stations_namesid[int(i)] for i in path]))
            total_time.config(text = ' '.join(['Total travel time is:', str(travel), 'minutes']))
        except:
    #Handle the error where path does not exist:
            label_result.config(text = '')
            result.config(text = "There is no possible route due to line closure")
            total_time.config(text = '')
# 2- Function for the button "Closed lines/station out of service"
def closed_line_station():
    global openstations
    global closedstation
    global openlines
    global closedlines
    global this_window

#create an editable copy of stations names and lines for the listboxes to save changes made by the user
    station_list = list(sorted(london_stations_namesid.values()))
    lines_list = list(sorted(london_lines_nameID.values()))

#Update the lists of values for the listbox widgets
    if closedstation_list:
        for st in closedstation_list:
            station_list.remove(st)

    if closedline_list:
        for li in closedline_list:
            lines_list.remove(li)
#Create a new window
    this_window = Toplevel(root)
    this_window.geometry("440x570")
    this_window.title("Closed line/Station out of service")
    this_window.configure(bg  = '#bfb5b2')
    this_window.bind('<Button-1>', lambda e: this_window.focus())
#Create widgets
    info_label = ttk.Label(this_window, text = 'Please select a line or station to change its status', font = ('corbel',10,'bold','italic'))
    info_label.pack()
    info_label.place(x = 10, y = 10)
    #Listbox widgets for open and closed stations
    openstationlabel = ttk.Label(this_window, text = 'Open Stations:')
    openstationlabel.pack()
    openstationlabel.place(x = 10,y = 30)
    openstations = tk.Listbox(this_window, listvariable = StringVar(value = station_list), height = 10, width = 30, selectmode = 'single', background = '#c7bbc9' )
    openstations.pack()
    openstations.place(x = 10,y = 50)

    changestatus = ttk.Button(this_window, text = '\nChange status of station or line\n' , command = change_status, cursor = 'hand2')
    changestatus.pack()
    changestatus.place(x = 130, y = 229)

    closedstationlabel = ttk.Label(this_window, text = 'Closed Stations:')
    closedstationlabel.pack()
    closedstationlabel.place(x = 10, y = 290)
    closedstation = tk.Listbox(this_window ,listvariable = StringVar(value = closedstation_list), height = 10, width = 30, selectmode = 'single',background = '#c7bbc9')
    closedstation.pack()
    closedstation.place(x = 10, y = 310)

    #Listbox widgets for open and closed lines
    openlineslabel = ttk.Label(this_window, text = 'Open Lines:')
    openlineslabel.pack()
    openlineslabel.place(x = 280,y = 30)
    openlines = tk.Listbox(this_window, listvariable =  StringVar(value = lines_list), height = 10, width = 30, selectmode = 'single',background = '#c7bbc9')
    openlines.pack()
    openlines.place(x = 250, y = 50)
    closedlineslabel = ttk.Label(this_window, text = 'Closed Lines:')
    closedlineslabel.pack()
    closedlineslabel.place(x = 280, y = 290)
    closedlines = tk.Listbox(this_window, height = 10,width = 30,listvariable = StringVar(value = closedline_list), selectmode = 'single',background = '#c7bbc9')
    closedlines.pack()
    closedlines.place(x = 250, y = 310)
    savechanges = ttk.Button(this_window, text = "\nSave changes\n", command =  this_window.destroy, cursor = 'hand2')
    savechanges.pack()
    savechanges.place(x = 300, y = 500)
    this_window.resizable(False, False)
    this_window.grab_set()

#----- Function for the button: Change status of station or line
def change_status():
# Depending on the selected item in open/closed lines or stations, move the item to the opposite side
    if (openstations.curselection()):
        station = changeStationStatus(openstations, closedstation)
        closedstation_list.append(station)
    if (closedstation.curselection()):
        station = changeStationStatus(closedstation, openstations)
        closedstation_list.remove(station)
    if (openlines.curselection()):
        station = changeStationStatus(openlines, closedlines)
        closedline_list.append(station)
    if (closedlines.curselection()):
        station = changeStationStatus(closedlines, openlines)
        closedline_list.remove(station)   

#---Function to change the status of selected item # adapted from 
def changeStationStatus(original_box, Next_box):
    index = original_box.curselection()[0]
    selected_item = original_box.get(index)
    temp_items = list(Next_box.get(0, tk.END))
    temp_items.append(selected_item)
    temp_items.sort()
    Next_box.delete(0, tk.END)

    for item in temp_items:
        Next_box.insert(tk.END, item)
    original_box.delete(index)

    return selected_item
#---Function to get stations and lines ids from dictionaries using names
def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v  ==  val]
    if keys:
        return keys[0]
    return None

 #------construct the network using two classes: Vertex for stations and Graph for the network, adapted from Practical 4
class Vertex:
    def __init__(self, ident):
        self.ident = ident
        self.adjacent = defaultdict(list)  # Adjacency list
        self.distance = sys.maxsize #set the distance to infinity 
        self.visited = False # mark all nodes uvisited
        self.previous = None
        self.lin = set()

    def __str__(self): # used to test the code
        return str(self.ident) + ' adjacent: ' + str([x.ident for x in self.adjacent]) 

    def addNeighbour(self, neighbour, l, weight=0): #adding adjacent stations
        self.lin.add(l)
        self.adjacent.update({neighbour: [weight, self.lin]}) # store weight and all available lines in a connection
        

    def getConnections(self): # return adjacent stations
        return self.adjacent.keys()

    def getId(self): # return station id
        return self.ident

    def get_weight(self, neighbour): #return travel time between vertex and a neighbour
        return self.adjacent[neighbour][0]

    def get_lines(self, neighbour): #return a station's lines 
        return self.adjacent[neighbour][1]
    
    def remove_line(self,l): #delete a closed line
        self.lin.remove(l)

    def set_distance(self, dist): #set current total weight of the smallest weight path from the start to the vertex
        self.distance = dist

    def get_distance(self): #return distance
        return self.distance

    def set_previous(self, prev): #set predecessor
        self.previous = prev

    def set_visited(self): #set visited state
        self.visited = True

class graph:
    def __init__(self):
        self.vertDict = {}
        self.numVertices = 0

    def __iter__(self): #used to test the code
        return iter(self.vertDict.values())

    def addVertex(self, id): #add a vertex as an object of Vertex
        self.numVertices += 1
        newVertex = Vertex(id)
        self.vertDict[id] = newVertex
        return newVertex

    def getVertex(self, n): #return vertex object
        if n in self.vertDict:
            return self.vertDict[n]
        else:
            return None

    def getVertices(self): #return all vertices
        return self.vertDict.keys()

    def addEdge(self, frm, to, l, cost=0): #add a new edge to the graph
        if frm not in self.vertDict:
            self.addVertex(frm)
        if to not in self.vertDict:
            self.addVertex(to)
        self.vertDict[frm].addNeighbour(self.vertDict[to], l, cost)
        self.vertDict[to].addNeighbour(self.vertDict[frm], l, cost)

    def set_previous(self, current):  #set state to previous
        self.previous = current

#-- The next two functions to calculate the shortest path are inspired from: K Hong, DIJKSTRA'S SHORTEST PATH ALGORITHM available on: https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php

#---Function to return the shortest path using the destination, allows to gather predecessors starting from the target node
def shortest_path_function(v, path):

    if v.previous:
        path.append(v.previous.getId())
        shortest_path_function(v.previous, path)
    return

# Dijkstra function calculates the shortest path
def dijkstra(aGraph, start, target):
    # Set the distance for the start node to zero 
    start.set_distance(0)
    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(),v.getId()) for v in aGraph]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # pop vertex with the smallest distance
        uv = heapq.heappop(unvisited_queue)
        current = aGraph.getVertex(uv[1])
        current.set_visited()

        #for next in v.adjacent:
        for next in current.adjacent:
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + current.get_weight(next)
            
            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)

        # Rebuild heap
        # Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v.getId()) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)


def pathfromdeptodest(departure, destination):
    #  adding network data from londonconnections file to the graph while considering line closure
    network = graph()
    with open("londonconnections.csv") as connect:
        reader = csv.reader(connect)
        header= next(reader)
        for row in reader:
            a = int(row[0])
            b = int(row[1])
            line = int(row[2])
            c = int(row[3])

            #If a line is closed, don't add the edge to the graph
            if closedline_list:
                l_id = [int(get_key_from_value(london_lines_nameID, l)) for l in closedline_list]
                if line  not in  l_id:
                    network.addEdge(a,b,line,c)
            else:
                network.addEdge(a,b,line,c)

    dijkstra(network, network.getVertex(departure), network.getVertex(destination)) #calculate the shortest path from departure to destinstion

    target = network.getVertex(destination) #set the target to destination

    path = [target.getId()] #intitialise the path list with target

    travel_time = target.get_distance() #get the travel time to target

    shortest_path_function(target, path) #get the shortest path to target

    shortest_path = path[::-1]

    return shortest_path, travel_time

#----Launching the app and set theme
root = Tk() 
root.title("London UnderGround App")
root.geometry("400x250+300+300")
s = ttk.Style(root)
s.theme_use('clam')
s.configure('TFrame', background = '#bfb5b2')
s.configure('TButton',foreground = '#83adb5',font = ('Didot',9,'bold'), background = '#2e4045')
s.configure('TLabel',foreground = '#2e4045', background = '#bfb5b2')
s.configure('TCombobox',foreground = '#2e4045', background = '#c7bbc9')
root.resizable(False, False)
main_window(root) 
root.mainloop()
