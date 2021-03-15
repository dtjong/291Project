import tkinter as tk
from tkinter import ttk
from view import *
from hierarchy import *
import pyperclip

DEFAULT_WIDTH = 375
DEFAULT_HEIGHT = 667

class Canvas(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.dimensions=[DEFAULT_HEIGHT, DEFAULT_WIDTH]
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
        self.snapbt = tk.Button(self.bar, text="snap", command=self.snap)
        self.snapbt.pack(side=tk.LEFT)
        self.resizebt = tk.Button(self.bar, text="resize", command=self.resize)
        self.resizebt.pack(side=tk.LEFT)
        self.framebt = tk.Button(self.bar, text=str(ViewMode.Framed), command=self.toggleframed)
        self.framebt.pack(side=tk.LEFT)
        self.bar.pack()

        instr_text1 = "Press, drag, and release mouse to draw rectangles representing UI elements. "

        self.instruction1 = tk.Label(self.frame, text=instr_text1)
        self.instruction1.pack()

        self.widthlabel = tk.Label(self.bar, text="width:")
        self.widthlabel.pack(side=tk.LEFT)

        self.width_entry = tk.Entry(self.bar, width=10)
        self.width_entry.insert(0, str(DEFAULT_WIDTH))
        self.width_entry.pack(side=tk.LEFT)

        self.heightlabel = tk.Label(self.bar, text="height:")
        self.heightlabel.pack(side=tk.LEFT)

        self.height_entry = tk.Entry(self.bar, width=10)
        self.height_entry.insert(0, str(DEFAULT_HEIGHT))
        self.height_entry.pack(side=tk.LEFT)

        self.view_mode = ViewMode.Framed

    def toggleframed(self):
        self.view_mode = ~self.view_mode
        self.framebt['text'] = str(self.view_mode)

    def resize(self):
        self.dimensions=[int(self.height_entry.get()),
                         int(self.width_entry.get())]
        self.clear()

    def submit(self):
        hier = infer_hierarchy(self.views)
        hier.solve()
        pyperclip.copy(hier.to_swiftui())

    def snap(self):
        hier = infer_hierarchy(self.views)
        self.clear()
        hier.cleanse()
        self.views.extend(hier.flatlist())
        for view in self.views[1:]:
            self.canvas.create_rectangle(view.top_left[1], view.top_left[0],
                                         view.bot_right[1], view.bot_right[0],
                                         fill="black" if view.view_mode else
                                         "white", tags="element")

    def create_canvas(self):
        self.canvasframe = tk.Frame(self.frame, highlightbackground="black", highlightthickness=1)

        self.canvas = tk.Canvas(self.canvasframe, width=self.dimensions[1], height=self.dimensions[0], cursor="cross")
        self.canvas.pack(side="top")

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.views = [View([0, 0], self.dimensions)]
        self.canvasframe.pack()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="black" if self.view_mode else "white", tags="element")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        curX, curY = (event.x, event.y)
        self.views.append(View([self.start_y, self.start_x], [curY, curX], view_mode=self.view_mode))

    def clear(self):
        # Clear the canvas
        self.canvasframe.destroy()
        self.create_canvas()

if __name__ == "__main__":
    app = Canvas()
    app.mainloop()
