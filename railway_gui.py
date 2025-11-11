import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from datetime import datetime, timedelta
import hashlib

class RailwayManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Database connection
        self.db = None
        self.cursor = None
        self.current_user = None
        self.current_user_role = None
        self.db_connected = False
        
        # Connect to database
        if not self.connect_db():
            # Connection failed, don't continue initialization
            return
        
        # Create main container
        self.main_container = tk.Frame(root, bg='#2c3e50')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Show login screen
        self.show_login()
    
    def connect_db(self):
        """Connect to MySQL database - Returns True if successful, False otherwise"""
        try:
            # First, connect without specifying database to check if it exists
            temp_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hehe"  # Change this to your MySQL password
            )
            temp_cursor = temp_conn.cursor()
            
            # Check if database exists
            temp_cursor.execute("SHOW DATABASES LIKE 'railway_system'")
            db_exists = temp_cursor.fetchone()
            
            if not db_exists:
                messagebox.showerror(
                    "Database Not Found", 
                    "The 'railway_system' database does not exist!\n\n"
                    "Please run the SQL script first:\n"
                    "mysql -u root -p < dbmsprojmain.sql\n\n"
                    "Then run the sample data:\n"
                    "mysql -u root -p < sample_data.sql"
                )
                temp_cursor.close()
                temp_conn.close()
                self.root.destroy()
                return False
            
            temp_cursor.close()
            temp_conn.close()
            
            # Now connect to the database
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hehe",  # Change this to your MySQL password
                database="railway_system"
            )
            self.cursor = self.db.cursor()
            
            # Check if essential tables exist
            required_tables = ['user', 'station', 'train', 'ticket', 'route', 'payment']
            self.cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in self.cursor.fetchall()]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                messagebox.showwarning(
                    "Incomplete Database", 
                    f"Missing tables: {', '.join(missing_tables)}\n\n"
                    "The database exists but some tables are missing.\n"
                    "Please run the complete SQL script:\n"
                    "mysql -u root -p < dbmsprojmain.sql"
                )
            
            # Check if there's any data in critical tables
            self.cursor.execute("SELECT COUNT(*) FROM station")
            station_count = self.cursor.fetchone()[0]
            
            if station_count == 0:
                response = messagebox.askyesno(
                    "Empty Database", 
                    "The database has no stations!\n\n"
                    "Would you like to continue anyway?\n"
                    "(You should run sample_data.sql for testing)"
                )
                if not response:
                    self.root.destroy()
                    return False
            
            print("Database connected successfully!")
            print(f"Found {station_count} stations in the database.")
            self.db_connected = True
            return True
            
        except mysql.connector.Error as err:
            error_msg = str(err)
            if "Access denied" in error_msg:
                messagebox.showerror(
                    "Authentication Error", 
                    "Access denied for MySQL user 'root'.\n\n"
                    "Please update the password in railway_gui.py:\n"
                    "Line 40: password='YOUR_MYSQL_PASSWORD'"
                )
            elif "Can't connect" in error_msg:
                messagebox.showerror(
                    "Connection Error", 
                    "Cannot connect to MySQL server!\n\n"
                    "Please ensure:\n"
                    "1. MySQL server is running\n"
                    "2. Host and port are correct\n"
                    "3. MySQL service is started"
                )
            else:
                messagebox.showerror("Database Error", f"Error: {err}")
            
            self.root.destroy()
            return False
    
    def clear_frame(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_login(self):
        """Display login screen"""
        self.clear_frame()
        
        login_frame = tk.Frame(self.main_container, bg='#34495e', padx=50, pady=50)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        tk.Label(login_frame, text="Railway Management System", 
                font=('Arial', 24, 'bold'), bg='#34495e', fg='#ecf0f1').pack(pady=20)
        
        # Email
        tk.Label(login_frame, text="Email:", font=('Arial', 12), 
                bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W, pady=(10,0))
        self.email_entry = tk.Entry(login_frame, font=('Arial', 12), width=30)
        self.email_entry.pack(pady=5)
        
        # Password
        tk.Label(login_frame, text="Password:", font=('Arial', 12), 
                bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W, pady=(10,0))
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12), width=30, show='*')
        self.password_entry.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(login_frame, bg='#34495e')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", font=('Arial', 12, 'bold'), 
                 bg='#27ae60', fg='white', width=12, command=self.login).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Register", font=('Arial', 12, 'bold'), 
                 bg='#3498db', fg='white', width=12, command=self.show_register).pack(side=tk.LEFT, padx=5)
    
    def login(self):
        """Handle user login"""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            self.cursor.execute(
                "SELECT user_id, name, role FROM user WHERE email = %s AND password = %s",
                (email, hashed_password)
            )
            result = self.cursor.fetchone()
            
            if result:
                self.current_user = result[0]
                self.current_user_name = result[1]
                self.current_user_role = result[2]
                messagebox.showinfo("Success", f"Welcome {self.current_user_name}!")
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def show_register(self):
        """Display registration screen"""
        self.clear_frame()
        
        reg_frame = tk.Frame(self.main_container, bg='#34495e', padx=30, pady=30)
        reg_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(reg_frame, text="Register New User", font=('Arial', 20, 'bold'), 
                bg='#34495e', fg='#ecf0f1').grid(row=0, column=0, columnspan=2, pady=20)
        
        # Form fields
        fields = [
            ("User ID:", "user_id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("City:", "city"),
            ("State:", "state"),
            ("PIN Code:", "pin_code"),
            ("Mobile No:", "mobile")
        ]
        
        self.reg_entries = {}
        for idx, (label, key) in enumerate(fields, start=1):
            tk.Label(reg_frame, text=label, font=('Arial', 11), 
                    bg='#34495e', fg='#ecf0f1').grid(row=idx, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(reg_frame, font=('Arial', 11), width=30)
            if key == "password":
                entry.config(show='*')
            entry.grid(row=idx, column=1, pady=5, padx=10)
            self.reg_entries[key] = entry
        
        # Gender
        tk.Label(reg_frame, text="Gender:", font=('Arial', 11), 
                bg='#34495e', fg='#ecf0f1').grid(row=len(fields)+1, column=0, sticky=tk.W, pady=5)
        self.gender_var = tk.StringVar(value="male")
        gender_frame = tk.Frame(reg_frame, bg='#34495e')
        gender_frame.grid(row=len(fields)+1, column=1, sticky=tk.W)
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="male", 
                      bg='#34495e', fg='#ecf0f1', selectcolor='#34495e').pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="female", 
                      bg='#34495e', fg='#ecf0f1', selectcolor='#34495e').pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Other", variable=self.gender_var, value="other", 
                      bg='#34495e', fg='#ecf0f1', selectcolor='#34495e').pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(reg_frame, bg='#34495e')
        btn_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Register", font=('Arial', 12, 'bold'), 
                 bg='#27ae60', fg='white', width=12, command=self.register_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back to Login", font=('Arial', 12, 'bold'), 
                 bg='#95a5a6', fg='white', width=12, command=self.show_login).pack(side=tk.LEFT, padx=5)
    
    def register_user(self):
        """Register a new user"""
        user_data = {key: entry.get() for key, entry in self.reg_entries.items()}
        
        if not all(user_data.values()):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Hash password
        hashed_password = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        try:
            # Insert user
            self.cursor.execute(
                """INSERT INTO user (user_id, name, email, password, dob, gender, city, state, pin_code, role)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'passenger')""",
                (user_data['user_id'], user_data['name'], user_data['email'], hashed_password,
                 user_data['dob'], self.gender_var.get(), user_data['city'], 
                 user_data['state'], user_data['pin_code'])
            )
            
            # Insert mobile number
            self.cursor.execute(
                "INSERT INTO user_mobile (user_id, mobile_no) VALUES (%s, %s)",
                (user_data['user_id'], user_data['mobile'])
            )
            
            self.db.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_login()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            self.db.rollback()
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.clear_frame()
        
        # Header
        header = tk.Frame(self.main_container, bg='#1abc9c', height=80)
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"Railway Management System - Welcome {self.current_user_name}!", 
                font=('Arial', 18, 'bold'), bg='#1abc9c', fg='white').pack(side=tk.LEFT, padx=20, pady=25)
        
        tk.Button(header, text="Logout", font=('Arial', 11, 'bold'), 
                 bg='#e74c3c', fg='white', command=self.show_login).pack(side=tk.RIGHT, padx=20)
        
        # Main content area
        content = tk.Frame(self.main_container, bg='#ecf0f1')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Button grid
        buttons = [
            ("🔍 Search Trains", self.search_trains),
            ("🎫 Book Ticket", self.book_ticket_simple),
            ("📋 My Bookings", self.view_bookings),
            ("❌ Cancel Ticket", self.cancel_ticket),
            ("🚉 View Stations", self.view_stations),
            ("🚂 View All Trains", self.view_trains),
            ("💳 Payment History", self.view_payments),
            ("📊 Train Status", self.view_train_status)
        ]
        
        for idx, (text, command) in enumerate(buttons):
            row = idx // 3
            col = idx % 3
            btn = tk.Button(content, text=text, font=('Arial', 14, 'bold'), 
                          bg='#3498db', fg='white', width=20, height=3,
                          command=command, cursor='hand2')
            btn.grid(row=row, column=col, padx=15, pady=15)
    
    def search_trains(self):
        """Search trains between two stations"""
        search_win = tk.Toplevel(self.root)
        search_win.title("Search Trains")
        search_win.geometry("900x600")
        search_win.configure(bg='#ecf0f1')
        
        # Get stations from database
        self.cursor.execute("SELECT station_id, station_name, city FROM station ORDER BY station_name")
        stations = self.cursor.fetchall()
        station_list = ["-- Any Station --"] + [f"{s[0]} - {s[1]} ({s[2]})" for s in stations]
        station_ids = {f"{s[0]} - {s[1]} ({s[2]})": s[0] for s in stations}
        station_ids["-- Any Station --"] = None
        
        # Input frame
        input_frame = tk.Frame(search_win, bg='#34495e', padx=20, pady=20)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(input_frame, text="Source Station:", font=('Arial', 11), 
                bg='#34495e', fg='white').grid(row=0, column=0, pady=5, padx=5)
        source_var = tk.StringVar()
        source_combo = ttk.Combobox(input_frame, textvariable=source_var, values=station_list, 
                                     font=('Arial', 10), width=30, state='readonly')
        source_combo.grid(row=0, column=1, pady=5, padx=5)
        source_combo.set("-- Any Station --")
        
        tk.Label(input_frame, text="Destination Station:", font=('Arial', 11), 
                bg='#34495e', fg='white').grid(row=0, column=2, pady=5, padx=5)
        dest_var = tk.StringVar()
        dest_combo = ttk.Combobox(input_frame, textvariable=dest_var, values=station_list, 
                                   font=('Arial', 10), width=30, state='readonly')
        dest_combo.grid(row=0, column=3, pady=5, padx=5)
        dest_combo.set("-- Any Station --")
        
        tk.Label(input_frame, text="Travel Date:", font=('Arial', 11), 
                bg='#34495e', fg='white').grid(row=1, column=0, pady=5, padx=5)
        date_frame = tk.Frame(input_frame, bg='#34495e')
        date_frame.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(date_frame, textvariable=date_var, font=('Arial', 11), width=12)
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quick date buttons
        tk.Button(date_frame, text="Today", font=('Arial', 9), bg='#95a5a6', fg='white',
                 command=lambda: date_var.set(datetime.now().strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=2)
        tk.Button(date_frame, text="Tomorrow", font=('Arial', 9), bg='#95a5a6', fg='white',
                 command=lambda: date_var.set((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=2)
        
        # Results frame
        result_frame = tk.Frame(search_win, bg='#ecf0f1')
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for results
        columns = ("Train No", "Train Name", "Type", "Departure", "Arrival")
        tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        def perform_search():
            # Clear previous results
            for item in tree.get_children():
                tree.delete(item)
            
            source_text = source_var.get()
            dest_text = dest_var.get()
            travel_date = date_var.get()
            
            # Extract station IDs
            source = station_ids.get(source_text, '')
            dest = station_ids.get(dest_text, '')
            
            try:
                # If "Any Station" is selected, show all trains
                if source is None and dest is None:
                    # Show all trains
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type, 
                               s.start_time, s.end_time
                        FROM train t
                        JOIN schedule s ON t.train_no = s.train_no
                        ORDER BY t.train_name
                    """)
                    trains = self.cursor.fetchall()
                    for train in trains:
                        tree.insert('', tk.END, values=train)
                elif source is None:
                    # Show trains going to destination
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type,
                               rs.departure_time, rs.arrival_time
                        FROM train t
                        JOIN route_station rs ON t.route_id = rs.route_id
                        WHERE rs.station_id = %s
                        ORDER BY t.train_name
                    """, (dest,))
                    trains = self.cursor.fetchall()
                    for train in trains:
                        tree.insert('', tk.END, values=train)
                elif dest is None:
                    # Show trains from source
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type,
                               rs.departure_time, rs.arrival_time
                        FROM train t
                        JOIN route_station rs ON t.route_id = rs.route_id
                        WHERE rs.station_id = %s
                        ORDER BY t.train_name
                    """, (source,))
                    trains = self.cursor.fetchall()
                    for train in trains:
                        tree.insert('', tk.END, values=train)
                else:
                    # Normal search with both stations
                    self.cursor.callproc('search_trains', (source, dest, travel_date))
                    for result in self.cursor.stored_results():
                        trains = result.fetchall()
                        for train in trains:
                            tree.insert('', tk.END, values=train)
                
                if not tree.get_children():
                    messagebox.showinfo("Info", "No trains found")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
        
        tk.Button(input_frame, text="Search", font=('Arial', 12, 'bold'), 
                 bg='#27ae60', fg='white', command=perform_search).grid(row=1, column=2, padx=10, pady=5)
    
    def book_ticket(self):
        """Book a new ticket - Ultra simplified"""
        book_win = tk.Toplevel(self.root)
        book_win.title("Book Ticket - Easy & Fast")
        book_win.geometry("900x700")
        book_win.configure(bg='#ecf0f1')
        
        # Header
        header = tk.Frame(book_win, bg='#3498db', height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎫 Book Your Train Ticket", font=('Arial', 20, 'bold'), 
                bg='#3498db', fg='white').pack(pady=15)
        
        main_frame = tk.Frame(book_win, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Step 1: Route Selection
        step1_frame = tk.LabelFrame(main_frame, text="Step 1: Select Your Journey", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white', padx=20, pady=15)
        step1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get stations
        self.cursor.execute("SELECT station_id, station_name, city FROM station ORDER BY station_name")
        stations = self.cursor.fetchall()
        station_list = [f"{s[1]} ({s[2]})" for s in stations]
        station_map = {f"{s[1]} ({s[2]})": s[0] for s in stations}
        
        # Source and Destination in same row
        route_frame = tk.Frame(step1_frame, bg='#34495e')
        route_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(route_frame, text="From:", font=('Arial', 11, 'bold'), 
                bg='#34495e', fg='white').grid(row=0, column=0, sticky=tk.W, padx=(0,5))
        source_var = tk.StringVar()
        source_combo = ttk.Combobox(route_frame, textvariable=source_var, values=station_list, 
                                    font=('Arial', 11), width=25, state='readonly')
        source_combo.grid(row=0, column=1, padx=5)
        if station_list:
            source_combo.set(station_list[0])
        
        tk.Label(route_frame, text="To:", font=('Arial', 11, 'bold'), 
                bg='#34495e', fg='white').grid(row=0, column=2, padx=(15,5))
        dest_var = tk.StringVar()
        dest_combo = ttk.Combobox(route_frame, textvariable=dest_var, values=station_list, 
                                  font=('Arial', 11), width=25, state='readonly')
        dest_combo.grid(row=0, column=3, padx=5)
        if len(station_list) > 1:
            dest_combo.set(station_list[1])
        
        # Travel date
        date_frame = tk.Frame(step1_frame, bg='#34495e')
        date_frame.pack(fill=tk.X, pady=(10,5))
        
        tk.Label(date_frame, text="Travel Date:", font=('Arial', 11, 'bold'), 
                bg='#34495e', fg='white').pack(side=tk.LEFT, padx=(0,10))
        date_var = tk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        date_entry = tk.Entry(date_frame, textvariable=date_var, font=('Arial', 11), width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(date_frame, text="Tomorrow", font=('Arial', 9), bg='#3498db', fg='white',
                 command=lambda: date_var.set((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=2)
        tk.Button(date_frame, text="+3 days", font=('Arial', 9), bg='#3498db', fg='white',
                 command=lambda: date_var.set((datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=2)
        tk.Button(date_frame, text="+7 days", font=('Arial', 9), bg='#3498db', fg='white',
                 command=lambda: date_var.set((datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=2)
        
        # Find Trains Button
        find_btn = tk.Button(step1_frame, text="🔍 Find Available Trains", font=('Arial', 12, 'bold'), 
                            bg='#27ae60', fg='white', height=2)
        find_btn.pack(pady=(15,5), fill=tk.X)
        
        # Step 2: Train Selection
        step2_frame = tk.LabelFrame(main_frame, text="Step 2: Choose Train & Class", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white', padx=20, pady=15)
        step2_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Available trains list
        info_label = tk.Label(step2_frame, text="Select route and click 'Find Available Trains'", 
                             font=('Arial', 10, 'italic'), bg='#34495e', fg='#ecf0f1')
        info_label.pack(pady=10)
        
        trains_frame = tk.Frame(step2_frame, bg='#34495e')
        trains_frame.pack(fill=tk.BOTH, expand=True)
        
        # Train selection variables
        selected_train = {'train_no': None, 'train_name': None}
        selected_class = {'class_id': None, 'class_name': None, 'available_seats': 0}
        
        def find_trains():
            """Find trains that go on the selected route"""
            # Clear previous results
            for widget in trains_frame.winfo_children():
                widget.destroy()
            
            source_text = source_var.get()
            dest_text = dest_var.get()
            travel_date = date_var.get()
            
            if not source_text or not dest_text:
                messagebox.showerror("Error", "Please select both source and destination")
                return
            
            source_id = station_map.get(source_text)
            dest_id = station_map.get(dest_text)
            
            if source_id == dest_id:
                messagebox.showerror("Error", "Source and destination cannot be the same!")
                return
            
            # Find trains on this route
            try:
                self.cursor.callproc('search_trains', (source_id, dest_id, travel_date))
                trains = []
                for result in self.cursor.stored_results():
                    trains = result.fetchall()
                
                if not trains:
                    info_label.config(text="❌ No trains found on this route!", fg='#e74c3c')
                    return
                
                info_label.config(text=f"✅ Found {len(trains)} train(s) on this route:", fg='#2ecc71')
                
                # Display trains with radio buttons
                train_var = tk.StringVar()
                
                for idx, train in enumerate(trains):
                    train_no, train_name, train_type, dept_time, arr_time = train
                    
                    train_frame = tk.Frame(trains_frame, bg='#2c3e50', relief=tk.RAISED, borderwidth=2)
                    train_frame.pack(fill=tk.X, pady=5, padx=5)
                    
                    radio = tk.Radiobutton(train_frame, text="", variable=train_var, value=train_no,
                                          bg='#2c3e50', selectcolor='#2c3e50', activebackground='#2c3e50')
                    radio.pack(side=tk.LEFT, padx=5)
                    
                    details = tk.Frame(train_frame, bg='#2c3e50')
                    details.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
                    
                    tk.Label(details, text=f"{train_name} ({train_no})", 
                            font=('Arial', 11, 'bold'), bg='#2c3e50', fg='white').pack(anchor=tk.W)
                    tk.Label(details, text=f"Type: {train_type.upper()} | Departs: {dept_time} → Arrives: {arr_time}", 
                            font=('Arial', 9), bg='#2c3e50', fg='#ecf0f1').pack(anchor=tk.W)
                    
                    if idx == 0:
                        train_var.set(train_no)
                        selected_train['train_no'] = train_no
                        selected_train['train_name'] = train_name
                
                def on_train_select():
                    """Load classes when train is selected"""
                    train_no = train_var.get()
                    if train_no:
                        selected_train['train_no'] = train_no
                        for train in trains:
                            if train[0] == train_no:
                                selected_train['train_name'] = train[1]
                                break
                        show_classes(train_no, travel_date)
                
                train_var.trace('w', lambda *args: on_train_select())
                if trains:
                    show_classes(trains[0][0], travel_date)
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
        
        def show_classes(train_no, travel_date):
            """Show available classes for selected train"""
            # Clear class selection area
            for widget in step3_frame.winfo_children():
                widget.destroy()
            
            tk.Label(step3_frame, text="Select Class:", font=('Arial', 11, 'bold'), 
                    bg='#34495e', fg='white').pack(anchor=tk.W, pady=(0,10))
            
            # Get classes with availability
            self.cursor.execute("""
                SELECT c.class_id, c.class_name, c.coach_type, 
                       COALESCE(sa.available_seats, 0) as available_seats
                FROM class c
                LEFT JOIN seat_availability sa ON c.class_id = sa.class_id 
                    AND sa.train_no = c.train_no AND sa.travel_date = %s
                WHERE c.train_no = %s
                ORDER BY c.c_multiplier DESC
            """, (travel_date, train_no))
            
            classes = self.cursor.fetchall()
            
            if not classes:
                tk.Label(step3_frame, text="No classes available for this train", 
                        font=('Arial', 10), bg='#34495e', fg='#e74c3c').pack()
                return
            
            class_var = tk.StringVar()
            
            for idx, cls in enumerate(classes):
                class_id, class_name, coach_type, available = cls
                
                class_frame = tk.Frame(step3_frame, bg='#2c3e50', relief=tk.RAISED, borderwidth=2)
                class_frame.pack(fill=tk.X, pady=3, padx=5)
                
                radio = tk.Radiobutton(class_frame, text="", variable=class_var, value=class_id,
                                      bg='#2c3e50', selectcolor='#2c3e50', activebackground='#2c3e50')
                radio.pack(side=tk.LEFT, padx=5)
                
                details = tk.Frame(class_frame, bg='#2c3e50')
                details.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
                
                tk.Label(details, text=f"{class_name} ({coach_type.upper()})", 
                        font=('Arial', 10, 'bold'), bg='#2c3e50', fg='white').pack(side=tk.LEFT)
                
                seats_color = '#2ecc71' if available > 20 else '#e67e22' if available > 0 else '#e74c3c'
                seats_text = f"🎫 {available} seats" if available > 0 else "❌ Sold Out"
                tk.Label(details, text=seats_text, font=('Arial', 10), 
                        bg='#2c3e50', fg=seats_color).pack(side=tk.RIGHT, padx=10)
                
                if idx == 0 and available > 0:
                    class_var.set(class_id)
                    selected_class['class_id'] = class_id
                    selected_class['class_name'] = class_name
                    selected_class['available_seats'] = available
            
            def on_class_select():
                class_id = class_var.get()
                for cls in classes:
                    if cls[0] == class_id:
                        selected_class['class_id'] = class_id
                        selected_class['class_name'] = cls[1]
                        selected_class['available_seats'] = cls[3]
                        break
            
            class_var.trace('w', lambda *args: on_class_select())
        
        # Step 3: Class Selection
        step3_frame = tk.LabelFrame(main_frame, text="Step 3: Select Class", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white', padx=20, pady=15)
        step3_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Confirm Button
        def confirm_booking():
            if not selected_train['train_no']:
                messagebox.showerror("Error", "Please select a train")
                return
            
            if not selected_class['class_id']:
                messagebox.showerror("Error", "Please select a class")
                return
            
            if selected_class['available_seats'] <= 0:
                messagebox.showerror("Error", "No seats available in selected class!")
                return
            
            source_id = station_map.get(source_var.get())
            dest_id = station_map.get(dest_var.get())
            # Generate short PNR: P + MMDDHHMMSS (11 chars)
            pnr = f"P{datetime.now().strftime('%m%d%H%M%S')}"
            
            try:
                self.cursor.callproc('book_ticket', 
                    (pnr, selected_train['train_no'], self.current_user, 
                     source_id, dest_id, date_var.get(), selected_class['class_id'], ''))
                
                self.db.commit()
                
                messagebox.showinfo("Success", 
                    f"🎉 Ticket Booked Successfully!\n\n"
                    f"PNR: {pnr}\n"
                    f"Train: {selected_train['train_name']}\n"
                    f"From: {source_var.get()}\n"
                    f"To: {dest_var.get()}\n"
                    f"Date: {date_var.get()}\n"
                    f"Class: {selected_class['class_name']}")
                book_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
                self.db.rollback()
        
        confirm_frame = tk.Frame(main_frame, bg='#ecf0f1')
        confirm_frame.pack(fill=tk.X)
        
        tk.Button(confirm_frame, text="✅ Confirm Booking", font=('Arial', 14, 'bold'), 
                 bg='#27ae60', fg='white', height=2, command=confirm_booking).pack(fill=tk.X)
        
        find_btn.config(command=find_trains)
    
    def book_ticket_simple(self):
        """Clickable booking with visual train and class selection"""
        book_win = tk.Toplevel(self.root)
        book_win.title("Book Train Ticket")
        book_win.geometry("1000x750")
        book_win.configure(bg='white')
        
        # Main container with padding
        container = tk.Frame(book_win, bg='white', padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(container, text="🚂 Book Your Ticket", font=('Arial', 22, 'bold'), 
                bg='white', fg='#2c3e50').pack(pady=(0,20))
        
        # Form frame
        form = tk.Frame(container, bg='white')
        form.pack(fill=tk.X)
        
        # Get stations for dropdown
        self.cursor.execute("SELECT DISTINCT station_name, city FROM station ORDER BY station_name")
        stations = self.cursor.fetchall()
        station_names = ["-- Any Station --"] + [f"{s[0]} ({s[1]})" for s in stations]
        
        # From
        tk.Label(form, text="From:", font=('Arial', 12, 'bold'), bg='white').grid(row=0, column=0, sticky=tk.W, pady=10)
        from_var = tk.StringVar()
        from_combo = ttk.Combobox(form, textvariable=from_var, values=station_names, 
                                  font=('Arial', 11), width=35, state='readonly')
        from_combo.grid(row=0, column=1, pady=10, sticky=tk.W)
        from_combo.set("-- Any Station --")
        
        # To
        tk.Label(form, text="To:", font=('Arial', 12, 'bold'), bg='white').grid(row=1, column=0, sticky=tk.W, pady=10)
        to_var = tk.StringVar()
        to_combo = ttk.Combobox(form, textvariable=to_var, values=station_names, 
                                font=('Arial', 11), width=35, state='readonly')
        to_combo.grid(row=1, column=1, pady=10, sticky=tk.W)
        to_combo.set("-- Any Station --")
        
        # Date with quick buttons
        tk.Label(form, text="Date:", font=('Arial', 12, 'bold'), bg='white').grid(row=2, column=0, sticky=tk.W, pady=10)
        date_frame = tk.Frame(form, bg='white')
        date_frame.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        date_var = tk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        tk.Entry(date_frame, textvariable=date_var, font=('Arial', 11), width=13).pack(side=tk.LEFT)
        tk.Button(date_frame, text="Tomorrow", bg='#3498db', fg='white', font=('Arial', 9),
                 command=lambda: date_var.set((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT, padx=5)
        tk.Button(date_frame, text="Next Week", bg='#3498db', fg='white', font=('Arial', 9),
                 command=lambda: date_var.set((datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))).pack(side=tk.LEFT)
        
        # Passenger count
        tk.Label(form, text="Passengers:", font=('Arial', 12, 'bold'), bg='white').grid(row=3, column=0, sticky=tk.W, pady=10)
        passenger_var = tk.IntVar(value=1)
        passenger_spin = tk.Spinbox(form, from_=1, to=10, textvariable=passenger_var, 
                                    font=('Arial', 11), width=10, state='readonly')
        passenger_spin.grid(row=3, column=1, pady=10, sticky=tk.W)
        
        # Canvas for scrollable results
        result_frame = tk.LabelFrame(container, text="Available Trains - Click to Select", 
                                     font=('Arial', 12, 'bold'), bg='white', padx=15, pady=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        canvas = tk.Canvas(result_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial message
        tk.Label(scrollable_frame, text="Click 'Search Trains' to see available options...", 
                font=('Arial', 11), bg='#f8f9fa', fg='#7f8c8d').pack(pady=30)
        
        # Store selected train and class
        selected_train = {'train_no': None, 'class_id': None, 'class_name': None, 
                         'train_name': None, 'seats_available': 0}
        
        def search_trains():
            """Find available trains and display as clickable cards"""
            # Clear previous results
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            from_station = from_var.get()
            to_station = to_var.get()
            travel_date = date_var.get()
            
            # Handle "Any Station" option
            from_id = None
            to_id = None
            
            if from_station != "-- Any Station --":
                from_station = from_station.split('(')[0].strip()
                self.cursor.execute("SELECT station_id FROM station WHERE station_name = %s", (from_station,))
                from_id_result = self.cursor.fetchone()
                if from_id_result:
                    from_id = from_id_result[0]
            
            if to_station != "-- Any Station --":
                to_station = to_station.split('(')[0].strip()
                self.cursor.execute("SELECT station_id FROM station WHERE station_name = %s", (to_station,))
                to_id_result = self.cursor.fetchone()
                if to_id_result:
                    to_id = to_id_result[0]
            
            # Search trains
            try:
                trains = []
                
                if from_id is None and to_id is None:
                    # Show all trains
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type, 
                               s.start_time, s.end_time
                        FROM train t
                        JOIN schedule s ON t.train_no = s.train_no
                        ORDER BY t.train_name
                    """)
                    trains = self.cursor.fetchall()
                elif from_id is None:
                    # Show trains going to destination
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type,
                               rs.departure_time, rs.arrival_time
                        FROM train t
                        JOIN route_station rs ON t.route_id = rs.route_id
                        WHERE rs.station_id = %s
                        ORDER BY t.train_name
                    """, (to_id,))
                    trains = self.cursor.fetchall()
                elif to_id is None:
                    # Show trains from source
                    self.cursor.execute("""
                        SELECT DISTINCT t.train_no, t.train_name, t.type,
                               rs.departure_time, rs.arrival_time
                        FROM train t
                        JOIN route_station rs ON t.route_id = rs.route_id
                        WHERE rs.station_id = %s
                        ORDER BY t.train_name
                    """, (from_id,))
                    trains = self.cursor.fetchall()
                else:
                    # Normal search with both stations
                    self.cursor.callproc('search_trains', (from_id, to_id, travel_date))
                    for result in self.cursor.stored_results():
                        trains = result.fetchall()
                
                if not trains:
                    tk.Label(scrollable_frame, text="No trains found on this route.\nTry a different route or date.", 
                            font=('Arial', 12), bg='#f8f9fa', fg='#e74c3c', justify=tk.CENTER).pack(pady=30)
                    return
                
                # Radio button variable for train+class selection
                selection_var = tk.StringVar()
                
                for train in trains:
                    train_no, train_name, train_type, dept, arr = train
                    
                    # Get classes with seats
                    self.cursor.execute("""
                        SELECT c.class_id, c.class_name, c.coach_type, 
                               COALESCE(sa.available_seats, 0) as seats
                        FROM class c
                        LEFT JOIN seat_availability sa ON c.class_id = sa.class_id 
                            AND sa.train_no = c.train_no AND sa.travel_date = %s
                        WHERE c.train_no = %s AND COALESCE(sa.available_seats, 0) > 0
                        ORDER BY c.c_multiplier DESC
                    """, (travel_date, train_no))
                    
                    classes = self.cursor.fetchall()
                    
                    if not classes:
                        continue  # Skip trains with no available seats
                    
                    # Train card
                    train_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RIDGE, borderwidth=2)
                    train_card.pack(fill=tk.X, padx=10, pady=8)
                    
                    # Train header
                    header = tk.Frame(train_card, bg='#3498db', padx=10, pady=8)
                    header.pack(fill=tk.X)
                    
                    tk.Label(header, text=f"{train_name} ({train_no})", 
                            font=('Arial', 13, 'bold'), bg='#3498db', fg='white').pack(anchor=tk.W)
                    tk.Label(header, text=f"{train_type.upper()} | Departs: {dept} → Arrives: {arr}", 
                            font=('Arial', 10), bg='#3498db', fg='white').pack(anchor=tk.W)
                    
                    # Classes section
                    classes_frame = tk.Frame(train_card, bg='white', padx=10, pady=10)
                    classes_frame.pack(fill=tk.X)
                    
                    tk.Label(classes_frame, text="Available Classes:", 
                            font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(0,5))
                    
                    for cls in classes:
                        class_id, class_name, coach_type, seats = cls
                        
                        # Determine color based on seat availability
                        if seats > 50:
                            seat_color = '#27ae60'  # Green
                        elif seats > 20:
                            seat_color = '#f39c12'  # Orange
                        else:
                            seat_color = '#e74c3c'  # Red
                        
                        # Class radio button
                        class_frame = tk.Frame(classes_frame, bg='white')
                        class_frame.pack(fill=tk.X, pady=2)
                        
                        radio_value = f"{train_no}|{class_id}|{class_name}|{train_name}|{seats}"
                        
                        def make_selection_handler(val):
                            def handler():
                                parts = val.split('|')
                                selected_train['train_no'] = parts[0]
                                selected_train['class_id'] = parts[1]
                                selected_train['class_name'] = parts[2]
                                selected_train['train_name'] = parts[3]
                                selected_train['seats_available'] = int(parts[4])
                            return handler
                        
                        rb = tk.Radiobutton(class_frame, text=f"{class_name} ({coach_type})", 
                                          variable=selection_var, value=radio_value,
                                          font=('Arial', 10), bg='white', 
                                          command=make_selection_handler(radio_value))
                        rb.pack(side=tk.LEFT)
                        
                        tk.Label(class_frame, text=f"{seats} seats", 
                                font=('Arial', 10, 'bold'), bg='white', fg=seat_color).pack(side=tk.LEFT, padx=10)
                
            except mysql.connector.Error as err:
                tk.Label(scrollable_frame, text=f"Error: {err}", 
                        font=('Arial', 11), bg='#f8f9fa', fg='#e74c3c').pack(pady=20)
        
        # Action buttons
        action_frame = tk.Frame(container, bg='white')
        action_frame.pack(fill=tk.X, pady=(10,0))
        
        tk.Button(action_frame, text="🔍 Search Trains", font=('Arial', 12, 'bold'), 
                 bg='#3498db', fg='white', command=search_trains, width=20, height=2).pack(side=tk.LEFT, padx=5)
        
        def book_selected():
            """Book the selected train and class"""
            if not selected_train['train_no'] or not selected_train['class_id']:
                messagebox.showerror("Error", "Please select a train and class first!")
                return
            
            from_station_text = from_var.get()
            to_station_text = to_var.get()
            
            # Check if "Any Station" is selected
            if from_station_text == "-- Any Station --" or to_station_text == "-- Any Station --":
                messagebox.showerror("Error", 
                    "Please select specific source and destination stations to book a ticket.\n\n"
                    "'Any Station' can only be used for searching trains.")
                return
            
            # Check if enough seats available
            passengers = passenger_var.get()
            if passengers > selected_train['seats_available']:
                messagebox.showerror("Error", 
                    f"Only {selected_train['seats_available']} seats available!\n"
                    f"You selected {passengers} passengers.")
                return
            
            from_station = from_station_text.split('(')[0].strip()
            to_station = to_station_text.split('(')[0].strip()
            
            # Get station IDs
            self.cursor.execute("SELECT station_id FROM station WHERE station_name = %s", (from_station,))
            from_id_result = self.cursor.fetchone()
            self.cursor.execute("SELECT station_id FROM station WHERE station_name = %s", (to_station,))
            to_id_result = self.cursor.fetchone()
            
            if not from_id_result or not to_id_result:
                messagebox.showerror("Error", "Could not find station IDs")
                return
            
            from_id = from_id_result[0]
            to_id = to_id_result[0]
            
            try:
                # Book tickets for each passenger
                pnr_list = []
                for i in range(passengers):
                    # Generate unique PNR for each ticket
                    pnr = f"P{datetime.now().strftime('%m%d%H%M%S')}{i:02d}"[:15]
                    
                    # Book ticket
                    self.cursor.callproc('book_ticket', 
                        (pnr, selected_train['train_no'], self.current_user, from_id, to_id, 
                         date_var.get(), selected_train['class_id'], ''))
                    
                    pnr_list.append(pnr)
                
                # Update seat availability
                self.cursor.execute("""
                    UPDATE seat_availability 
                    SET available_seats = available_seats - %s 
                    WHERE train_no = %s AND class_id = %s AND travel_date = %s
                """, (passengers, selected_train['train_no'], selected_train['class_id'], date_var.get()))
                
                self.db.commit()
                
                pnr_text = ', '.join(pnr_list) if len(pnr_list) <= 3 else f"{pnr_list[0]} ... {pnr_list[-1]}"
                
                messagebox.showinfo("Success!", 
                    f"🎉 {passengers} Ticket(s) Booked!\n\n"
                    f"PNR(s): {pnr_text}\n"
                    f"Train: {selected_train['train_name']}\n"
                    f"Class: {selected_train['class_name']}\n"
                    f"From: {from_var.get()}\n"
                    f"To: {to_var.get()}\n"
                    f"Date: {date_var.get()}")
                
                book_win.destroy()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Booking failed: {err}")
                self.db.rollback()
        
        tk.Button(action_frame, text="✅ Book Now", font=('Arial', 12, 'bold'), 
                 bg='#27ae60', fg='white', command=book_selected, width=20, height=2).pack(side=tk.LEFT, padx=5)
    
    def view_bookings(self):
        """View user's booking history"""
        booking_win = tk.Toplevel(self.root)
        booking_win.title("My Bookings")
        booking_win.geometry("1000x500")
        booking_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(booking_win, bg='#ecf0f1', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="My Booking History", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        columns = ("PNR", "Train No", "Train Name", "Source", "Destination", 
                   "Travel Date", "Booking Time", "Fare", "Status")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=18)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        try:
            self.cursor.callproc('get_booking_history', (self.current_user,))
            
            for result in self.cursor.stored_results():
                bookings = result.fetchall()
                for booking in bookings:
                    tree.insert('', tk.END, values=booking)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def cancel_ticket(self):
        """Cancel a ticket"""
        cancel_win = tk.Toplevel(self.root)
        cancel_win.title("Cancel Ticket")
        cancel_win.geometry("500x400")
        cancel_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(cancel_win, bg='#34495e', padx=30, pady=30)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(frame, text="Cancel Ticket", font=('Arial', 18, 'bold'), 
                bg='#34495e', fg='white').pack(pady=20)
        
        # Get user's active bookings
        self.cursor.execute(
            """SELECT t.pnr_no, t.train_no, tr.train_name, t.travel_date, t.status 
               FROM ticket t 
               JOIN train tr ON t.train_no = tr.train_no 
               WHERE t.user_id = %s AND t.status = 'booked'
               ORDER BY t.travel_date""",
            (self.current_user,)
        )
        bookings = self.cursor.fetchall()
        
        if not bookings:
            tk.Label(frame, text="You have no active bookings to cancel.", 
                    font=('Arial', 12), bg='#34495e', fg='#ecf0f1').pack(pady=20)
            tk.Button(frame, text="Close", font=('Arial', 12, 'bold'), 
                     bg='#95a5a6', fg='white', width=15, 
                     command=cancel_win.destroy).pack(pady=10)
            return
        
        # PNR dropdown
        tk.Label(frame, text="Select Booking to Cancel:", font=('Arial', 12), 
                bg='#34495e', fg='white').pack(pady=5)
        booking_list = [f"{b[0]} - {b[2]} on {b[3]}" for b in bookings]
        booking_dict = {f"{b[0]} - {b[2]} on {b[3]}": b[0] for b in bookings}
        
        pnr_var = tk.StringVar()
        pnr_combo = ttk.Combobox(frame, textvariable=pnr_var, values=booking_list, 
                                font=('Arial', 10), width=40, state='readonly')
        pnr_combo.pack(pady=5)
        if booking_list:
            pnr_combo.set(booking_list[0])
        
        # Reason dropdown with common reasons
        tk.Label(frame, text="Reason for Cancellation:", font=('Arial', 12), 
                bg='#34495e', fg='white').pack(pady=(15,5))
        reasons = ["Change of plans", "Emergency", "Found better option", 
                  "Train timing not suitable", "Medical reasons", "Other"]
        reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(frame, textvariable=reason_var, values=reasons, 
                                   font=('Arial', 10), width=28)
        reason_combo.pack(pady=5)
        reason_combo.set(reasons[0])
        
        def confirm_cancel():
            pnr_text = pnr_var.get()
            reason = reason_var.get()
            
            if not pnr_text or not reason:
                messagebox.showerror("Error", "Please select a booking and reason")
                return
            
            pnr = booking_dict.get(pnr_text, '')
            
            # Show confirmation dialog
            confirm = messagebox.askyesno("Confirm Cancellation", 
                f"Are you sure you want to cancel this booking?\n\n"
                f"{pnr_text}\n\n"
                f"Reason: {reason}\n\n"
                f"A refund will be processed according to the cancellation policy.")
            
            if not confirm:
                return
            
            # Auto-generate cancel ID silently
            cancel_id = f"C{datetime.now().strftime('%d%H%M%S')}"
            
            try:
                result = self.cursor.callproc('cancel_ticket', (pnr, cancel_id, reason, ''))
                self.db.commit()
                messagebox.showinfo("Success", 
                    f"✅ Ticket cancelled successfully!\n\n"
                    f"Cancellation ID: {cancel_id}\n"
                    f"Refund will be processed to your account.")
                cancel_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
                self.db.rollback()
        
        tk.Button(frame, text="⚠️ Confirm Cancellation", font=('Arial', 12, 'bold'), 
                 bg='#e74c3c', fg='white', width=25, command=confirm_cancel).pack(pady=20)
    
    def view_stations(self):
        """View all stations"""
        station_win = tk.Toplevel(self.root)
        station_win.title("Stations")
        station_win.geometry("800x500")
        station_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(station_win, bg='#ecf0f1', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="All Stations", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        columns = ("Station ID", "Station Name", "City", "State")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        try:
            self.cursor.execute("SELECT * FROM station ORDER BY station_name")
            stations = self.cursor.fetchall()
            for station in stations:
                tree.insert('', tk.END, values=station)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def view_trains(self):
        """View all trains"""
        train_win = tk.Toplevel(self.root)
        train_win.title("Trains")
        train_win.geometry("900x500")
        train_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(train_win, bg='#ecf0f1', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="All Trains", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        columns = ("Train No", "Train Name", "Type", "Base Multiplier", "Route ID")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=170, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        try:
            self.cursor.execute("SELECT * FROM train ORDER BY train_name")
            trains = self.cursor.fetchall()
            for train in trains:
                tree.insert('', tk.END, values=train)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def view_payments(self):
        """View payment history"""
        payment_win = tk.Toplevel(self.root)
        payment_win.title("Payment History")
        payment_win.geometry("1000x500")
        payment_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(payment_win, bg='#ecf0f1', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Payment History", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        columns = ("Transaction ID", "PNR", "Amount", "Mode", "Status", "Date")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=18)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        try:
            self.cursor.execute(
                "SELECT transaction_id, pnr_no, amount, mode, status, transaction_date FROM payment WHERE user_id = %s ORDER BY transaction_date DESC",
                (self.current_user,)
            )
            payments = self.cursor.fetchall()
            for payment in payments:
                tree.insert('', tk.END, values=payment)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def view_train_status(self):
        """View train status"""
        status_win = tk.Toplevel(self.root)
        status_win.title("Train Status")
        status_win.geometry("900x500")
        status_win.configure(bg='#ecf0f1')
        
        frame = tk.Frame(status_win, bg='#ecf0f1', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Train Status", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        columns = ("Train No", "Date", "Current Station", "Delay (mins)", "Status")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=170, anchor=tk.CENTER)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        try:
            self.cursor.execute("SELECT * FROM train_status ORDER BY status_date DESC")
            statuses = self.cursor.fetchall()
            for status in statuses:
                tree.insert('', tk.END, values=status)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if self.db:
            self.cursor.close()
            self.db.close()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayManagementGUI(root)
    root.mainloop()
