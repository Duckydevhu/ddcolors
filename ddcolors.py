# A szükséges könyvtárak importálása
# tkinter - grafikus felhasználói felület (GUI) létrehozásához
import tkinter as tk
from tkinter import filedialog, messagebox
# filedialog: fájl párbeszédablakok kezelésére (pl. kép betöltése)
# messagebox: felugró információs és hibaüzenetek megjelenítésére

# PIL (Pillow) - képkezelési funkciókhoz
from PIL import Image, ImageTk
# Image: képek megnyitására, manipulálására (átméretezés, konvertálás)
# ImageTk: PIL képek konvertálása olyan formátumba, amit a tkinter is kezel

# numpy - hatékony numerikus számításokhoz, a képpontok feldolgozásához
import numpy as np

# scikit-learn - gépi tanulási könyvtár
from sklearn.cluster import MiniBatchKMeans
# MiniBatchKMeans: egy klaszterező algoritmus, ami a KMeans egy memóriahatékonyabb változata.
# Különösen hasznos nagy képek feldolgozásánál, mert nem kell az összes adatot egyszerre a memóriába tölteni.

# os - operációs rendszerrel kapcsolatos műveletekhez (pl. fájl elérhetőségének ellenőrzése)
import os

# Az alkalmazás fő osztálya, ami az egész program logikáját tartalmazza.
class ImageColorApp:
    
    # Konstruktor: az alkalmazás inicializálása
    def __init__(self, root):
        # A fő ablak (root) mentése az osztály egy attribútumába
        self.root = root
        
        # Ablak címének és méretének beállítása
        self.root.title("Kép szín elemző")
        self.root.geometry("1200x800")
        
        # IKON BEÁLLÍTÁSA
        # Ellenőrzi, hogy létezik-e az 'icon.ico' nevű fájl,
        # és ha igen, beállítja az ablak ikonjának.
        if os.path.exists("icon.ico"):
            self.root.iconbitmap("icon.ico")
        
        # Változók inicializálása a kép és a nézetkezelés (zoom, mozgatás) tárolására
        self.original_image = None
        self.current_image = None
        self.photo_image = None
        
        # Változók a kép nagyításához és mozgatásához
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_x = 0
        self.last_y = 0

        self.pixel_data = None
        self.current_image_path = ""
        
        # Változók a felhasználó által gyűjtött színekhez
        self.custom_palette_colors = []
        self.picked_color_code = None
        
        # A felhasználói felület (UI) felépítésének elindítása
        self.setup_ui()

    # --- UI RÉSZ ---
    
    # A felhasználói felület elemeinek elhelyezése és beállítása
    def setup_ui(self):
        # Fő keret létrehozása, ami a bal oldali panelt és a képnézegetőt tartalmazza
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bal oldali panel, ami a vezérlőket tartalmazza
        left_panel = tk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Kép betöltése gomb
        btn_load = tk.Button(left_panel, text="Kép betöltése", command=self.load_image)
        btn_load.pack(side=tk.TOP, pady=5, fill=tk.X)
        
        # Színválasztó szekció
        color_picker_frame = tk.LabelFrame(left_panel, text="Színválasztó")
        color_picker_frame.pack(fill=tk.X, pady=5)
        self.lbl_picked_color = tk.Label(color_picker_frame, text="", width=2, bg="white")
        self.lbl_picked_color.pack(side=tk.LEFT, pady=5, padx=5, fill=tk.Y)
        
        # Színkódok (RGB, HEX) megjelenítése
        self.picked_color_code_frame = tk.Frame(color_picker_frame)
        self.picked_color_code_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_color_codes = tk.Label(self.picked_color_code_frame, text="RGB: \nHEX: ")
        self.lbl_color_codes.pack(side=tk.LEFT, padx=5)
        self.btn_copy_hex = tk.Button(self.picked_color_code_frame, text="Másolás", command=self.copy_hex_picker)
        self.btn_copy_hex.pack(side=tk.RIGHT, padx=5)
        
        # Saját paletta szekció
        custom_palette_frame = tk.LabelFrame(left_panel, text="Saját paletta")
        custom_palette_frame.pack(fill=tk.X, pady=5)
        
        self.custom_palette_buttons_frame = tk.Frame(custom_palette_frame)
        self.custom_palette_buttons_frame.pack(fill=tk.X)
        
        self.btn_add_to_custom = tk.Button(self.custom_palette_buttons_frame, text="Hozzáadás", command=self.add_to_custom_palette)
        self.btn_add_to_custom.pack(side=tk.LEFT, pady=5, padx=5, expand=True)
        self.btn_show_custom = tk.Button(self.custom_palette_buttons_frame, text="Paletta", command=self.show_custom_palette)
        self.btn_show_custom.pack(side=tk.LEFT, pady=5, padx=5, expand=True)
        self.btn_clear_custom = tk.Button(self.custom_palette_buttons_frame, text="Törlés", command=self.clear_custom_palette)
        self.btn_clear_custom.pack(side=tk.LEFT, pady=5, padx=5, expand=True)
        
        # Generált színpaletta szekció
        palette_frame = tk.LabelFrame(left_panel, text="Színpaletta")
        palette_frame.pack(fill=tk.X, pady=5)
        self.palette_scale = tk.Scale(palette_frame, from_=2, to=32, orient=tk.HORIZONTAL, label="Színek száma")
        self.palette_scale.set(8) # Alapértelmezett érték 8
        self.palette_scale.pack(fill=tk.X, padx=5)
        
        btn_generate_palette = tk.Button(palette_frame, text="Paletta generálása", command=self.generate_palette)
        btn_generate_palette.pack(side=tk.LEFT, pady=5, padx=5, expand=True, fill=tk.X)
        
        btn_show_top_colors = tk.Button(palette_frame, text="Top 10 szín", command=self.analyze_colors)
        btn_show_top_colors.pack(side=tk.RIGHT, pady=5, padx=5, expand=True, fill=tk.X)
        
        # Eredmények konténere (leggyakoribb színek, saját paletta)
        result_container = tk.LabelFrame(left_panel, text="Eredmények")
        result_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas és görgetősáv az eredményekhez, ha azok nem férnek el
        self.result_canvas = tk.Canvas(result_container)
        self.result_frame = tk.Frame(self.result_canvas)
        self.scrollbar = tk.Scrollbar(result_container, orient="vertical", command=self.result_canvas.yview)
        self.result_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.result_canvas.pack(side="left", fill="both", expand=True)
        self.result_canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        # Ez a sor dinamikusan frissíti a görgetősávot, ha az eredmények száma megváltozik
        self.result_frame.bind("<Configure>", lambda event, canvas=self.result_canvas: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Mentés gombok
        save_button_frame = tk.Frame(left_panel)
        save_button_frame.pack(fill=tk.X, pady=5)
        btn_save_txt = tk.Button(save_button_frame, text="Mentés TXT-be", command=lambda: self.save_results("txt"))
        btn_save_txt.pack(side=tk.LEFT, expand=True, padx=5)
        btn_save_html = tk.Button(save_button_frame, text="Mentés HTML-be", command=lambda: self.save_results("html"))
        btn_save_html.pack(side=tk.RIGHT, expand=True, padx=5)
        
        # Fő canvas a kép megjelenítéséhez
        self.canvas = tk.Canvas(main_frame, width=900, height=780, bg="lightgrey",
                                 borderwidth=2, relief="sunken")
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Eseménykezelők a nagyításhoz (görgetőkerék), mozgatáshoz (jobb klikk) és színválasztáshoz (bal klikk)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-3>", self.pan_start)
        self.canvas.bind("<B3-Motion>", self.pan_move)
        self.canvas.bind("<Button-1>", self.get_pixel_color)
        
    def show_status(self, message):
        # Ez a funkció jelenleg nem csinál semmit, de egy lehetséges
        # hely a jövőbeli állapotüzenetek (pl. "Feldolgozás...") kiírására.
        pass
        
    # --- KÉP KEZELŐ FÜGGVÉNYEK ---
    
    # Fájl megnyitása párbeszédablak a kép betöltéséhez
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Képek", "*.jpg *.jpeg *.bmp *.png *.webp *.tiff")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image_path = file_path
                self.analyze_colors() # Automatikusan elemzi a top 10 színt
                self.reset_view() # Visszaállítja a nagyítást és a pozíciót
            except Exception as e:
                messagebox.showerror("Hiba", f"Nem sikerült betölteni a képet: {e}")

    # A nézet alaphelyzetbe állítása a kép betöltésekor
    def reset_view(self):
        img_width, img_height = self.original_image.size
        max_size = 900
        # A kép átméretezése, ha túl nagy, hogy elférjen a canvas-on
        if img_width > max_size or img_height > max_size:
            self.current_image = self.original_image.copy()
            self.current_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        else:
            self.current_image = self.original_image.copy()
        
        # A kép konvertálása tkinter-kompatibilis formátumra
        self.photo_image = ImageTk.PhotoImage(self.current_image)
        self.canvas.delete("all")
        # Kép elhelyezése a canvas közepén
        self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, 
                                 anchor=tk.CENTER, image=self.photo_image)
        
        # Nagyítási és mozgatási paraméterek alaphelyzetbe állítása
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        
        # A görgetősáv határainak beállítása (bár a nagyítás/mozgatás miatt ez itt nem teljesen kihasznált)
        self.canvas.config(scrollregion=(0, 0, self.current_image.width, self.current_image.height))

    # --- SZÍN ELEMZŐ FÜGGVÉNYEK ---
    
    # A 10 leggyakoribb szín elemzése MiniBatchKMeans-szel
    def analyze_colors(self):
        if not self.original_image:
            return
        
        # A kép konvertálása RGB módba, ha szükséges
        if self.original_image.mode != "RGB":
            rgb_image = self.original_image.convert("RGB")
        else:
            rgb_image = self.original_image

        # A képpontokból egy NumPy tömböt hoz létre, ahol minden sor egy képpontot (R,G,B) jelöl
        pixels = np.array(rgb_image).reshape(-1, 3)
        
        # MiniBatchKMeans modell inicializálása és illesztése 10 klaszterre
        kmeans = MiniBatchKMeans(n_clusters=10, random_state=0, n_init=3)
        kmeans.fit(pixels)
        # A klaszterek középpontjai a leggyakoribb színek, egész számokká alakítva
        top_10_colors = kmeans.cluster_centers_.astype(int)
        
        # Az eredmények megjelenítése a felületen
        self.display_results("A 10 leggyakoribb szín:", top_10_colors)

    # Az elemzési eredmények (színek) megjelenítése a bal oldali panelen
    def display_results(self, title, colors):
        # Előző eredmények törlése a framből
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Cím megjelenítése
        title_label = tk.Label(self.result_frame, text=title, anchor="w", font=("Arial", 10, "bold"))
        title_label.pack(fill=tk.X, padx=5, pady=(5,0))
        
        # Minden színhez létrehoz egy külön sávot
        for rgb_color in colors:
            rgb_code = tuple(map(int, rgb_color))
            hex_code = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
            
            color_row = tk.Frame(self.result_frame)
            color_row.pack(fill=tk.X, padx=5, pady=2)
            
            # Színes négyzet megjelenítése
            color_box = tk.Label(color_row, bg=hex_code, width=4, height=1)
            color_box.pack(side=tk.LEFT, fill=tk.Y)
            
            # RGB és HEX kódok szövegként
            color_labels = tk.Label(color_row, text=f"RGB: {rgb_code}\nHEX: {hex_code}", anchor="w", justify=tk.LEFT)
            color_labels.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Másolás gomb a HEX kódhoz
            btn_copy = tk.Button(color_row, text="Másolás", command=lambda hex_val=hex_code: self.copy_to_clipboard(hex_val))
            btn_copy.pack(side=tk.RIGHT)
            
            # Ha a saját palettát jeleníti meg, hozzáad egy törlés gombot
            if title.startswith("Saját paletta"):
                btn_delete = tk.Button(color_row, text="x", command=lambda color=rgb_color: self.remove_from_custom_palette(color))
                btn_delete.pack(side=tk.RIGHT, padx=(5, 0))

    # Egy képpont színének lekérdezése kattintásra
    def get_pixel_color(self, event):
        if not self.original_image:
            return
        
        # A kattintás pozíciójának átváltása a canvas koordinátáiból az eredeti kép koordinátáira
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Korrigált pozíció a nagyítás és mozgatás miatt
        zoomed_x = event.x - (canvas_width / 2) - self.pan_x
        zoomed_y = event.y - (canvas_height / 2) - self.pan_y
        
        # Visszaállítás az eredeti képméretre
        original_x = int(zoomed_x / self.zoom_level + self.original_image.width / 2)
        original_y = int(zoomed_y / self.zoom_level + self.original_image.height / 2)
        
        # Ellenőrzi, hogy a kattintás a kép határain belül van-e
        if 0 <= original_x < self.original_image.width and 0 <= original_y < self.original_image.height:
            # Lekéri a képpont színét
            rgb_color = self.original_image.getpixel((original_x, original_y))
            # Konvertálja a színt HEX formátumra
            hex_color = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
            
            # Frissíti a színválasztó panelen a színt és a kódokat
            self.lbl_picked_color.config(bg=hex_color)
            self.lbl_color_codes.config(text=f"RGB: {rgb_color}\nHEX: {hex_color}")
            self.picked_color_code = (rgb_color, hex_color)
    
    # --- PALETTA KEZELŐ FÜGGVÉNYEK ---
    
    # Kiválasztott szín hozzáadása a saját palettához
    def add_to_custom_palette(self):
        if self.picked_color_code:
            rgb_color, hex_code = self.picked_color_code
            # Ellenőrzi, hogy a szín még nem szerepel a palettán
            if hex_code not in [c[1] for c in self.custom_palette_colors]:
                self.custom_palette_colors.append((rgb_color, hex_code))
                self.show_custom_palette() # Frissíti a kijelzőt
            else:
                messagebox.showinfo("Információ", "Ez a szín már szerepel a palettán.")
        else:
            messagebox.showinfo("Információ", "Kérlek, válassz ki egy színt a képből!")

    # Szín eltávolítása a saját palettáról
    def remove_from_custom_palette(self, color_to_remove):
        # List comprehension segítségével szűri a listát
        self.custom_palette_colors = [c for c in self.custom_palette_colors if not np.array_equal(c[0], color_to_remove)]
        self.show_custom_palette()

    # Saját paletta megjelenítése
    def show_custom_palette(self):
        if not self.custom_palette_colors:
            messagebox.showinfo("Információ", "A saját paletta üres. Válassz ki színeket!")
            return
        
        # Csak az RGB kódokat adja át a display_results függvénynek
        colors = [c[0] for c in self.custom_palette_colors]
        self.display_results("Saját paletta:", colors)

    # Saját paletta tartalmának törlése
    def clear_custom_palette(self):
        self.custom_palette_colors = []
        self.display_results("Saját paletta:", [])
    
    # Színválasztó HEX kódjának másolása
    def copy_hex_picker(self):
        if hasattr(self, 'picked_color_code') and self.picked_color_code:
            self.copy_to_clipboard(self.picked_color_code[1])
        else:
            messagebox.showinfo("Információ", "Nincs kiválasztott szín a másoláshoz.")
    
    # Általános funkció a szöveg vágólapra másolásához
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    # Színpaletta generálása a csúszka értékének megfelelően
    def generate_palette(self):
        if not self.original_image:
            messagebox.showinfo("Információ", "Kérlek, tölts be egy képet a paletta generálásához.")
            return

        n_colors = self.palette_scale.get()
        
        # Hasonló logika, mint az analyze_colors() függvényben, de a klaszterek száma most a csúszka értéke
        pixels = np.array(self.original_image).reshape(-1, 3)
        
        kmeans = MiniBatchKMeans(n_clusters=n_colors, random_state=0, n_init=3)
        kmeans.fit(pixels)
        
        palette_colors = kmeans.cluster_centers_.astype(int)
        
        self.display_results(f"Generált színpaletta ({n_colors} szín):", palette_colors)

    # --- MENTÉS KEZELŐ FÜGGVÉNYEK ---
    
    # Az eredmények mentése TXT vagy HTML formátumba
    def save_results(self, file_format):
        results_text = self.get_results_text_to_save()
        
        if not results_text.strip():
            messagebox.showinfo("Információ", "Nincsenek eredmények a mentéshez.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{file_format}",
            filetypes=[("Szöveges fájlok", "*.txt")] if file_format == "txt" else [("HTML fájlok", "*.html")]
        )
        
        if file_path:
            try:
                if file_format == "html":
                    # HTML mentéshez külön kell kinyerni a színeket
                    self.save_as_html(file_path, self.get_colors_from_results())
                else:
                    self.save_as_txt(file_path, results_text)

                messagebox.showinfo("Siker", f"Eredmények sikeresen elmentve {file_path}-ként!")
            except Exception as e:
                messagebox.showerror("Hiba", f"Nem sikerült a mentés: {e}")

    # A menteni kívánt színek listájának kinyerése
    def get_colors_from_results(self):
        colors_to_save = []
        # Ellenőrzi, hogy van-e valami a result_frame-ben
        if not self.result_frame.winfo_children() or len(self.result_frame.winfo_children()) < 2:
            return colors_to_save

        title_label = self.result_frame.winfo_children()[0]
        # Ha a saját palettát jeleníti meg, a saját listából dolgozik
        if title_label.cget("text").startswith("Saját paletta"):
            colors_to_save = [{'rgb': c[0], 'hex': c[1]} for c in self.custom_palette_colors]
        else:
            # Különben a jelenleg kijelzett widgetekből olvassa ki az adatokat
            for widget in self.result_frame.winfo_children()[1:]:
                if isinstance(widget, tk.Frame):
                    labels = widget.winfo_children()
                    if len(labels) >= 2:
                        rgb_text = labels[1].cget("text").split("RGB: ")[-1].split(")")[0]
                        hex_text = labels[1].cget("text").split("HEX: ")[-1]
                        
                        rgb = tuple(map(int, rgb_text.replace('(', '').strip().split(',')))
                        hex_code = hex_text.strip()
                        colors_to_save.append({'rgb': rgb, 'hex': hex_code})
        return colors_to_save

    # A menteni kívánt szöveg kinyerése
    def get_results_text_to_save(self):
        if not self.result_frame.winfo_children() or len(self.result_frame.winfo_children()) < 2:
            return ""
        
        title_label = self.result_frame.winfo_children()[0]
        if title_label.cget("text").startswith("Saját paletta"):
            return "Saját paletta:\n" + "\n".join([f"RGB: {c[0]}, HEX: {c[1]}" for c in self.custom_palette_colors])
        else:
            text_lines = []
            for widget in self.result_frame.winfo_children()[1:]:
                if isinstance(widget, tk.Frame):
                    labels = widget.winfo_children()
                    if len(labels) >= 2:
                        text_lines.append(labels[1].cget("text"))
            return title_label.cget("text") + "\n" + "\n".join(text_lines)

    # Eredmények mentése sima szöveges fájlként
    def save_as_txt(self, file_path, text):
        with open(file_path, "w") as f:
            f.write(text)

    # Eredmények mentése HTML fájlként stílusos megjelenítéssel
    def save_as_html(self, file_path, colors):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Színpaletta</title>
        <style>
        body { font-family: sans-serif; padding: 20px; }
        h1 { color: #333; }
        .color-palette { display: flex; flex-wrap: wrap; gap: 20px; }
        .color-box {
            width: 150px;
            height: 150px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            padding: 10px;
        }
        .color-code {
            margin-top: 10px;
            font-weight: bold;
        }
        </style>
        </head>
        <body>
        <h1>Színpaletta</h1>
        <div class="color-palette">
        """
        for color in colors:
            html_content += f"""
            <div class="color-box" style="background-color: {color['hex']};">
                <div class="color-code">HEX: {color['hex']}</div>
                <div class="color-code">RGB: {color['rgb']}</div>
            </div>
            """
        
        html_content += """
        </div>
        </body>
        </html>
        """
        with open(file_path, "w") as f:
            f.write(html_content)

    # --- KÉP NAGYÍTÁSA ÉS MOZGATÁSA ---
    
    # Nagyítás (zoom) görgővel
    def zoom(self, event):
        if not self.original_image:
            return

        # A nagyítás irányának meghatározása
        if event.delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level /= 1.1

        # A nagyítási szint korlátozása
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
        self.update_canvas()

    # Mozgatás (pan) kezdete a jobb egérgomb lenyomására
    def pan_start(self, event):
        self.last_x = event.x
        self.last_y = event.y

    # Mozgatás folytatása a jobb egérgomb lenyomva tartása alatt
    def pan_move(self, event):
        if not self.original_image:
            return
        
        # Az egér elmozdulásának kiszámítása
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        # A kép eltolásának frissítése
        self.pan_x += dx
        self.pan_y += dy
        
        # A pillanatnyi pozíció mentése a következő lépéshez
        self.last_x = event.x
        self.last_y = event.y
        
        self.update_canvas()

    # A canvas frissítése a nagyítás és a mozgatás hatására
    def update_canvas(self):
        if not self.original_image:
            return

        new_size = (int(self.original_image.width * self.zoom_level),
                    int(self.original_image.height * self.zoom_level))
        
        if new_size[0] > 0 and new_size[1] > 0:
            # Az eredeti kép átméretezése az aktuális zoom szint szerint
            self.current_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(self.current_image)
            self.canvas.delete("all")
            # A kép elhelyezése az új pozíción
            self.canvas.create_image(self.canvas.winfo_width() / 2 + self.pan_x,
                                     self.canvas.winfo_height() / 2 + self.pan_y,
                                     anchor=tk.CENTER, image=self.photo_image)

# Fő végrehajtási blokk
if __name__ == "__main__":
    # Fő ablak létrehozása
    root = tk.Tk()
    # Az alkalmazás osztályának példányosítása, ami elindítja a GUI-t
    app = ImageColorApp(root)
    # Az eseményhurok elindítása, ami figyeli a felhasználó interakcióit
    root.mainloop()