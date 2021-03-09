import tkinter as tk
from tkinter import ttk
from view import *
from hierarchy import *

class Canvas(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.dimensions=[512, 512]
        self.x = self.y = 0
        self.frame = tk.Frame(self)
        self.init_menu()
        self.create_canvas()
        self.frame.pack()

    def init_menu(self):
        self.bar = tk.Frame(self.frame)
        self.submitbt = tk.Button(self.bar, text="submit", fg="green", command=self.submit)
        self.submitbt.pack(side=tk.LEFT)
        self.clearbt = tk.Button(self.bar, text="clear", command=self.clear)
        self.clearbt.pack(side=tk.LEFT)
        self.bar.pack()

        instr_text1 = "Press, drag, and release mouse to draw rectangles representing UI elements. "

        self.instruction1 = tk.Label(self.frame, text=instr_text1)
        self.instruction1.pack()

    def submit(self):
        hier = infer_hierarchy(self.views)
        hier.solve()
        print(hier.to_swiftui()) #TODO: Present swiftUI to user

    def create_canvas(self):
        self.canvas = tk.Canvas(self.frame, width=self.dimensions[1], height=self.dimensions[0], cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.views = [View([0, 0], self.dimensions)]

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="black", tags="element")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        curX, curY = (event.x, event.y)
        self.views.append(View([self.start_y, self.start_x], [curY, curX]))

    def clear(self):
        # Clear the canvas
        self.canvas.destroy()
        self.create_canvas()
    
if __name__ == "__main__":
    app = Canvas()
    app.mainloop()
