from tkinter import *
from tkinter import ttk
import datetime
import shortuuid
from tkinter import messagebox
from tkinter import filedialog as fd
import json

import customtkinter

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

male_color_value = "#0073cf"
female_color_value = "#f88379"
other_color_value = "#00755E"

def recursively_delete_children(node, node_list):
    for child in node.children:

        if child.spouse != None:
            node_list.remove(child.spouse)
        node_list.remove(child)
        recursively_delete_children(child, node_list)


# Class to hold details for each person
class Person():
    def __init__(self) -> None:
        self.id = str(shortuuid.uuid())[0:12]
        self.name = ""
        self.gender = "Male"
        self.birth = ""
        self.death = ""
        self.children = []
        self.spouse = None

        self.level = 0

        self.position_x = 0
        self.position_y = 0

        self.shape = None

        self.width = 120
        self.height = 60
        self.spacing_x = 120
        self.spacing_y = 120

# Main window class
class Window(Frame):

    def __init__(self):
        super().__init__()

        self.start_x = 310
        self.start_y = 150

        self.shape_index = 0

        self.current_shape = None
        self.previous_shape = None

        self.everyone = {}
        self.person_list = []
        self.level_dict = {}

        self.initUI()

    # Called when a shape is clicked on the canvas
    def single_shape_clicked(self, event):
        x, y = event.x, event.y
        #shape = self.canvas.find_closest(x, y)
        index = (event.widget.find_withtag("current")[0])
        #c.delete(shape)
        self.previous_shape = self.current_shape
        self.current_shape = index

        if self.previous_shape != None:
            self.canvas.itemconfig(self.previous_shape, width = 0)
        self.canvas.itemconfig(self.current_shape, width = 3)


        self.clear_information()
        #self.fetch_information()
        self.display_information()

    # Add new node
    def add_new_node(self):
        
        start_x = self.start_x
        start_y = self.start_y

        person = Person()
        person.position_x = start_x
        person.position_y = start_y

        person.level = 0

        self.person_list.append(person)

        self.draw_family_tree()

    # Add Spouse to Node
    def add_spouse(self):
        if self.current_shape == None:
            messagebox.showwarning(title="No node selected", message="Please select a node before trying to add a relation")
            return
        
        selected_individual = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected_individual = individual

        if selected_individual.spouse != None:
            return

        start_x = selected_individual.position_x + selected_individual.width + selected_individual.spacing_x
        start_y = selected_individual.position_y

        spouse = Person()
        spouse.position_x = start_x
        spouse.position_y = start_y

        selected_individual.spouse = spouse
        spouse.spouse = selected_individual

        spouse.level = selected_individual.level

        for child in selected_individual.children:
            spouse.children.append(child)

        self.reposition_children(selected_individual)
            

        self.person_list.append(spouse)

        self.draw_family_tree()

    # Add both parents to node
    def add_parents(self):
        if self.current_shape == None:
            messagebox.showwarning(title="No node selected", message="Please select a node before trying to add a relation")
            return
        
        selected_individual = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected_individual = individual

        start_x = selected_individual.position_x - selected_individual.width
        start_y = selected_individual.position_y - (selected_individual.height) - selected_individual.spacing_y

        mother = Person()
        mother.position_x = start_x
        mother.position_y = start_y
        mother.gender = "Female"

        father = Person()
        father.position_x = start_x + selected_individual.width + selected_individual.spacing_x
        father.position_y = start_y
        father.gender = "Male"

        mother.spouse, father.spouse = father, mother

        mother.children.append(selected_individual)
        father.children.append(selected_individual)

        mother.level = selected_individual.level - 1
        father.level = selected_individual.level - 1

        self.person_list.append(mother)
        self.person_list.append(father)

        self.draw_family_tree()

    # Add child to node
    def add_child(self):
        if self.current_shape == None:
            messagebox.showwarning(title="No node selected", message="Please select a node before trying to add a relation")
            return
        
        selected_individual = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected_individual = individual
                break

        children_count = len(selected_individual.children) + 1

        line_length = (selected_individual.width * children_count) // 2 - (selected_individual.width//2)

        line_length += (selected_individual.spacing_x * (children_count -1)//2)

        if selected_individual.spouse == None:

            initial_x = selected_individual.position_x
            initial_y = selected_individual.position_y

        else:
            if selected_individual.position_x < selected_individual.spouse.position_x:
                initial_x = selected_individual.position_x + selected_individual.width
                initial_y = selected_individual.position_y

            else:
                initial_x = selected_individual.spouse.position_x + selected_individual.spouse.width
                initial_y = selected_individual.spouse.position_y

        # for child in self.everyone[self.current_shape].children:
        # self.everyone[self.current_shape].children = []

        start_x = initial_x  - line_length
        start_y = initial_y + selected_individual.spacing_y + selected_individual.height

        for i in range(children_count):
            #print(i)

            if i >= children_count - 1:
            
                person = Person()
                person.position_x = start_x
                person.position_y = start_y


                selected_individual.children.append(person)

                person.level = selected_individual.level + 1

                if selected_individual.spouse != None:
                    selected_individual.spouse.children.append(person)

                self.person_list.append(person)

            else:
                child = selected_individual.children[i]
                child.position_x = start_x
                child.position_y = start_y


                if selected_individual.spouse != None:
                    if child not in selected_individual.spouse.children:
                        selected_individual.spouse.children.append(child)

                start_x += selected_individual.width + selected_individual.spacing_x

        self.draw_family_tree()

    def add_sibling(self):
        if self.current_shape == None:
            messagebox.showwarning(title="No node selected", message="Please select a node before trying to add a relation")
            return
        
        selected_individual = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected_individual = individual
                break

        selected_parent = None
        for individual in self.person_list:
            #print(selected_individual, individual.children)
            if selected_individual in individual.children:
                selected_parent = individual
                break

        if selected_parent == None:
            messagebox.showwarning(title="Node doesn't have parent", message="Ensure node has parent before adding sibline")
            return
        
        selected_individual = selected_parent

        children_count = len(selected_individual.children) + 1

        line_length = (selected_individual.width * children_count) // 2 - (selected_individual.width//2)

        line_length += (selected_individual.spacing_x * (children_count -1)//2)

        if selected_individual.spouse == None:

            initial_x = selected_individual.position_x
            initial_y = selected_individual.position_y

        else:
            if selected_individual.position_x < selected_individual.spouse.position_x:
                initial_x = selected_individual.position_x + selected_individual.width
                initial_y = selected_individual.position_y

            else:
                initial_x = selected_individual.spouse.position_x + selected_individual.spouse.width
                initial_y = selected_individual.spouse.position_y

        # for child in self.everyone[self.current_shape].children:
        # self.everyone[self.current_shape].children = []

        start_x = initial_x  - line_length
        start_y = initial_y + selected_individual.spacing_y + selected_individual.height

        for i in range(children_count):
            #print(i)

            if i >= children_count - 1:
            
                person = Person()
                person.position_x = start_x
                person.position_y = start_y
                selected_individual.children.append(person)

                person.level = selected_individual.level + 1

                if selected_individual.spouse != None:
                    selected_individual.spouse.children.append(person)

                self.person_list.append(person)


            else:
                child = selected_individual.children[i]
                child.position_x = start_x
                child.position_y = start_y

                if selected_individual.spouse != None:
                    if child not in selected_individual.spouse.children:
                        selected_individual.spouse.children.append(child)

                start_x += selected_individual.width + selected_individual.spacing_x

        self.draw_family_tree()
 

    # Connect nodes with spouse relations
    def draw_spouse_relation(self, node1, node2):
        if node1.position_x < node2.position_x:
            x1 = node1.position_x + node1.width
            x2 = node2.position_x
            # else:
            #     x2 = node1.position_x + node1.width
            #     x1 = node2.position_x

            y = node1.position_y + (node1.height//2)

            self.canvas.create_line(x1, y, x2, y, width = 2)

    # Join nodes with parental Relations
    def draw_parental_relation(self, parent, child):
        if parent.spouse != None:
            if parent.position_x < parent.spouse.position_x:
                x1 = parent.position_x + parent.width + (parent.spacing_x//2)
                
                y1 = parent.position_y + (parent.height//2)
                y2  = y1 + (parent.spacing_y//2) + (parent.spacing_y//4)

                self.canvas.create_line(x1, y1, x1, y2, width = 2)

                x2 = child.position_x + (child.width//2)

                y1 = y2
                y2 = y1 + (child.spacing_y//2) + child.width//4 - (parent.spacing_y//4)

                self.canvas.create_line(x2, y1, x2, y2, width = 2)

                if x1 != x2:
                    self.canvas.create_line(x1, y1, x2, y1, width = 2)

        else:
            x1 = parent.position_x + (parent.width//2)
                
            y1 = parent.position_y + parent.height
            y2  = y1 + (parent.spacing_y//2)

            self.canvas.create_line(x1, y1, x1, y2, width = 2)

            x2 = child.position_x + (child.width//2)

            y1 = y2
            y2 = y1 + (child.spacing_y//2)

            self.canvas.create_line(x2, y1, x2, y2, width = 2)

            if x1 != x2:
                self.canvas.create_line(x1, y1, x2, y1, width = 2)


    # reorganize nodes To prevent overlap
    def reorganize_nodes(self):
        level = 0
        keys = []

        for key in self.level_dict:
            keys.append(key)

        
        while True:
            found = False
            for level in keys:
                for node in self.level_dict[level]:
                    for comparison_node in self.level_dict[level]:
                        if node != comparison_node:
                            if node.position_x == comparison_node.position_x:
                                node.position_x = node.position_x - node.width - node.spacing_x

                                if node.spouse != None:
                                    node.spouse.position_x = node.spouse.position_x - node.width - node.spacing_x
                                found = True
                            
                            elif (node.position_x + node.width) == comparison_node.position_x:
                                node.position_x = node.position_x - node.spacing_x

                                if node.spouse != None:
                                    node.spouse.position_x = node.spouse.position_x - node.spacing_x
                                found = True
            if not found:
                break
        # Change children order to match parent order
        for level in sorted(keys)[1:]:
            parents_dict = {}
            parent_list = []
            coordinate_list = []
            parent_coordinate_list = []
            parent_coordinate_dict = {}
            node_list = []
            for node in self.level_dict[level]:
                for comparison_node in self.level_dict[level - 1]:
                    if node in comparison_node.children:
                        parent_node = comparison_node
                        parents_dict[node] = parent_node

                        if parent_node not in parent_list:
                            parent_list.append(parent_node)
                            parent_coordinate_list.append(parent_node.position_x)
                            parent_coordinate_dict[parent_node.position_x] = parent_node

                coordinate_list.append(node.position_x)


            node_list = []
            for coord in sorted(parent_coordinate_list):
                for child in parent_coordinate_dict[coord].children:
                    node_list.append(child)


            # set new node coordinates to sorted coordinates
            for node, coord in zip(node_list, sorted(coordinate_list)):
                node.position_x = coord

            

            coordinate_list = []
            node_list = []
            node_coordinate_dict = {}
            number_married = 0

            for node in self.level_dict[level]:
                coordinate_list.append(node.position_x)
                node_coordinate_dict[node.position_x] = node

                if node.spouse != None:
                    number_married += 1

            sorted_coordinates = sorted(coordinate_list)

            start_x = sorted_coordinates[0]

            n = Person()

            # for i in range(1):
            #     start_x = start_x - n.spacing_x - n.width

            for coord in sorted_coordinates:
                node = node_coordinate_dict[coord]

                node.position_x = start_x

                start_x = start_x + node.width + node.spacing_x

                if node.spouse != None:
                    node.spouse.position_x = start_x
                    start_x = start_x + node.width + node.spacing_x


    # Reposition children nodes to align with parents
    def reposition_children(self, selected_individual):
        children_count = len(selected_individual.children)

        line_length = (selected_individual.width * children_count) // 2 - (selected_individual.width//2)

        line_length += (selected_individual.spacing_x * (children_count -1)//2)


        if selected_individual.position_x > selected_individual.spouse.position_x:
            return
        
        initial_x = selected_individual.position_x + selected_individual.width
        initial_y = selected_individual.position_y

        # for child in self.everyone[self.current_shape].children:
        # self.everyone[self.current_shape].children = []

        start_x = initial_x  - line_length
        start_y = initial_y + selected_individual.spacing_y + selected_individual.height

        for i in range(children_count):
            #print(i)

            child = selected_individual.children[i]
            child.position_x = start_x
            child.position_y = start_y

            if selected_individual.spouse != None:
                if child not in selected_individual.spouse.children:
                    selected_individual.spouse.children.append(child)

            start_x += selected_individual.width + selected_individual.spacing_x

        #self.draw_family_tree()

    # Draw Family Tree
    def draw_family_tree(self):

        self.group_nodes_by_levels()

        self.reorganize_nodes()

        self.canvas.delete("all")

        for person in self.person_list:
            x = person.position_x
            y = person.position_y
            width = person.width
            height = person.height

            color = other_color_value
            if person.gender == "Male":
                color = male_color_value
            if person.gender == "Female":
                color = female_color_value

            square = self.canvas.create_rectangle(x, y, x + width, y + height,
            outline="#333333", fill=color, width = 0,tags="single_shape")

            self.canvas.create_text(x + (width//2),y + (height//2),fill="white",font="Roboto 10",
                        text=person.name)

            person.shape = square
        
            self.canvas.tag_bind("single_shape","<Button-1>",self.single_shape_clicked)

            if person.spouse != None:
                self.draw_spouse_relation(person, person.spouse)

            if person.children:
                for child in person.children:
                    self.draw_parental_relation(person, child)

    # Read input fields and save information to Person Objects
    def update_information(self):
        info_1 = self.id_entry.get()
        info_2 = self.name_entry.get()
        info_3 = self.option_variable.get()
        info_4 = self.birth_entry.get()
        info_5 = self.death_entry.get()

        selected = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected = individual
                break

        if selected == None:
            return
        
        selected.id = info_1
        selected.name = info_2
        selected.gender = info_3
        selected.birth = info_4
        selected.death = info_5  

        self.draw_family_tree()    

    # Copy information from file
    def fetch_information(self):
        pass

    def display_information(self):
        selected = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected = individual
                break

        if selected == None:
            return
        data = [selected.id, selected.name, selected.gender, selected.birth, selected.death

        ]
        self.id_entry.insert(0,data[0])
        self.name_entry.insert(0,data[1])
        self.option_variable.set(data[2])
        self.birth_entry.insert(0,data[3])
        self.death_entry.insert(0,data[4])

    # Clear text boxes
    def clear_information(self):
        self.id_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.option_variable.set("Select")
        self.birth_entry.delete(0, END)
        self.death_entry.delete(0, END)


    # Save data to a text file
    def save_data(self):
        #data = list(self.shape_data.values())
        data = []

        for person in self.person_list:
            person_data = {}

            id = person.id
            name = person.name
            gender = person.gender
            spouse = person.spouse
            children = person.children
            x_pos = person.position_x
            y_pos = person.position_y
            level = person.level

            if id:
                person_data["id"] =  id
            if name:
                person_data["name"] = name
            if gender:
                person_data["gender"] = gender
            if spouse != None:
                person_data["spouse"] = str(spouse.id)

            if children != None:
                person_data["children"] = []
                for child in children:
                    person_data["children"].append(str(child.id))

            person_data["x"] = str(x_pos)
            person_data["y"] = str(y_pos)
            person_data["level"] = str(level)

            data.append(person_data)

            filename = "output1.json"

            with open(filename, "w") as outfile:
                json.dump(data, outfile, indent=4, separators=(',', ': '))

    # Save data to a text file
    def import_data(self):
        filename = fd.askopenfilename()

        if not filename:
            return 
        
        self.person_list = []
        
        file = open (filename, "r")
  
        # Reading from file
        data = json.loads(file.read())
        
        # Iterating through the json
        # list
        for dict in data:
            person = Person()
            if "id" in dict:
                person.id = dict["id"]

            if "name" in dict:
                person.name = dict["name"]

            if "gender" in dict:
                person.gender = dict["gender"]

            if "birth" in dict:
                person.birth = dict["birth"]

            if "death" in dict:
                person.death = dict["death"]

            if "children" in dict:
                person.children = dict["children"]

            if "spouse" in dict:
                person.spouse = dict["spouse"]

            if "x" in dict:
                person.position_x = int(dict["x"])

            if "y" in dict:
                person.position_y = int(dict["y"])

            if "level" in dict:
                person.level = int(dict["level"])

            self.person_list.append(person)
        
        # Closing file
        file.close()

        #print("length", (self.person_list))

        for person in self.person_list:
            children_count = len(person.children)
            if children_count > 0:
                for i in range(children_count):
                    #print(i)
                    if isinstance(person.children[i], str):
                        for each in self.person_list:
                            if each.id == person.children[i]:
                                person.children[i] = each
                                break

            if person.spouse != "None":
                for each in self.person_list:
                    if each.id == person.spouse:
                        person.spouse = each
                        break

            else:
                person.spouse = None

        self.draw_family_tree()

    def group_nodes_by_levels(self):
        for person in self.person_list:
            self.level_dict[person.level] = []

        for person in self.person_list:
            if person.spouse == None:
                self.level_dict[person.level].append(person)
            else:
                if person.position_x < person.spouse.position_x:
                    self.level_dict[person.level].append(person)

        #print(self.level_dict)

    # Clear all nodes
    def clear_all(self):
        msg_box = messagebox.askquestion('Deletion Warning', 'Are you sure you want to delete every node?',
                                        icon='warning')
        if msg_box != 'yes':
            return
        self.person_list = []
        self.draw_family_tree()

    # Clear all nodes
    def delete_node(self):
        if self.current_shape == None:
            messagebox.showwarning(title="No node selected", message="Please select the node you want to delete")
            return

        msg_box = messagebox.askquestion('Deletion Warning', 'Are you sure you want to delete selected node? \nThis may delete all nodes descended from it!',
                                        icon='warning')
        if msg_box != 'yes':
            return
        # else:
        #     tk.messagebox.showinfo('Return', 'You will now return to the application screen')
        
        selected_individual = None
        for individual in self.person_list:
            if individual.shape == self.current_shape:
                selected_individual = individual
                break

        self.group_nodes_by_levels()
        nodes_above = []
        if (selected_individual.level - 1) in self.level_dict:
            nodes_above = self.level_dict[selected_individual.level - 1]

        has_parent = False
        spouse_has_parent = False
        for node in nodes_above:
            if selected_individual.spouse != None:
                if selected_individual.spouse in node.children:
                    spouse_has_parent = True
        
        if selected_individual.spouse != None:
            selected_individual.spouse.spouse = None

        if not spouse_has_parent:
            recursively_delete_children(selected_individual, self.person_list)
            if selected_individual.spouse != None:
                self.person_list.remove(selected_individual.spouse)


        for node in nodes_above:
            if selected_individual in node.children:
                node.children.remove(selected_individual)
        self.person_list.remove(selected_individual)

        self.draw_family_tree()


    # Display help window
    def show_help(self):
        help_window = Toplevel(root)
        help_window.geometry("640x400")
        help_window.title("Help")

        help_text = Label(help_window, text = "Hello, this is the help screen")
        help_text.pack()


    # Create and style UI widgets
    def initUI(self):

        self.master.title("Family Tree")
        self.pack(fill=BOTH, expand=1)

        # This will create style object
        style = ttk.Style()
        
        # This will be adding style, and
        # naming that style variable as
        # W.Tbutton (TButton is used for ttk.Button).
        style.configure('W.TButton', font =
                    ('calibri', 10, 'bold', 'underline'),
                        foreground = 'red')

        style.configure("TMenubutton", background="#cccccc")

        # Create menubar
        menu = Menu(self.master, bg="gray")
        self.master.config(menu=menu)

        # create the file object)
        file = Menu(menu, tearoff = 0)
        file.add_command(label="Import JSON", command=self.import_data)

        file.add_command(label="Export JSON", command=self.save_data)

        #file.add_command(label="EXPORT to .PNG", command=self.export_data)
        

        #added "file" to our menu
        menu.add_cascade(label="File", menu=file)

        # create the help object)
        help = Menu(menu, tearoff = 0)
        help.add_command(label="Show Help screen", command=self.show_help)

        #added "file" to our menu
        menu.add_cascade(label="Help", menu=help)

        ## Frame Creation ##
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill = BOTH, expand = True)

        self.buttons_frame = customtkinter.CTkFrame(self.main_frame)
        self.buttons_frame.grid(row = 0, column = 0, sticky="ewns", padx = 10, pady = 20)

        self.information_frame = customtkinter.CTkFrame(self.main_frame)
        self.information_frame.grid(row = 1, column = 0,sticky="ewns", padx = 10, pady = 20)

        self.canvas_frame = Frame(self.main_frame)
        self.canvas_frame.grid(row = 0, column = 1, rowspan=2, sticky="ewns", padx = 20, pady = 20)

        ## Buttons creation ##
        empty = customtkinter.CTkLabel(self.buttons_frame, text = "")
        empty.grid(columnspan=2, sticky="ew", padx = 30)
        
        self.add_node_button = customtkinter.CTkButton(self.buttons_frame, text = "Add Node", command=self.add_new_node)
        self.add_node_button.grid(columnspan=2, sticky="ew", padx = 30)

        self.add_child_button = customtkinter.CTkButton(self.buttons_frame, text = "Add Child", command=self.add_child)
        self.add_child_button.grid(columnspan=2, pady = 8, sticky="ew", padx = 30)

        self.add_spouse_button = customtkinter.CTkButton(self.buttons_frame, text = "Add Spouse", command=self.add_spouse)
        self.add_spouse_button.grid(columnspan=2, sticky="ew", padx = 30)

        self.add_parents_button = customtkinter.CTkButton(self.buttons_frame, text = "Add Parents", command=self.add_parents)
        self.add_parents_button.grid(columnspan=2, pady = 8, sticky="ew", padx = 30)

        self.add_sibling_button = customtkinter.CTkButton(self.buttons_frame, text = "Add Sibling", command=self.add_sibling)
        self.add_sibling_button.grid(columnspan=2, sticky="ew", padx = 30)

        self.delete_node_button = customtkinter.CTkButton(self.buttons_frame, text = "Delete Node", command=self.delete_node)
        self.delete_node_button.grid(columnspan=2 , pady = 8, sticky="ew", padx = 30)

        self.clear_all_button = customtkinter.CTkButton(self.buttons_frame, text = "Clear all", command=self.clear_all)
        self.clear_all_button.grid(columnspan = 2, sticky="ew", padx = 30)

        empty = customtkinter.CTkLabel(self.buttons_frame, text = "")
        empty.grid(columnspan=2, sticky="ew", padx = 30)

        ## Information Entry ##

        empty = customtkinter.CTkLabel(self.information_frame, text = "")
        empty.grid(columnspan=2, sticky="ew", padx = 30)

        self.id_label = customtkinter.CTkLabel(self.information_frame, text = "ID", anchor = W)
        self.id_label.grid(sticky="ew", pady = 5, padx = 30, row = 1, column = 0)

        self.id_entry = customtkinter.CTkEntry(self.information_frame)
        self.id_entry.grid(sticky="ew", pady = 5, padx = 30, row = 1, column = 1)

        self.name_label = customtkinter.CTkLabel(self.information_frame, text = "Name", anchor = W)
        self.name_label.grid(sticky="ew", pady = 5, padx = 30, row = 2, column = 0)        

        self.name_entry = customtkinter.CTkEntry(self.information_frame)
        self.name_entry.grid(sticky="ew", padx = 30, row = 2, column = 1)

        self.gender_label = customtkinter.CTkLabel(self.information_frame, text = "Gender", anchor = W)
        self.gender_label.grid(sticky="ew", pady = 5, padx = 30, row = 3, column = 0)

        self.option_variable = customtkinter.StringVar(self)
        self.option_variable.set("Male")
        option_list = ["Select", "Male", "Female", "Other"]

        self.gender_entry = customtkinter.CTkOptionMenu(self.information_frame, variable = self.option_variable, values = option_list)
        self.gender_entry.grid(sticky="ew", pady = 5, padx = 30, row = 3, column = 1)

        self.birth_label = customtkinter.CTkLabel(self.information_frame, text = "Birth", anchor = W)
        self.birth_label.grid(sticky="ew", pady = 5, padx = 30, row = 4, column = 0)

        self.birth_entry = customtkinter.CTkEntry(self.information_frame)
        self.birth_entry.grid(sticky="ew", padx = 30, row = 4, column = 1)

        self.death_label = customtkinter.CTkLabel(self.information_frame, text = "Death", anchor = W)
        self.death_label.grid(sticky="ew", pady = 5, padx = 30, row = 5, column = 0)

        self.death_entry = customtkinter.CTkEntry(self.information_frame)
        self.death_entry.grid(sticky="ew", padx = 30, row = 5, column = 1)

        

        self.save_info_button = customtkinter.CTkButton(self.information_frame, text = "Update Information", command = self.update_information)
        self.save_info_button.grid(sticky="ew", padx = 30, pady= 10, columnspan = 2)

        empty = customtkinter.CTkLabel(self.information_frame, text = "")
        empty.grid(columnspan=2, sticky="ew", padx = 30)

        ## Create canvas  ##

        def do_zoom(event):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            factor = 1.001 ** event.delta
            self.canvas.scale(ALL, x, y, factor, factor)

        self.canvas = Canvas(self.canvas_frame, bg = "#eeeeee")   
        self.canvas.bind("<MouseWheel>", do_zoom)
        self.canvas.bind('<ButtonPress-1>', lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        self.canvas.pack(fill=BOTH, expand=True)

        # Set grid column weights to define how they stretch

        self.main_frame.grid_columnconfigure(1,weight=4)
        #self.main_frame.grid_rowconfigure(0,weight=1)

        self.information_frame.grid_columnconfigure(0, weight=1)
        self.information_frame.grid_columnconfigure(1, weight=4)
        
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)


# Create root window and start event loop
def main():
    global root

    root = customtkinter.CTk()
    ex = Window()
    root.geometry("1100x650+150+30")
    root.mainloop()


if __name__ == '__main__':
    main()