import mysql.connector
import Tkinter as tk
import ttk
import sqlite3 as sl
from drones import Drone, DroneStore
from operators import Operator, OperatorStore
from maps import Map, MapStore
from trackingsystem import TrackingSystem, DroneLocation


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)
        self.maps = MapStore(conn)
        self.tracking = TrackingSystem()

        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        map_button = tk.Button(
            frame, text="View Map", command=self.view_maps, width=40, padx=5, pady=5)
        map_button.pack(side=tk.TOP)
        map_button = tk.Button(
            frame, text="Allocate Drone", command=self.view_allocate, width=40, padx=5, pady=5)
        map_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def view_operators(self):
        """ Display the operators. """
        # Instantiate the operators window
        # Display the window and wait
        #print 'TODO operators'
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)

    def view_maps(self):
        wnd = MapListWindow(self)
        self.root.wait_window(wnd.root)

    def view_allocate(self):
        wnd = AllocateEditorWindow(self)
        self.root.wait_window(wnd.root)


class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.maps = parent.maps
        self.tracking = parent.tracking

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('Id', 'Name', 'Class', 'Rescue', 'Operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        #print 'TODO: Load data'
        self.tree.delete(*self.tree.get_children())
        data = self.drones.list_all()
        for d in data:
            op_name = d.operator.first_name + ' ' + d.operator.last_name
            values = (d.id, d.name, 'One' if d.class_type == 1 else 'Two', 'Yes' if d.rescue else 'No', op_name) 
            self.tree.insert('', 'end', values=values)
                    
        # The following is a dummy record - need to remove and replace with data from the store
        #self.tree.insert('', 'end', values=(1, 'Test', 1, 'No', '<None>'))


    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        #print 'TODO: Start a new drone'
        drone = Drone('')
        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.add(drone)
        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        #print 'TODO: Load drone with ID %04d' % (item_id)
        drone = self.drones.get(item_id)

        # Display the drone
        self.view_drone(drone, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.save(drone)
        self.populate_data()

    def view_drone(self, drone, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action)
        self.root.wait_window(wnd.root)

class OperatorListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Operators')

        # Add the list and fill it with data
        columns = ('Name', 'Class', 'Rescue', 'Operations', 'Drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        #print 'TODO: Load data'
        self.tree.delete(*self.tree.get_children())
        data = self.operators.list_all()
        for o in data:
            op_name = o.first_name + ' ' + o.last_name
            values = (op_name, 'One' if o.drone_license == 1 else 'Two', 'Yes' if o.rescue_endorsement else 'No', o.operations, o.drone) 
            self.tree.insert('', 'end', values=values)
                    
        # The following is a dummy record - need to remove and replace with data from the store
        #self.tree.insert('', 'end', values=(1, 'Test', 1, 'No', '<None>'))

    def add_operator(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        #print 'TODO: Start a new drone'
        op = Operator()
        # Display the drone
        self.view_operator(op, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the drone in the store and updates the list. """
        self.operators._add(operator)
        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        full_name = item_id.strip().split()
        if len(full_name) == 1:
            fn = full_name[0].strip()
            operator = self.operators.get(first_n=fn)
            self.view_operator(operator, self._update_operator)
        else:
            fn = full_name[0].strip()
            ln = full_name[1].strip()
            operator = self.operators.get(first_n = fn, last_n = ln)
            self.view_operator(operator, self._update_operator)
        #print 'TODO: Load drone with ID %04d' % (operator.id)

        # Display the drone
        #self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the drone. """
        self.operators.save(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the drone editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)

class MapListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(MapListWindow, self).__init__(parent, 'Map Viewer')
        self._c = tk.Canvas(self.frame, bd=0, width=800, height = 400, relief= tk.SUNKEN)
        self._c.grid(row = 1, column = 0)
        self._shapes = []
        self._coordinates = {}


        # Add the list and fill it with data
        self.populate_data()

        # Add the command buttons
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=4, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Refresh",
                                command=self.refresh, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=5, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        data = self.maps.list_all()
        self._c.mapbox = ttk.Combobox(self.frame)
        self._temp = {}
        name = []
        for d in data:
            self._temp[d.name] = d.filepath
            name += [d.name]
        tk.Label(self.frame, text= 'Map:').grid(row=0,column=0, sticky="W")
        self._c.mapbox['values'] = self._temp.keys()
        self._c.mapbox.current(0)
        curr_img = self._c.mapbox.get()
        self._c.mapbox.place(x=40, y=0, width = 400)        
        curr_filename = self._temp[self._c.mapbox.get()]
        xscrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        xscrollbar.grid(row=2, column=0, sticky=tk.E+tk.W)
        yscrollbar = tk.Scrollbar(self.frame)
        yscrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
        self._c.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        self._c.img = tk.PhotoImage(file=curr_filename)
        self._c.create_image(0,0,image=self._c.img, anchor="nw")
        xscrollbar.config(command=self._c.xview)
        yscrollbar.config(command=self._c.yview)
        self._c.config(scrollregion=self._c.bbox(tk.ALL))
        self._c.mapbox.bind("<<ComboboxSelected>>", self.display_map)
        self.retrieve_map()

    def display_map(self,eventObject):
        curr_img = self._c.mapbox.get()
        curr_filename = self._temp[self._c.mapbox.get()]
        xscrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        xscrollbar.config(command=self._c.xview)
        xscrollbar.grid(row=2, column=0, sticky=tk.E+tk.W)
        yscrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        yscrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
        yscrollbar.config(command=self._c.yview)
        self._c.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        self._c.img = tk.PhotoImage(file=curr_filename)
        self._c.create_image(0,0,image=self._c.img, anchor="nw")
        self.retrieve_map()
        self._c.config(scrollregion=(0,0, self._c.img.width(), self._c.img.height()))

    def retrieve_map(self):
        for drone in self.drones.list_maps():
            a_map = self.tracking.retrieve(drone.map.name, drone)
            if a_map.is_valid():
                #print drone.name
                pos = a_map.position()
                x_co, y_co = a_map._x, a_map._y
                #print x_co, y_co
                self._coordinates[drone.name] = [x_co, y_co]
                if drone.map.name == self._c.mapbox.get():
                    #self._dimensions = [x_co *(self._c.img.width()/100), y_co * (self._c.img.height()/100), (x_co *(self._c.img.width()/100)) + 10, (y_co * (self._c.img.height()/100)) + 10]
                    if drone.rescue == True:
                        #print x_co, y_co
                        self._d = self._d = self._c.create_oval((x_co *(self._c.img.width()/100)) - 5, (y_co * (self._c.img.height()/100)) - 5, (x_co *(self._c.img.width()/100)) + 15, (y_co * (self._c.img.height()/100)) + 15, fill='Blue')
                        #self._d = self._c.create_oval(x_co *(self._c.img.width()/100), y_co * (self._c.img.height()/100), (x_co *(self._c.img.width()/100)) + 10, (y_co * (self._c.img.height()/100)) + 10, fill='Red')
                        self._shapes += [self._d]
                    else:
                        #print x_co, y_co, 'not rescue'
                        self._d = self._c.create_oval((x_co *(self._c.img.width()/100)) - 5, (y_co * (self._c.img.height()/100)) - 5, (x_co *(self._c.img.width()/100)) + 15, (y_co * (self._c.img.height()/100)) + 15, fill='Red')
                        self._shapes += [self._d]
                        #self._d = self._c.create_oval(x_co *(self._c.img.width()/100), y_co * (self._c.img.height()/100), (x_co *(self._c.img.width()/100)) + 10, (y_co * (self._c.img.height()/100)) + 10, fill='Black')
                    
        

    def refresh(self):
        for i in self._shapes:
            self._c.delete(i)
        self.retrieve_map()      


class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, dr_or_op, save_action):
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()
        self._drone = dr_or_op
        self._op = dr_or_op
        self._map = dr_or_op

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        last_row = self.add_editor_widgets(dr_or_op)

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=last_row + 1, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=last_row + 2, column=1, sticky=tk.E)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action):
        # TODO: Add either the drone name or <new> in the window title, depending on whether this is a new
        # drone or not
        self.tracking = parent.tracking
        super(DroneEditorWindow, self).__init__(parent, 'Drone: ', drone, self.save_drone)
        #self._drone = drone
        self._save_action = save_action
        #last_row = self.add_editor_widgets()

        # TODO: Load drone details

    def add_editor_widgets(self,drone):
        tk.Label(self.frame, text = 'Name:').grid(row=0, sticky="W")
        tk.Label(self.frame, text = 'Drone Class:').grid(row=1, sticky="W")
        tk.Label(self.frame, text  = 'Rescue Drone:').grid(row=2, sticky="W")
        self._name = tk.Entry(self.frame, width=40)
        self._name.grid(row=0, column=1)
        self._class_t = ttk.Combobox(self.frame)
        self._class_t['values'] = ('One', 'Two')
        self._class_t.current(0)
        self._resc = ttk.Combobox(self.frame)
        self._resc['values'] = ('Yes', 'No')
        self._resc.current(1)
        self._class_t.grid(row=1, column=1, sticky="W")
        self._resc.grid(row=2, column=1, sticky="W")
        self._name.insert(tk.INSERT, "")
        tk.Label(self.frame, text= 'Location').grid(row=3, sticky="W")
        self._loc = tk.Entry(self.frame, width=10)
        self._loc.insert(tk.INSERT,'n/a')
        self._loc.config(state='readonly')
        self._loc.grid(row=3, column=1, sticky="W")
        if drone.name is not '':
            self._name.insert(tk.INSERT, drone.name)
            self._class_t.current(0 if drone.class_type == 1 else 1)
            self._resc.current(0 if drone.rescue else 1)
            if drone.map is not None:
                a_map = self.tracking.retrieve(drone.map, drone)
                if a_map.is_valid():
                    pos = a_map.position()
                    #print pos
                    self._loc = tk.Entry(self.frame, width=10)
                    to_insert = '(', a_map._x, ',', a_map._y, ')'
                    self._loc.insert(tk.INSERT,to_insert)
                    self._loc.config(state='readonly')
                    self._loc.grid(row=3, column=1, sticky="W")
                else:
                    self._loc = tk.Entry(self.frame, width=10)
                    self._loc.insert(tk.INSERT,'n/a')
                    self._loc.config(state='readonly')
                    self._loc.grid(row=3, column=1, sticky="W")
            else:
                self._loc = tk.Entry(self.frame, width=10)
                self._loc.insert(tk.INSERT,'n/a')
                self._loc.config(state='readonly')
                self._loc.grid(row=3, column=1, sticky="W")
        #return 2
        """ Adds the widgets dor editing a drone. """
        #print 'TODO: Create widgets and populate them with data'
        return 2

    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        #print 'TODO: Update the drone from the widgets'
        self._drone.name = self._name.get()
        self._drone.class_type =  1 if self._class_t.get() == 'One' else 2
        self._drone.rescue = 1 if self._resc.get() == 'Yes' else 0
        self._save_action(self._drone)
        self.close()


class OperatorEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, operator, save_action):
        # TODO: Add either the drone name or <new> in the window title, depending on whether this is a new
        # drone or not
        super(OperatorEditorWindow, self).__init__(parent, 'Operator: ', operator, self.save_operator)
        #self._op = operator
        op = operator
        self._save_action = save_action
        #last_row = self.add_editor_widgets()

        # TODO: Load drone details

    def add_editor_widgets(self,operator):
        tk.Label(self.frame, text = 'First Name:').grid(row=0, sticky="W")
        tk.Label(self.frame, text = 'Last Name:').grid(row=1, sticky="W")
        tk.Label(self.frame, text = 'Drone License:').grid(row=2, sticky="W")
        tk.Label(self.frame, text  = 'Rescue Endorsement:').grid(row=4, sticky="W")
        tk.Label(self.frame, text  = 'Number of Operations:').grid(row=5, sticky="W")
        self._firstname = tk.Entry(self.frame, width=40)
        self._lastname = tk.Entry(self.frame, width=40)
        self._firstname.grid(row=0, column=1)
        self._lastname.grid(row=1, column=1)
        self._drone_l = ttk.Combobox(self.frame)
        self._drone_l['values'] = ('One', 'Two')
        self._drone_l.current(0)
        self._drone_l.grid(row=2, column=1, sticky="W")
        self._operations = None
        self._resc = None
        if operator.first_name is not None:
            self._firstname.insert(tk.INSERT, operator.first_name)
            self._lastname.insert(tk.INSERT, operator.last_name)
            self._drone_l.current(0 if operator.drone_license == 1 else 1)
            no_of_operations = tk.StringVar()
            no_of_operations.set(operator.operations)
            self._operations = tk.Spinbox(self.frame, from_=0, to = 100, textvariable=no_of_operations)
            self._operations.grid(row=5, column = 1, sticky= "W")
            if operator.rescue_endorsement:
                self._resc = tk.Entry(self.frame, width=10,)
                self._resc.insert(tk.INSERT,'Yes')
                self._resc.config(state='readonly')
                self._resc.grid(row=4, column=1, sticky="W")
            else:
                self._resc = tk.Entry(self.frame, width=10)
                self._resc.insert(tk.INSERT,'No')
                self._resc.config(state='readonly')
                self._resc.grid(row=4, column=1, sticky="W")
        else:
            self._operations = tk.Spinbox(self.frame, from_=0, to = 100)
            self._operations.grid(row=5, column = 1, sticky= "W")
            self._resc = tk.Entry(self.frame, width=20)
            self._resc.insert(tk.INSERT, 'No')
            self._resc.config(state='readonly')
            self._resc.grid(row=4, column=1, sticky="W")
        #return 2
        """ Adds the widgets dor editing a drone. """
        return 10

    def save_operator(self):
        """ Updates the drone details and calls the save action. """
        #print 'TODO: Update the drone from the widgets'
        self._op.first_name = self._firstname.get()
        self._op.last_name = self._lastname.get()
        self._op.drone_license =  1 if self._drone_l.get() == 'One' else 2
        self._op.operations = int(self._operations.get())
        self._op.rescue_endorsement = 1 if self._op.operations >= 5 else 0        
        self._save_action(self._op)
        self.close()

class AllocateEditorWindow:
    """ Editor window for drones. """

    def __init__(self, parent):
        # TODO: Add either the drone name or <new> in the window title, depending on whether this is a new
        # drone or not
        self.drones = parent.drones
        self.operators = parent.operators
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title('Allocate Drone:')
        self.root.transient(parent.root)
        self.root.grab_set()
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Check",
                               command=self.check_action, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=4, column=1, sticky = tk.W)
        #add_button.place(in_= self.frame, x = 204, y = 45)
        allocate_button = tk.Button(self.frame, text="Allocate",
                                command=self.allocate, width=20, padx=5, pady=5)
        allocate_button.grid(in_=self.frame, row=5, column=1)
        exit_button = tk.Button(self.frame, text="Cancel",
                                command=self.cancel, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=6, column=1)
        self._check_clicked = False
        self._allocate_clicked = False
        #super(AllocateEditorWindow, self).__init__(parent, 'Allocate Drone: ', None, self.allocate_drone)
        #self._op = operator
        #op = operator
        #self._save_action = save_action
        #last_row = self.add_editor_widgets()

        # TODO: Load drone details

    def add_editor_widgets(self):
        tk.Label(self.frame, text = 'Drone:').grid(row=0, sticky="W")
        tk.Label(self.frame, text = 'Operator:').grid(row=1, sticky="W")
        drones = self.drones.list_all()
        operators = self.operators.list_all()
        temp_d = []
        temp_o = []
        for d in drones:
            temp_d += [str(d.id) + ': ' + d.name]
        for o in operators:
            temp_o += [o.first_name + ' ' + str(o.last_name)]
        self._drones = ttk.Combobox(self.frame)
        self._drones['values'] = temp_d
        self._drones.current(0)
        #self._drones.grid(row = 0, column = 1, sticky = tk.W)
        self._drones.place(x=60, y = 0, width = 200)
        self._ops = ttk.Combobox(self.frame)
        self._ops['values'] = temp_o
        self._ops.current(0)
        self._ops.place(x=60, y = 20, width = 200)
        self._errors = tk.Text(self.frame, width=50, height=10)
        self._errors.insert(tk.INSERT,'Error Messages')
        self._errors.config(state='disabled')
        self._errors.grid(row=3, column=0, sticky="W")
        return 0

    def check_action(self):
        curr_op_name = self._ops.get()
        full_name = curr_op_name.strip().split()
        if len(full_name) == 1:
            fn = full_name[0].strip()
            operator = self.operators.get(first_n=fn)
        else:
            fn = full_name[0].strip()
            ln = full_name[1].strip()
            operator = self.operators.get(first_n = fn, last_n = ln)
        curr_dr = self._drones.get()
        curr_dr = curr_dr.strip().split()
        curr_id = curr_dr[0].split(":")
        curr_id_id = curr_id[0]
        drone = self.drones.get(curr_id_id)
        self._allocate_mess = self.drones.allocate(drone, operator)
        if len(self._allocate_mess.messages) >= 1:
            self._errors.config(state='normal')
            self._errors.delete('1.0', tk.END)
            self._errors.insert(tk.INSERT,'Error Messages\n')
            for i in self._allocate_mess.messages:
                error = i + '\n'
                self._errors.insert(tk.INSERT, error)
            self._errors.config(state='disabled')
        else:
            self._errors.config(state='normal')
            self._errors.delete('1.0', tk.END)
            self._errors.insert(tk.INSERT, 'No Error Messages')
            self._errors.config(state='disabled')
        self._check_clicked = True
            

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

    def allocate(self):
        if self._check_clicked == False:
            self._errors.config(state='normal')
            self._errors.delete('1.0', tk.END)
            self._errors.insert(tk.INSERT, 'The allocation has not been checked')
            self._errors.config(state='disabled')
        else:
            self._allocate_mess.commit()
            self._check_clicked = False
            self.close()

    def cancel(self):
        self.close()



if __name__ == '__main__':
    try:
        conn = sl.connect("drones.db")
    
    except:
        print 'Connection to university database failed...'
        print 'Connecting to local database...'
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='iteration_3')
    app = Application(conn)
    app.main_loop()
    conn.close()
