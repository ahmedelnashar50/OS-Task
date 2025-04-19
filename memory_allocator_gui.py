import tkinter as tk
from tkinter import messagebox

class MemoryBlock:
    def __init__(self, start, size, process_name=None):
        self.start = start
        self.size = size
        self.process_name = process_name

    def is_free(self):
        return self.process_name is None

class MemoryAllocator:
    def __init__(self, total_size):
        self.total_size = total_size
        self.memory = [MemoryBlock(0, total_size)]
        self.next_fit_index = 0  

    def allocate(self, process_name, size, allocation_type='first_fit'):
        if allocation_type == 'first_fit':
            return self.first_fit(process_name, size)
        elif allocation_type == 'best_fit':
            return self.best_fit(process_name, size)
        elif allocation_type == 'next_fit':
            return self.next_fit(process_name, size)
        else:
            return False

    def first_fit(self, process_name, size):
        for i, block in enumerate(self.memory):
            if block.is_free() and block.size >= size:
                allocated_block = MemoryBlock(block.start, size, process_name)
                remaining_size = block.size - size
                if remaining_size > 0:
                    self.memory[i] = allocated_block
                    self.memory.insert(i + 1, MemoryBlock(block.start + size, remaining_size))
                else:
                    self.memory[i] = allocated_block
                return True
        return False

    def best_fit(self, process_name, size):
        best_fit_index = -1
        best_fit_size = float('inf')
        for i, block in enumerate(self.memory):
            if block.is_free() and block.size >= size and block.size < best_fit_size:
                best_fit_size = block.size
                best_fit_index = i
        if best_fit_index != -1:
            block = self.memory[best_fit_index]
            allocated_block = MemoryBlock(block.start, size, process_name)
            remaining_size = block.size - size
            if remaining_size > 0:
                self.memory[best_fit_index] = allocated_block
                self.memory.insert(best_fit_index + 1, MemoryBlock(block.start + size, remaining_size))
            else:
                self.memory[best_fit_index] = allocated_block
            return True
        return False

    def next_fit(self, process_name, size):
        start_index = self.next_fit_index
        for i in range(start_index, len(self.memory)):
            block = self.memory[i]
            if block.is_free() and block.size >= size:
                allocated_block = MemoryBlock(block.start, size, process_name)
                remaining_size = block.size - size
                if remaining_size > 0:
                    self.memory[i] = allocated_block
                    self.memory.insert(i + 1, MemoryBlock(block.start + size, remaining_size))
                else:
                    self.memory[i] = allocated_block
                self.next_fit_index = i + 1  
                return True

        for i in range(0, start_index):
            block = self.memory[i]
            if block.is_free() and block.size >= size:
                allocated_block = MemoryBlock(block.start, size, process_name)
                remaining_size = block.size - size
                if remaining_size > 0:
                    self.memory[i] = allocated_block
                    self.memory.insert(i + 1, MemoryBlock(block.start + size, remaining_size))
                else:
                    self.memory[i] = allocated_block
                self.next_fit_index = i + 1
                return True
        return False

    def deallocate(self, process_name):
        for block in self.memory:
            if block.process_name == process_name:
                block.process_name = None
        self.merge_free_blocks()

    def merge_free_blocks(self):
        i = 0
        while i < len(self.memory) - 1:
            current = self.memory[i]
            next_block = self.memory[i + 1]
            if current.is_free() and next_block.is_free():
                current.size += next_block.size
                self.memory.pop(i + 1)
            else:
                i += 1

    def compact(self):
        new_memory = []
        current_address = 0
        for block in self.memory:
            if not block.is_free():
                new_memory.append(MemoryBlock(current_address, block.size, block.process_name))
                current_address += block.size
        remaining_size = self.total_size - current_address
        if remaining_size > 0:
            new_memory.append(MemoryBlock(current_address, remaining_size))
        self.memory = new_memory

class MemoryGUI:
    def __init__(self, root):
        self.allocator = MemoryAllocator(1000)
        self.root = root
        self.root.title("Memory Allocation GUI")

        self.canvas = tk.Canvas(root, width=800, height=200, bg="white")
        self.canvas.pack(pady=10)

        tk.Label(root, text="Process Name:").pack()
        self.process_entry = tk.Entry(root)
        self.process_entry.pack()

        tk.Label(root, text="Size:").pack()
        self.size_entry = tk.Entry(root)
        self.size_entry.pack()

        tk.Label(root, text="Allocation Type:").pack()
        self.allocation_type = tk.StringVar(value="first_fit")
        tk.OptionMenu(root, self.allocation_type, "first_fit", "best_fit", "next_fit").pack()

        tk.Button(root, text="Allocate", command=self.allocate).pack(pady=5)
        tk.Button(root, text="Deallocate", command=self.deallocate).pack(pady=5)
        tk.Button(root, text="Compact", command=self.compact).pack(pady=5)

        self.draw_memory()

    def allocate(self):
        name = self.process_entry.get()
        try:
            size = int(self.size_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid size.")
            return
        allocation_type = self.allocation_type.get()
        if self.allocator.allocate(name, size, allocation_type):
            self.draw_memory()
        else:
            messagebox.showwarning("Warning", "Not enough memory or external fragmentation occurred.")

    def deallocate(self):
        name = self.process_entry.get()
        self.allocator.deallocate(name)
        self.draw_memory()

    def compact(self):
        self.allocator.compact()
        self.draw_memory()

    def draw_memory(self):
        self.canvas.delete("all")
        x = 10
        block_height = 50
        total_width = 780
        for block in self.allocator.memory:
            block_width = (block.size / self.allocator.total_size) * total_width
            color = "lightgreen" if block.is_free() else "skyblue"
            self.canvas.create_rectangle(x, 50, x + block_width, 50 + block_height, fill=color)
            text = f"{block.start}-{block.start + block.size}"
            if not block.is_free():
                text += f"\n{block.process_name}"
            self.canvas.create_text(x + block_width / 2, 75, text=text)
            x += block_width

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryGUI(root)
    root.mainloop()
