import numpy as np
import time
import random
import tkinter as tk
from tkinter import messagebox, filedialog, Text, END
import itertools 

class DuplicatedCoordinateException(Exception): 
    pass # Exception yang muncul jika ada koordinat yang sama di dua Path.

class Path():
    def __init__(self, coords=[]):
        # Inisialisasi objek Path. Parameter yang diperlukan adalah coords (koordinat), 
        # yang merupakan list dari koordinat path.
        self.coords = coords

    def __add__(self, other):
        # Menambahkan dua objek Path. 
        # Jika ada koordinat yang sama di kedua Path, maka akan muncul DuplicatedCoordinateException.
        new_coords = self.coords + other.coords
        if any(map(lambda coord: coord in self.coords, other.coords)):
            raise DuplicatedCoordinateException()
        return Path(new_coords)

    def __repr__(self):
        # Merepresentasi string dari objek Path. 
        # Ini akan mengembalikan string dari list koordinat path.
        return '\n'.join([f"{col}, {row}" for row, col in self.coords])

class SequenceScore():
    def __init__(self, sequence, buffer_size, sequence_score, reward_level=0):
        # Inisialisasi objek SequenceScore. Parameter yang diperlukan adalah sequence (urutan angka),
        # buffer_size (ukuran maksimum sequence), sequence_score (skor untuk sequence), dan reward_level (level reward).
        self.max_progress = len(sequence)
        self.sequence = sequence
        self.score = 0
        self.reward_level = reward_level
        self.buffer_size = buffer_size
        self.sequence_score = sequence_score

    def compute(self, compare):
        # Menghitung skor sequence. Parameter yang diperlukan adalah compare (angka untuk dibandingkan
        # dengan angka saat ini dalam sequence). Jika angka cocok, metode __increase dipanggil. Jika tidak, metode __decrease dipanggil.
        if not self.__completed():
            if self.sequence[self.score] == compare:
                self.__increase()
            else:
                self.__decrease()

    def __increase(self):
        # Meningkatkan skor jika angka dalam sequence cocok. Jika sequence selesai, 
        # skor diatur ke sequence_score.
        self.buffer_size -= 1
        self.score += 1
        if self.__completed():
            self.score = self.sequence_score
            
    def __decrease(self):
        # Mengurangi skor jika angka dalam sequence tidak cocok. Jika sequence selesai,
        # skor diatur ke 0.
        self.buffer_size -= 1
        if self.score > 0:
            self.score -= 1
        if self.__completed():
            self.score = 0

    def __completed(self):
        # Memeriksa apakah sequence selesai. Sequence dianggap selesai jika skor kurang dari 0,
        # skor lebih besar atau sama dengan progress maksimum, atau buffer_size kurang dari progress maksimum dikurangi skor.
        return self.score < 0 or self.score >= self.max_progress or self.buffer_size < self.max_progress - self.score

class PathScore():
    def __init__(self, path, sequences, buffer_size, code_matrix):
        # Inisialisasi objek PathScore. Parameter yang diperlukan adalah path (jalur), sequences (urutan sequence),
        # buffer_size (ukuran maksimum sequence), dan code_matrix (matriks kode).
        self.score = None
        self.path = path
        self.code_matrix = code_matrix
        self.sequence_scores = [SequenceScore(sequence, buffer_size, score, reward_level) for reward_level, (sequence, score) in enumerate(sequences)]

    def compute(self):
         # Menghitung skor total untuk path. Skor total adalah jumlah skor semua sequence. 
        if self.score != None:
            return self.score
        for row, column in self.path.coords:
            for seq_score in self.sequence_scores:
                seq_score.compute(self.code_matrix[row-1][column-1])
        self.score = sum(map(lambda seq_score: seq_score.score, self.sequence_scores))
        return self.score

def generate_paths(buffer_size, code_matrix):
    # Fungsi ini digunakan untuk menghasilkan semua path yang mungkin. Parameter yang diperlukan adalah buffer_size (ukuran maksimum sequence)
    # dan code_matrix (matriks kode).

    completed_paths = []

    def candidate_coords(code_matrix, turn=0, coordinate=(1,1)):
        # Fungsi ini digunakan untuk menghasilkan koordinat kandidat untuk langkah selanjutnya. Parameter yang diperlukan adalah code_matrix (matriks kode),
        # turn (giliran), dan coordinate (koordinat).
        if turn % 2 == 0:
            return [(coordinate[0], column) for column in range(1, len(code_matrix)+1)]
        else:
            return [(row, coordinate[1]) for row in range(1, len(code_matrix)+1)]

    def _walk_paths(buffer_size, completed_paths, partial_paths_stack = [Path()], turn = 0, candidates = candidate_coords(code_matrix)):
        # Fungsi ini digunakan untuk berjalan melalui semua path yang mungkin dan menyimpan path yang selesai. Parameter yang diperlukan adalah buffer_size (ukuran maksimum sequence),
        # completed_paths (path yang selesai), partial_paths_stack (stack path parsial), turn (giliran), dan candidates (kandidat).
        path = partial_paths_stack.pop()
        for coord in candidates:
            try:
                new_path = path + Path([coord])
            except DuplicatedCoordinateException:
                continue

            if len(new_path.coords) == buffer_size:
                completed_paths.append(new_path) 

            else: 
                partial_paths_stack.append(new_path)  
                _walk_paths(buffer_size, completed_paths, partial_paths_stack, turn + 1, candidate_coords(code_matrix, turn + 1, coord))

    _walk_paths(buffer_size, completed_paths)

    return completed_paths
    # Mengembalikan semua path yang selesai.
    

def run_program_keyboard():
    # Fungsi ini digunakan untuk menjalankan program dengan input dari keyboard.
    
    # Membuat entry untuk input
    num_token_types_entry = tk.Entry(root)
    num_token_types_entry.pack()

    token_types_entry = tk.Entry(root)
    token_types_entry.pack()

    buffer_size_entry = tk.Entry(root)
    buffer_size_entry.pack()

    rows_cols_entry = tk.Entry(root)
    rows_cols_entry.pack()

    num_sequences_entry = tk.Entry(root)
    num_sequences_entry.pack()

    max_sequence_length_entry = tk.Entry(root)
    max_sequence_length_entry.pack()

    submit_button = tk.Button(root, text="Submit", command=lambda: process_input(num_token_types_entry, token_types_entry, buffer_size_entry, rows_cols_entry, num_sequences_entry, max_sequence_length_entry))
    submit_button.pack()

    # Remove the initial buttons
    run_keyboard_button.pack_forget()
    run_file_button.pack_forget()

def process_input(num_token_types_entry, token_types_entry, buffer_size_entry, rows_cols_entry, num_sequences_entry, max_sequence_length_entry):   
    # Fungsi ini digunakan untuk memproses input dari keyboard dengan parameter num_token_types_entry (jumlah tipe token), token_types_entry (tipe token), buffer_size_entry (ukuran buffer), 
    # row cols_entry (baris kolom), num_sequences_entry (jumlah sequence), dan max_sequence_length_entry (panjang maksimum sequence).
    output_text = tk.Text(root)
    output_text.pack()

    num_token_types = int(num_token_types_entry.get())
    token_types = token_types_entry.get().split()

    if len(token_types) != num_token_types:
        messagebox.showerror("Banyak masukan tipe token tidak sesuai dengan jumlah tipe token")
    else:
        buffer_size = int(buffer_size_entry.get())
        if buffer_size == 0:
            messagebox.showerror("No solution : Tidak ada ukuran buffer")
            return
        rows, cols = map(int, rows_cols_entry.get().split())

        # Menghasilkan matriks kode acak
        code_matrix = [[int(random.choice(token_types), 16) for _ in range(cols)] for _ in range(rows)]
        code_matrix = np.array(code_matrix)

        output_text.insert(END, "Matrix yang terbuat:\n")
        for row in code_matrix:
            output_text.insert(END, ' '.join(format(num, '02X') for num in row) + "\n")

        num_sequences = int(num_sequences_entry.get())
        max_sequence_length = int(max_sequence_length_entry.get())
        sequences = []
        for _ in range(num_sequences):
            # Menghasilkan panjang sequence acak
            sequence_length = random.randint(1, max_sequence_length)
            # Menghasilkan sequence acak
            sequence = [int(random.choice(token_types), 16) for _ in range(sequence_length)]
            score = random.randint(10, 50)
            sequences.append((sequence, score))

        output_text.insert(END, "Sekuens beserta skor yang terbuat:\n")
        for sequence, score in sequences:
            output_text.insert(END, f"Sekuens: {' '.join(format(num, '02X') for num in sequence)}, Score: {score}\n")
        
        start_time = time.time()
        paths = [(path, PathScore(path, sequences, buffer_size, code_matrix).compute()) for path in generate_paths(buffer_size, code_matrix)]
        max_score = max(score for _, score in paths) if paths else 0

        if max_score == 0:
            output = "Skor maksimum: 0\n"
            output += "Tidak ada token yang dikunjungi\n"
            output += "Tidak ada jalur yang mencapai skor maksimum\n\n"
            output_text.insert(tk.END, output)

        else:
            max_path = max(paths, key=lambda path: path[1]) # Mengambil path dengan skor tertinggi
            output = f"Skor maksimum: {max_path[1]}\n" 

            elements_visited = [format(code_matrix[row-1][col-1], '02X') for row, col in max_path[0].coords] # Mengambil elemen yang dikunjungi
            output += f"Token yang dikunjungi: {' '.join(elements_visited)}\n"
            output += f"Jalur dengan skor maksimum:\n{max_path[0]}\n\n"
            output_text.insert(tk.END, output)

        end_time = time.time() # Menghentikan menghitung waktu eksekusi
        elapsed_time = (end_time - start_time) * 1000  # Kalkulasi waktu eksekusi dalam milidetik
        output = f"Waktu eksekusi program: {elapsed_time} ms\n"  # Menambahkan waktu eksekusi ke output
        output_text.insert(tk.END, output)

        save_output = messagebox.askyesno("Save Output", "Apakah ingin menyimpan solusi?")
        if save_output:
            with open('output.txt', 'w') as f:
                f.write(output_text.get("1.0", tk.END))
    

def run_program_file():
    output_text = tk.Text(root)
    output_text.pack()

    file_name = filedialog.askopenfilename()
    with open(file_name, 'r') as f:
        buffer_size = int(f.readline().strip())
        if buffer_size == 0:
            print("No solution : Tidak ada ukuran buffer")
            return
        rows, cols = map(int, f.readline().split())
        code_matrix = []
        for _ in range(rows):
            row_string = f.readline().strip()
            row = [int(hex_string, 16) for hex_string in row_string.split()]
            code_matrix.append(row)
        code_matrix = np.array(code_matrix)

        num_sequences = int(f.readline())
        sequences = []
        for _ in range(num_sequences):
            sequence_string = f.readline().strip()
            sequence = [int(hex_string, 16) for hex_string in sequence_string.split()]
            score = int(f.readline())
            sequences.append((sequence, score))
    
    start_time = time.time()
    paths = [(path, PathScore(path, sequences, buffer_size, code_matrix).compute()) for path in generate_paths(buffer_size, code_matrix)]
    max_score = max(score for _, score in paths) if paths else 0

    if max_score == 0:
        output = "Skor maksimum: 0\n"
        output += "Tidak ada token yang dikunjungi\n"
        output += "Tidak ada jalur yang mencapai skor maksimum\n\n"
        output_text.insert(tk.END, output)

    else:
        max_path = max(paths, key=lambda path: path[1]) # Mengambil path dengan skor tertinggi
        output = f"Skor maksimum: {max_path[1]}\n" 

        elements_visited = [format(code_matrix[row-1][col-1], '02X') for row, col in max_path[0].coords] # Mengambil elemen yang dikunjungi
        output += f"Token yang dikunjungi: {' '.join(elements_visited)}\n"
        output += f"Jalur dengan skor maksimum:\n{max_path[0]}\n\n"
        output_text.insert(tk.END, output)

    end_time = time.time() # Menghentikan menghitung waktu eksekusi
    elapsed_time = (end_time - start_time) * 1000  # Kalkulasi waktu eksekusi dalam milidetik
    output = f"Waktu eksekusi program: {elapsed_time} ms\n"  # Menambahkan waktu eksekusi ke output
    output_text.insert(tk.END, output)

    save_output = messagebox.askyesno("Save Output", "Apakah ingin menyimpan solusi?")
    if save_output:
        with open('output.txt', 'w') as f:
            f.write(output_text.get("1.0", tk.END))

root = tk.Tk()
root.configure(bg='light blue')

def change_label_color():
    next_color = next(color_cycle)
    title_label.config(fg=next_color)
    root.after(2000, change_label_color)

colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#8B00FF']
color_cycle = itertools.cycle(colors)

title_label = tk.Label(root, text="Cyberpunk 2077 Breach Protocol Solver", bg='light blue', font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

change_label_color()

# Menambahkan tombol untuk menjalankan program
run_keyboard_button = tk.Button(root, text="Run from Keyboard", command=run_program_keyboard)
run_keyboard_button.pack(pady=10)

run_file_button = tk.Button(root, text="Run from File", command=run_program_file)
run_file_button.pack(pady=10)

root.mainloop()