import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from tkinter import Canvas
import os

class Pokemon:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex")
        self.root.geometry("500x700")
        self.root.configure(bg='#DE082E')
        self.pokemon_cache = {}
        self.current_pokemon = None 
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#DE082E', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Logo - with fallback if image doesn't exist
        try:
            if os.path.exists("pokeee.png"):
                logo = Image.open("pokeee.png")
                logo = logo.resize((257, 103))   
                self.logo_img = ImageTk.PhotoImage(logo)
                logo_label = tk.Label(main_frame, image=self.logo_img, bg='#DE082E')
            else:
                # Fallback text logo
                logo_label = tk.Label(main_frame, text="POKÉDEX", 
                                    font=('Arial', 24, 'bold'), 
                                    fg='white', bg='#DE082E')
        except Exception:
            logo_label = tk.Label(main_frame, text="POKÉDEX", 
                                font=('Arial', 24, 'bold'), 
                                fg='white', bg='#DE082E')
        
        logo_label.pack(pady=10)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#DE082E')
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(search_frame, text="Search Pokémon:", 
                font=('Sans-serif', 12), fg='white', bg='#DE082E').pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 12), width=15)
        search_entry.pack(side='left', padx=(10, 5))
        search_entry.bind('<Return>', self.search_pokemon)
        
        search_btn = tk.Button(search_frame, text="Search", 
                              command=self.search_pokemon,
                              bg='#FFD700', fg='black', font=('Arial', 10, 'bold'))
        search_btn.pack(side='left', padx=(5, 0))
        
        # Main display area
        display_frame = tk.Frame(main_frame, bg='#1E90FF', relief='raised', bd=3)
        display_frame.pack(fill='both', expand=True)
        
        # Pokemon image
        self.image_label = tk.Label(display_frame, bg='#1E90FF', 
                                   text="Search for a Pokémon!", 
                                   font=('Arial', 14), fg='white')
        self.image_label.pack(pady=20)
        
        # Pokemon name and ID
        self.name_label = tk.Label(display_frame, text="", 
                                  font=('Arial', 18, 'bold'), 
                                  fg='white', bg='#1E90FF')
        self.name_label.pack()
        
        self.id_label = tk.Label(display_frame, text="", 
                                font=('Arial', 12), 
                                fg='white', bg='#1E90FF')
        self.id_label.pack()
        
        # Type display
        self.type_label = tk.Label(display_frame, text="", 
                                  font=('Arial', 12, 'bold'), 
                                  fg='white', bg='#1E90FF')
        self.type_label.pack(pady=5)
        
        # Stats frame
        stats_frame = tk.LabelFrame(display_frame, text="Base Stats", 
                                   font=('Arial', 12, 'bold'), 
                                   fg='white', bg='#1E90FF')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Create stats labels
        self.stats_labels = {}
        stats = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
        for i, stat in enumerate(stats):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(stats_frame, bg='#1E90FF')
            frame.grid(row=row, column=col, sticky='w', padx=10, pady=2)
            
            tk.Label(frame, text=f"{stat}:", font=('Arial', 9), 
                    fg='white', bg='#1E90FF', width=10, anchor='w').pack(side='left')
            self.stats_labels[stat.lower().replace(' ', '_').replace('.', '')] = tk.Label(
                frame, text="", font=('Arial', 9, 'bold'), fg='yellow', bg='#1E90FF')
            self.stats_labels[stat.lower().replace(' ', '_').replace('.', '')].pack(side='left')
        
        # Physical info frame
        info_frame = tk.Frame(display_frame, bg='#1E90FF')
        info_frame.pack(pady=10)
        
        # Height and Weight
        hw_frame = tk.Frame(info_frame, bg='#1E90FF')
        hw_frame.pack()
        
        self.height_label = tk.Label(hw_frame, text="", font=('Arial', 10), 
                                    fg='white', bg='#1E90FF')
        self.height_label.pack(side='left', padx=10)
        
        self.weight_label = tk.Label(hw_frame, text="", font=('Arial', 10), 
                                    fg='white', bg='#1E90FF')
        self.weight_label.pack(side='left', padx=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(main_frame, bg='#DE082E')
        nav_frame.pack(fill='x', pady=(10, 0))
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Previous", 
                                 command=self.previous_pokemon,
                                 bg='#FFD700', fg='black', font=('Arial', 10, 'bold'),
                                 state='disabled')
        self.prev_btn.pack(side='left')
        
        self.random_btn = tk.Button(nav_frame, text="Random", 
                                   command=self.random_pokemon,
                                   bg='#32CD32', fg='white', font=('Arial', 10, 'bold'))
        self.random_btn.pack(side='left', padx=(10, 0))
        
        self.next_btn = tk.Button(nav_frame, text="Next ▶", 
                                 command=self.next_pokemon,
                                 bg='#FFD700', fg='black', font=('Arial', 10, 'bold'),
                                 state='disabled')
        self.next_btn.pack(side='right')
        
        # Load a default Pokemon
        self.load_pokemon_async("pikachu")
    
    def search_pokemon(self, event=None):
        query = self.search_var.get().strip().lower()
        if query:
            self.load_pokemon_async(query)
        else:
            messagebox.showwarning("Warning", "Please enter a Pokémon name or ID!")
    
    def load_pokemon_async(self, pokemon_id):
        """Load Pokémon data in a separate thread to prevent GUI freezing"""
        thread = threading.Thread(target=self.load_pokemon, args=(pokemon_id,))
        thread.daemon = True
        thread.start()
    
    def load_pokemon(self, pokemon_id):
        try:
            # Show loading state
            self.root.after(0, self.show_loading)
            
            # Check cache first
            cache_key = str(pokemon_id).lower()
            if cache_key in self.pokemon_cache:
                pokemon_data = self.pokemon_cache[cache_key]
            else:
                # Fetch from API
                url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                pokemon_data = response.json()
                self.pokemon_cache[cache_key] = pokemon_data
            
            self.current_pokemon = pokemon_data
            
            # Update UI in main thread
            self.root.after(0, self.update_pokemon_display, pokemon_data)
            
        except requests.exceptions.RequestException:
            self.root.after(0, self.show_error, "Failed to connect to Pokémon API. Check your internet connection.")
        except Exception as e:
            self.root.after(0, self.show_error, f"Pokémon '{pokemon_id}' not found!")
    
    def show_loading(self):
        self.image_label.config(text="Loading...", image='')
        self.name_label.config(text="Loading...")
        
    def show_error(self, message):
        self.image_label.config(text="No image available", image='')
        self.name_label.config(text="Error")
        self.id_label.config(text="")
        self.type_label.config(text="")
        messagebox.showerror("Error", message)
    
    def update_pokemon_display(self, pokemon_data):
        try:
            # Update name and ID
            name = pokemon_data['name'].title()
            pokemon_id = pokemon_data['id']
            self.name_label.config(text=name)
            self.id_label.config(text=f"#{pokemon_id:03d}")
            
            # Update types
            types = [type_info['type']['name'].title() for type_info in pokemon_data['types']]
            type_colors = {
                'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0',
                'Electric': '#F8D030', 'Grass': '#78C850', 'Ice': '#98D8D8',
                'Fighting': '#C03028', 'Poison': '#A040A0', 'Ground': '#E0C068',
                'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
                'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8',
                'Dark': '#705848', 'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
            }
            type_text = " / ".join(types)
            self.type_label.config(text=f"Type: {type_text}")
            
            # Update stats
            for stat_info in pokemon_data['stats']:
                stat_name = stat_info['stat']['name'].replace('-', '_')
                if stat_name == 'special_attack':
                    stat_name = 'sp_attack'
                elif stat_name == 'special_defense':
                    stat_name = 'sp_defense'
                
                if stat_name in self.stats_labels:
                    self.stats_labels[stat_name].config(text=str(stat_info['base_stat']))
            
            # Update physical characteristics
            height = pokemon_data['height'] / 10  # Convert to meters
            weight = pokemon_data['weight'] / 10  # Convert to kg
            self.height_label.config(text=f"Height: {height:.1f} m")
            self.weight_label.config(text=f"Weight: {weight:.1f} kg")
            
            # Load and display image
            self.load_pokemon_image(pokemon_data['sprites']['front_default'])
            
            # Enable navigation buttons
            self.prev_btn.config(state='normal' if pokemon_id > 1 else 'disabled')
            self.next_btn.config(state='normal' if pokemon_id < 1010 else 'disabled')
            
            # Clear search box
            self.search_var.set("")
            
        except Exception as e:
            self.show_error(f"Error displaying Pokémon data: {str(e)}")
    
    def load_pokemon_image(self, image_url):
        """Load Pokémon image from URL"""
        try:
            if image_url:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            else:
                self.image_label.config(text="No image available", image='')
        except Exception:
            self.image_label.config(text="Image not available", image='')
    
    def previous_pokemon(self):
        if self.current_pokemon and self.current_pokemon['id'] > 1:
            self.load_pokemon_async(str(self.current_pokemon['id'] - 1))
    
    def next_pokemon(self):
        if self.current_pokemon and self.current_pokemon['id'] < 1010:
            self.load_pokemon_async(str(self.current_pokemon['id'] + 1))
    
    def random_pokemon(self):
        import random
        random_id = random.randint(1, 1010)
        self.load_pokemon_async(str(random_id))

def main():
    root = tk.Tk()
    app = Pokemon(root)
    root.mainloop()

if __name__ == "__main__":
    main()