# Yordan Yordanov
# December, 2025

import tkinter as tk
from tkinter import ttk, messagebox

BLOCK_SIZE = 1024
TOTAL_BLOCKS = 10
TOTAL_BYTES = BLOCK_SIZE * TOTAL_BLOCKS

class FATSimulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FAT Simulator (10 blocks of 1 KB each)")

        self.fat = [None] * TOTAL_BLOCKS  # next-block pointers
        self.directory = {}  # name -> {size, first_block}

        self.build_ui()
        self.refresh_tables()
        self.root.mainloop()

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(pady=10)

        tk.Label(top, text="File Name:").grid(row=0, column=0, padx=10, sticky="e")
        self.name_entry = tk.Entry(top, width=10)
        self.name_entry.grid(row=0, column=1)

        tk.Label(top, text="File Size (bytes):").grid(row=1, column=0, padx=10, sticky="e")
        self.size_entry = tk.Entry(top, width=10)
        self.size_entry.grid(row=1, column=1)

        tk.Button(top, text="New File/Extend", command=self.create_file).grid(row=0, column=2, padx=10)
        tk.Button(top, text="Delete File", command=self.delete_file).grid(row=1, column=2, padx=10, sticky="w")
        tk.Button(top, text="Trace Blocks", command=self.trace_file).grid(row=0, column=3, padx=10)

        mid = tk.Frame(self.root)
        mid.pack(pady=10)

        # Directory table
        self.dir_tree = ttk.Treeview(mid, columns=("name", "size", "first"), show="headings", height=10)
        self.dir_tree.heading("name", text="File Name")
        self.dir_tree.heading("size", text="File Size")
        self.dir_tree.heading("first", text="First Block")

        self.dir_tree.column("name", width=100, anchor="center")
        self.dir_tree.column("size", width=80, anchor="center")
        self.dir_tree.column("first", width=100, anchor="center")

        self.dir_tree.grid(row=0, column=0, padx=10)

        # FAT table
        self.fat_tree = ttk.Treeview(mid, columns=("index", "next"), show="headings", height=10)
        self.fat_tree.heading("index", text="Block")
        self.fat_tree.heading("next", text="Next Block")
        self.fat_tree.column("index", width=80, anchor="center")
        self.fat_tree.column("next", width=100, anchor="center")
        self.fat_tree.grid(row=0, column=1, padx=10)

        self.used_label = tk.Label(self.root, text="Used Space: 0 bytes")
        self.used_label.pack(pady=5)

        self.root.resizable(False, False)

    def refresh_tables(self):
        # directory
        for i in self.dir_tree.get_children():
            self.dir_tree.delete(i)
        for name, info in self.directory.items():
            self.dir_tree.insert("", tk.END, values=(name, info["size"], info["first_block"] + 1))

        # FAT
        for i in self.fat_tree.get_children():
            self.fat_tree.delete(i)
        for i in range(TOTAL_BLOCKS):
            nxt = self.fat[i]
            self.fat_tree.insert("", tk.END,
                values=(
                    i+1,
                    "/" if nxt == -1 else ((nxt+1) if nxt is not None else " ")
                )
            )

        used = sum(info["size"] for info in self.directory.values())
        self.used_label.config(text=f"Used Space: {used} of {TOTAL_BYTES} bytes")

    def allocate_blocks(self, num_blocks):
        free_indices = [i for i, free in enumerate(self.fat) if free == None]
        if len(free_indices) < num_blocks:
            return None
        allocated = free_indices[:num_blocks]
        for i in range(len(allocated) - 1):
            self.fat[allocated[i]] = allocated[i + 1]
        self.fat[allocated[-1]] = -1  # end-of-file marker
        return allocated[0]
    
    def create_file(self):
        name = self.name_entry.get().strip()
        try:
            size = int(self.size_entry.get())
        except:
            messagebox.showerror("Error", "Invalid size")
            return

        num_blocks_needed = (size + BLOCK_SIZE - 1) // BLOCK_SIZE

        # -------------------------------------------------------------
        # CASE 1: File does NOT exist — create it normally
        # -------------------------------------------------------------
        if name not in self.directory:
            if not name:
                messagebox.showerror("Error", "Invalid filename")
                return

            start = self.allocate_blocks(num_blocks_needed)
            if start is None:
                messagebox.showerror("Error", "Not enough free space")
                return

            self.directory[name] = {"size": size, "first_block": start}
            self.refresh_tables()
            return

        # -------------------------------------------------------------
        # CASE 2: File exists — extend it
        # -------------------------------------------------------------
        old_size = self.directory[name]["size"]
        old_blocks = (old_size + BLOCK_SIZE - 1) // BLOCK_SIZE

        if num_blocks_needed <= old_blocks:
            messagebox.showinfo("Info", "File already large enough.")
            return

        extra_blocks = num_blocks_needed - old_blocks
        extra_start = self.allocate_blocks(extra_blocks)

        if extra_start is None:
            messagebox.showerror("Error", "Not enough free space to extend file")
            return

        # Find the last block in the current chain
        blk = self.directory[name]["first_block"]
        while self.fat[blk] not in (None, -1):
            blk = self.fat[blk]

        # Link old last block → new first extra block
        # last block previously marked -1
        self.fat[blk] = extra_start

        # Update new last block to end marker
        # allocate_blocks() already sets the last new block to -1

        # Update directory size
        self.directory[name]["size"] = size

        self.refresh_tables()
        messagebox.showinfo("Success", f"File '{name}' extended.")

    def delete_file(self):
        name = self.name_entry.get().strip()
        if name not in self.directory:
            messagebox.showerror("Error", "File not found")
            return
        blk = self.directory[name]["first_block"]
        while blk is not None and blk != -1:
            nxt = self.fat[blk]
            self.fat[blk] = None
            blk = nxt
        del self.directory[name]
        self.refresh_tables()

    def trace_file(self):
        name = self.name_entry.get().strip()
        if name not in self.directory:
            messagebox.showerror("Error", "File not found")
            return

        blk = self.directory[name]["first_block"]
        chain = []
        while blk is not None and blk != -1:
            chain.append(str(blk + 1))  # <-- Add 1 to display index
            blk = self.fat[blk]

        messagebox.showinfo("Trace", " -> ".join(chain))

if __name__ == "__main__":
    FATSimulator()
