import numpy as np
import time
import random 

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

def main():
    input_method = input("Masukkan input dari file atau dari keyboard? (file/keyboard) ")

    if input_method.lower() == 'file':
        file_name = input("Masukkan nama file input: ")
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

    elif input_method.lower() == 'keyboard':
        num_token_types = int(input("Masukkan Jumlah token unik: "))
        token_types = input("Masukkan Token: ").split()
        if len(token_types) != num_token_types:
            print("Banyak masukan tipe token tidak sesuai dengan jumlah tipe token")
            return
        
        buffer_size = int(input("Masukkan Ukuran buffer: "))
        if buffer_size == 0:
            print("No solution : Tidak ada ukuran buffer")
            return
        rows, cols = map(int, input("Masukkan banyak baris dan kolom: ").split())

        # Generate a random matrix
        code_matrix = [[int(random.choice(token_types), 16) for _ in range(cols)] for _ in range(rows)]
        code_matrix = np.array(code_matrix)

        print("Matrix yang terbuat:")
        for row in code_matrix:
            print(' '.join(format(num, '02X') for num in row))

        num_sequences = int(input("Masukkan jumlah sekuens: "))
        max_sequence_length = int(input("Masukkan ukuran maksimal sekuens: "))
        sequences = []
        for _ in range(num_sequences):
            # Generate a random sequence length up to the maximum
            sequence_length = random.randint(1, max_sequence_length)
            # Generate a random sequence and a random score
            sequence = [int(random.choice(token_types), 16) for _ in range(sequence_length)]
            score = random.randint(10, 50)
            sequences.append((sequence, score))

        print("Sekuens beserta skor yang terbuat:")
        for sequence, score in sequences:
            print(f"Sequence: {' '.join(format(num, '02X') for num in sequence)}, Score: {score}")
    else:
        print("Metode tersebut tidak valid kawan :(")
        return
    
    start_time = time.time()
    paths = [(path, PathScore(path, sequences, buffer_size, code_matrix).compute()) for path in generate_paths(buffer_size, code_matrix)]
    
    max_score = max(score for _, score in paths) if paths else 0

    if max_score == 0:
        output = "Skor maksimum: 0\n"
        output += "Tidak ada token yang dikunjungi\n"
        output += "Tidak ada jalur yang mencapai skor maksimum\n\n"

    else:
        max_path = max(paths, key=lambda path: path[1]) # Mengambil path dengan skor tertinggi
        output = f"Skor maksimum: {max_path[1]}\n" 

        elements_visited = [format(code_matrix[row-1][col-1], '02X') for row, col in max_path[0].coords] # Mengambil elemen yang dikunjungi
        output += f"Token yang dikunjungi: {' '.join(elements_visited)}\n"
        output += f"Jalur dengan skor maksimum:\n{max_path[0]}\n\n"

    end_time = time.time() # Menghentikan menghitung waktu eksekusi
    elapsed_time = (end_time - start_time) * 1000  # Kalkulasi waktu eksekusi dalam milidetik
    output += f"Waktu eksekusi program: {elapsed_time} ms\n"  # Menambahkan waktu eksekusi ke output
    print(output)

    save_output = input("Apakah ingin menyimpan solusi? (y/n) ")
    if save_output.lower() == 'y':
        with open('output.txt', 'w') as f:
            f.write(output)

if __name__ == '__main__':
    main()