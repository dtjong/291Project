import tkinter as tk

class Canvas(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.x = self.y = 0
        self.canvas = tk.Canvas(self, width=512, height=512, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

        instr_text1 = "Press, drag, and release mouse to draw rectangles representing UI elements. "
        instr_text2 = "Click them to delete"

        self.instruction1 = tk.Label(self, text=instr_text1)
        self.instruction1.place(x=30, y=100)
        self.instruction2 = tk.Label(self, text=instr_text2)
        self.instruction2.place(x=150, y=130)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        # self.canvas.bind("<Button-1>", self.on_click)

        self.rect = None
        self.start_x = None
        self.start_y = None

    def on_button_press(self, event):
        # Instructions disappear when drawing starts
        self.instruction1.lower(self.canvas)
        self.instruction2.lower(self.canvas)

        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="black")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass

    def on_click(self, event):
        # Let one rect disappear on click
        pass
    
if __name__ == "__main__":
    app = Canvas()
    app.mainloop()