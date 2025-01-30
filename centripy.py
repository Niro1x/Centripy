import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox  # >>> ADDED
import math
import json  # >>> ADDED

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

def to_canvas_coords(x, y):
    """
    Convert math coords (origin at canvas center, +y up)
    to Tkinter coords (origin top-left, +y down).
    """
    cx = (CANVAS_WIDTH / 2) + x
    cy = (CANVAS_HEIGHT / 2) - y
    return cx, cy

def to_math_coords(cx, cy):
    """
    Convert Tkinter coords (origin top-left, +y down)
    to math coords (origin at canvas center, +y up).
    """
    x = cx - (CANVAS_WIDTH / 2)
    y = (CANVAS_HEIGHT / 2) - cy
    return x, y

# ----------------------------------------------------------------
# Base Shape and Helpers
# ----------------------------------------------------------------
class Shape:
    def calculate_area(self):
        raise NotImplementedError

    def calculate_centroid(self):
        raise NotImplementedError

    def draw(self, canvas):
        """Draw on canvas."""
        raise NotImplementedError

    def bounding_box(self):
        """
        Return (xmin, ymin, xmax, ymax) in *math* coords for
        a simple bounding-box check. We'll use this in 'delete mode'.
        """
        raise NotImplementedError

    def is_point_inside(self, x, y):
        """
        A simple check if (x, y) in math coords lies within the bounding box.
        This is a rough approach for selection. 
        """
        xmin, ymin, xmax, ymax = self.bounding_box()
        return (xmin <= x <= xmax) and (ymin <= y <= ymax)
    
    # >>> ADDED
    def to_dict(self):
        """Convert the shape to a dictionary for serialization."""
        raise NotImplementedError

    @staticmethod
    def from_dict(data):
        """Create a shape instance from a dictionary."""
        shape_type = data.get("type")
        if shape_type == "LineShape":
            return LineShape(**data["params"])
        elif shape_type == "RectangleShape":
            return RectangleShape(**data["params"])
        elif shape_type == "CircleShape":
            return CircleShape(**data["params"])
        elif shape_type == "TriangleShape":
            return TriangleShape(**data["params"])
        elif shape_type == "HalfCircleShape":
            return HalfCircleShape(**data["params"])
        elif shape_type == "QuarterCircleShape":
            return QuarterCircleShape(**data["params"])
        elif shape_type == "PolygonShape":
            return PolygonShape(**data["params"])
        else:
            return None
    # <<< ADDED

# ----------------------------------------------------------------
# 1) LineShape
# ----------------------------------------------------------------
class LineShape(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

    def calculate_area(self):
        return 0.0  # line has no area

    def calculate_centroid(self):
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return (cx, cy)

    def draw(self, canvas):
        c1 = to_canvas_coords(self.x1, self.y1)
        c2 = to_canvas_coords(self.x2, self.y2)
        canvas.create_line(*c1, *c2, fill="green", width=2)

        # midpoint
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="green")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="green")

    def bounding_box(self):
        xmin = min(self.x1, self.x2)
        xmax = max(self.x1, self.x2)
        ymin = min(self.y1, self.y2)
        ymax = max(self.y1, self.y2)
        return (xmin, ymin, xmax, ymax)
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "LineShape",
            "params": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 2) RectangleShape
# ----------------------------------------------------------------
class RectangleShape(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

    def calculate_area(self):
        return abs(self.x2 - self.x1) * abs(self.y2 - self.y1)

    def calculate_centroid(self):
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return (cx, cy)

    def draw(self, canvas):
        x_min, x_max = sorted([self.x1, self.x2])
        y_min, y_max = sorted([self.y1, self.y2])
        c1 = to_canvas_coords(x_min, y_min)
        c2 = to_canvas_coords(x_max, y_max)
        canvas.create_rectangle(*c1, *c2, outline="blue", width=2)

        # centroid
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="blue")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="blue")

    def bounding_box(self):
        xmin = min(self.x1, self.x2)
        xmax = max(self.x1, self.x2)
        ymin = min(self.y1, self.y2)
        ymax = max(self.y1, self.y2)
        return (xmin, ymin, xmax, ymax)
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "RectangleShape",
            "params": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 3) CircleShape
# ----------------------------------------------------------------
class CircleShape(Shape):
    def __init__(self, cx, cy, r):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.r = r

    def calculate_area(self):
        return math.pi * (self.r ** 2)

    def calculate_centroid(self):
        return (self.cx, self.cy)

    def draw(self, canvas):
        x_min = self.cx - self.r
        x_max = self.cx + self.r
        y_min = self.cy - self.r
        y_max = self.cy + self.r

        c1 = to_canvas_coords(x_min, y_min)
        c2 = to_canvas_coords(x_max, y_max)
        canvas.create_oval(*c1, *c2, outline="purple", width=2)

        # centroid
        ccx, ccy = to_canvas_coords(self.cx, self.cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="purple")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="purple")

    def bounding_box(self):
        x_min = self.cx - self.r
        x_max = self.cx + self.r
        y_min = self.cy - self.r
        y_max = self.cy + self.r
        return (x_min, y_min, x_max, y_max)
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "CircleShape",
            "params": {
                "cx": self.cx,
                "cy": self.cy,
                "r": self.r
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 4) TriangleShape
# ----------------------------------------------------------------
class TriangleShape(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3

    def calculate_area(self):
        # Shoelace formula
        return abs(
            (self.x1*(self.y2 - self.y3) +
             self.x2*(self.y3 - self.y1) +
             self.x3*(self.y1 - self.y2)) / 2
        )

    def calculate_centroid(self):
        # average of vertices
        cx = (self.x1 + self.x2 + self.x3) / 3
        cy = (self.y1 + self.y2 + self.y3) / 3
        return (cx, cy)

    def draw(self, canvas):
        p1 = to_canvas_coords(self.x1, self.y1)
        p2 = to_canvas_coords(self.x2, self.y2)
        p3 = to_canvas_coords(self.x3, self.y3)
        canvas.create_polygon(*p1, *p2, *p3,
                              outline="brown", fill="", width=2)
        # centroid
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="brown")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="brown")

    def bounding_box(self):
        xs = [self.x1, self.x2, self.x3]
        ys = [self.y1, self.y2, self.y3]
        return (min(xs), min(ys), max(xs), max(ys))
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "TriangleShape",
            "params": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2,
                "x3": self.x3,
                "y3": self.y3
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 5) HalfCircleShape
# ----------------------------------------------------------------
class HalfCircleShape(Shape):
    def __init__(self, cx, cy, r):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.r = r

    def calculate_area(self):
        return 0.5 * math.pi * (self.r ** 2)

    def calculate_centroid(self):
        # For a top half circle with flat side at y = cy - r:
        offset = -self.r + (4 * self.r) / (3 * math.pi)
        return (self.cx, self.cy + offset)

    def draw(self, canvas):
        x_min = self.cx - self.r
        y_min = self.cy - self.r
        x_max = self.cx + self.r
        y_max = self.cy + self.r
        c1 = to_canvas_coords(x_min, y_min)
        c2 = to_canvas_coords(x_max, y_max)

        # top half => start=180, extent=180
        canvas.create_arc(*c1, *c2, start=180, extent=180,
                          outline="orange", width=2, style=tk.ARC)
        # centroid
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="orange")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="orange")

    def bounding_box(self):
        x_min = self.cx - self.r
        x_max = self.cx + self.r
        y_min = self.cy - self.r
        y_max = self.cy + self.r
        return (x_min, y_min, x_max, y_max)
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "HalfCircleShape",
            "params": {
                "cx": self.cx,
                "cy": self.cy,
                "r": self.r
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 6) QuarterCircleShape
# ----------------------------------------------------------------
class QuarterCircleShape(Shape):
    def __init__(self, cx, cy, r):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.r = r

    def calculate_area(self):
        return 0.25 * math.pi * (self.r ** 2)

    def calculate_centroid(self):
        # top-right quarter circle => offset in x,y is 4r/(3π)
        offset = (4 * self.r) / (3 * math.pi)
        return (self.cx + offset, self.cy + offset)

    def draw(self, canvas):
        x_min = self.cx - self.r
        y_min = self.cy - self.r
        x_max = self.cx + self.r
        y_max = self.cy + self.r
        c1 = to_canvas_coords(x_min, y_min)
        c2 = to_canvas_coords(x_max, y_max)

        # top-right => start=270, extent=90
        canvas.create_arc(*c1, *c2, start=270, extent=90,
                          outline="red", width=2, style=tk.ARC)
        # centroid
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="red")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="red")

    def bounding_box(self):
        x_min = self.cx - self.r
        x_max = self.cx + self.r
        y_min = self.cy - self.r
        y_max = self.cy + self.r
        return (x_min, y_min, x_max, y_max)
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "QuarterCircleShape",
            "params": {
                "cx": self.cx,
                "cy": self.cy,
                "r": self.r
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# 7) PolygonShape (For Arbitrary Coordinates)
# ----------------------------------------------------------------
class PolygonShape(Shape):
    """
    A generic polygon defined by a list of points [(x1,y1), (x2,y2), ...].
    """
    def __init__(self, points):
        super().__init__()
        self.points = points  # list of (x, y)

    def calculate_area(self):
        # Shoelace formula
        area = 0
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]
            area += (x1 * y2 - x2 * y1)
        return abs(area) / 2

    def calculate_centroid(self):
        # Polygon centroid formula (for non-self-intersecting polygons)
        # Cx = (1/(6A)) * sum((x_i + x_{i+1})*(x_i*y_{i+1} - x_{i+1}*y_i))
        # Cy similarly
        A = self.calculate_area()
        if abs(A) < 1e-12:
            # Degenerate polygon => pick something
            return (0, 0)

        cx = 0
        cy = 0
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]
            cross = (x1 * y2 - x2 * y1)
            cx += (x1 + x2) * cross
            cy += (y1 + y2) * cross
        cx /= (6 * A)
        cy /= (6 * A)
        return (cx, cy)

    def draw(self, canvas):
        # Convert each point to canvas coords
        canvas_points = []
        for (x, y) in self.points:
            cx, cy = to_canvas_coords(x, y)
            canvas_points.append(cx)
            canvas_points.append(cy)

        # Draw polygon outline
        canvas.create_polygon(*canvas_points, outline="gray", fill="", width=2)

        # Draw centroid
        cx, cy = self.calculate_centroid()
        ccx, ccy = to_canvas_coords(cx, cy)
        canvas.create_line(ccx - 3, ccy, ccx + 3, ccy, fill="gray")
        canvas.create_line(ccx, ccy - 3, ccx, ccy + 3, fill="gray")

    def bounding_box(self):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
    
    # >>> ADDED
    def to_dict(self):
        return {
            "type": "PolygonShape",
            "params": {
                "points": self.points
            }
        }
    # <<< ADDED

# ----------------------------------------------------------------
# Main Application
# ----------------------------------------------------------------
class CentroidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CentriPy")

        self.shapes = []
        self.current_tool = None
        self.click_points = []
        self.preview_item = None
        self.delete_mode = False  # if True, clicking will delete shapes

        self.setup_gui()

    def setup_gui(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Combobox for shape selection
        self.shape_var = tk.StringVar(value="Rectangle")
        shape_choices = [
            "Line", "Rectangle", "Circle",
            "Triangle", "HalfCircle", "QuarterCircle"
        ]
        shape_combo = ttk.Combobox(toolbar, textvariable=self.shape_var,
                                   values=shape_choices, state="readonly")
        shape_combo.pack(side=tk.LEFT, padx=2)

        add_btn = ttk.Button(toolbar, text="Add Shape (Mouse)",
                             command=self.activate_shape_tool)
        add_btn.pack(side=tk.LEFT, padx=2)

        # Button: Add shape by coordinates
        coord_btn = ttk.Button(toolbar, text="Add Shape by Coordinates",
                               command=self.add_shape_by_coords_dialog)
        coord_btn.pack(side=tk.LEFT, padx=2)

        calc_btn = ttk.Button(toolbar, text="Recalculate Centroid",
                              command=self.calculate_composite_centroid)
        calc_btn.pack(side=tk.LEFT, padx=2)

        # Delete button toggles delete_mode
        del_btn = ttk.Button(toolbar, text="Delete Shape",
                             command=self.toggle_delete_mode)
        del_btn.pack(side=tk.LEFT, padx=2)

        # >>> ADDED: Import and Export Buttons
        import_btn = ttk.Button(toolbar, text="Import", command=self.import_shapes)
        import_btn.pack(side=tk.LEFT, padx=2)

        export_btn = ttk.Button(toolbar, text="Export", command=self.export_shapes)
        export_btn.pack(side=tk.LEFT, padx=2)

        # >>> ADDED: Help Button
        help_btn = ttk.Button(toolbar, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=2)
        # <<< ADDED

        self.centroid_label = ttk.Label(toolbar, text="Composite Centroid: (N/A, N/A)")
        self.centroid_label.pack(side=tk.LEFT, padx=10)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Event bindings
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        self.draw_axes()

    # ---------------------------
    # 1) Axes and Redraw
    # ---------------------------
    def draw_axes(self):
        self.canvas.delete("all")
        # X-axis
        x_axis_start = to_canvas_coords(-CANVAS_WIDTH, 0)
        x_axis_end = to_canvas_coords(CANVAS_WIDTH, 0)
        self.canvas.create_line(*x_axis_start, *x_axis_end, fill="black")

        # Y-axis
        y_axis_start = to_canvas_coords(0, -CANVAS_HEIGHT)
        y_axis_end = to_canvas_coords(0, CANVAS_HEIGHT)
        self.canvas.create_line(*y_axis_start, *y_axis_end, fill="black")

        # Origin cross
        ox, oy = to_canvas_coords(0, 0)
        self.canvas.create_line(ox - 5, oy, ox + 5, oy, fill="black")
        self.canvas.create_line(ox, oy - 5, ox, oy + 5, fill="black")

        # Redraw existing shapes
        for s in self.shapes:
            s.draw(self.canvas)

    def redraw_all(self):
        self.draw_axes()
        self.calculate_composite_centroid()

    # ---------------------------
    # 2) Delete Mode
    # ---------------------------
    def toggle_delete_mode(self):
        """
        Toggles whether we're in "delete mode".
        If true, clicking on a shape's bounding box will remove it.
        """
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            print("Delete Mode Activated: click on a shape to remove it.")
        else:
            print("Delete Mode Deactivated.")

    # ---------------------------
    # 3) Add Shape by Coordinates Dialog
    # ---------------------------
    def add_shape_by_coords_dialog(self):
        """
        Opens a small dialog window to let the user specify:
        - number of points
        - coordinates for the shape
        We'll create a PolygonShape from those points.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Shape by Coordinates")

        # Number of points
        tk.Label(dialog, text="Number of Points:").grid(row=0, column=0, padx=5, pady=5)
        points_var = tk.StringVar()
        e_points = ttk.Entry(dialog, textvariable=points_var)
        e_points.grid(row=0, column=1, padx=5, pady=5)

        # Coordinates
        tk.Label(dialog, text="Coordinates (x1,y1 x2,y2 ...):").grid(row=1, column=0, padx=5, pady=5)
        coords_var = tk.StringVar()
        e_coords = ttk.Entry(dialog, textvariable=coords_var, width=40)
        e_coords.grid(row=1, column=1, padx=5, pady=5)

        # Submit button
        def on_submit():
            try:
                n = int(points_var.get().strip())
                # --- New condition: require at least 3 points ---
                if n <= 3:
                    tk.messagebox.showerror("Error", "Requires at least 4 points.")
                    return

                coords_str = coords_var.get().strip()
                # parse them
                # e.g. "0,0 100,0 100,50"
                parts = coords_str.split()
                if len(parts) != n:
                    tk.messagebox.showerror("Error", f"Expected {n} pairs, got {len(parts)}.")
                    return

                points = []
                for p in parts:
                    xy = p.split(",")
                    if len(xy) != 2:
                        messagebox.showerror("Error", "Each pair must be x,y.")
                        return
                    x = float(xy[0])
                    y = float(xy[1])
                    points.append((x, y))

                # Create the polygon shape
                new_shape = PolygonShape(points)
                self.shapes.append(new_shape)
                dialog.destroy()

                self.redraw_all()

            except ValueError as ve:
                messagebox.showerror("Error", f"Invalid input: {ve}")

        submit_btn = ttk.Button(dialog, text="Submit", command=on_submit)
        submit_btn.grid(row=2, column=0, columnspan=2, pady=10)


    # ---------------------------
    # 4) Activating Mouse-based Shape Tools
    # ---------------------------
    def activate_shape_tool(self):
        self.current_tool = self.shape_var.get()
        self.click_points.clear()
        if self.preview_item:
            self.canvas.delete(self.preview_item)
            self.preview_item = None
        print(f"Creating shape: {self.current_tool}")
        # Turn off delete mode if on
        self.delete_mode = False

    # ---------------------------
    # 5) Mouse Events
    # ---------------------------
    def on_left_click(self, event):
        """
        If delete_mode is on, we attempt to delete the shape clicked.
        Otherwise, we gather points for shape creation.
        """
        mx, my = to_math_coords(event.x, event.y)

        if self.delete_mode:
            # Find the first shape whose bounding box contains (mx, my)
            for i, shape in enumerate(reversed(self.shapes), start=1):
                if shape.is_point_inside(mx, my):
                    # Actually remove it from self.shapes
                    idx = len(self.shapes) - i
                    removed_shape = self.shapes.pop(idx)
                    print("Deleted shape:", removed_shape.__class__.__name__)
                    self.redraw_all()
                    break
            # We remain in delete mode to allow multiple deletions
            return

        # If not delete mode, handle shape creation
        self.click_points.append((mx, my))

    def on_drag(self, event):
        if self.current_tool is None:
            return
        # If shape requires 2 points and we have at least 1 click
        shapes_needing_2_points = {"Line", "Rectangle", "Circle", "HalfCircle", "QuarterCircle"}
        if self.current_tool not in shapes_needing_2_points:
            return
        if len(self.click_points) < 1:
            return

        x1, y1 = self.click_points[0]
        x2, y2 = to_math_coords(event.x, event.y)

        if self.preview_item:
            self.canvas.delete(self.preview_item)
            self.preview_item = None

        # Draw new preview
        self.preview_item = self.draw_temporary_shape(self.current_tool, x1, y1, x2, y2)

    def on_left_release(self, event):
        if self.current_tool is None:
            return

        shape_type = self.current_tool
        needed_points = {
            "Line": 2,
            "Rectangle": 2,
            "Circle": 2,
            "Triangle": 3,
            "HalfCircle": 2,
            "QuarterCircle": 2
        }[shape_type]

        if len(self.click_points) < needed_points:
            # Not enough points yet
            return

        # Construct shape
        if shape_type == "Line":
            (x1, y1), (x2, y2) = self.click_points
            new_shape = LineShape(x1, y1, x2, y2)

        elif shape_type == "Rectangle":
            (x1, y1), (x2, y2) = self.click_points
            new_shape = RectangleShape(x1, y1, x2, y2)

        elif shape_type == "Circle":
            (cx, cy), (rx, ry) = self.click_points
            r = math.dist((cx, cy), (rx, ry))
            new_shape = CircleShape(cx, cy, r)

        elif shape_type == "HalfCircle":
            (cx, cy), (rx, ry) = self.click_points
            r = math.dist((cx, cy), (rx, ry))
            new_shape = HalfCircleShape(cx, cy, r)

        elif shape_type == "QuarterCircle":
            (cx, cy), (rx, ry) = self.click_points
            r = math.dist((cx, cy), (rx, ry))
            new_shape = QuarterCircleShape(cx, cy, r)

        elif shape_type == "Triangle":
            (x1, y1), (x2, y2), (x3, y3) = self.click_points
            new_shape = TriangleShape(x1, y1, x2, y2, x3, y3)

        else:
            new_shape = None

        if new_shape:
            self.shapes.append(new_shape)

        # Reset
        self.current_tool = None
        self.click_points.clear()
        if self.preview_item:
            self.canvas.delete(self.preview_item)
            self.preview_item = None

        self.redraw_all()

    # ---------------------------
    # 6) Temporary Shape (Preview)
    # ---------------------------
    def draw_temporary_shape(self, shape_type, x1, y1, x2, y2):
        c1 = to_canvas_coords(x1, y1)
        c2 = to_canvas_coords(x2, y2)

        if shape_type == "Line":
            return self.canvas.create_line(*c1, *c2,
                                           fill="gray", dash=(4, 2))

        elif shape_type == "Rectangle":
            x_min, x_max = sorted([x1, x2])
            y_min, y_max = sorted([y1, y2])
            c1_min = to_canvas_coords(x_min, y_min)
            c2_max = to_canvas_coords(x_max, y_max)
            return self.canvas.create_rectangle(*c1_min, *c2_max,
                                                outline="gray", dash=(4, 2))

        elif shape_type in ["Circle", "HalfCircle", "QuarterCircle"]:
            r = math.dist((x1, y1), (x2, y2))
            x_min = x1 - r
            x_max = x1 + r
            y_min = y1 - r
            y_max = y1 + r
            c1_min = to_canvas_coords(x_min, y_min)
            c2_max = to_canvas_coords(x_max, y_max)

            if shape_type == "Circle":
                return self.canvas.create_oval(*c1_min, *c2_max,
                                               outline="gray", dash=(4, 2))
            elif shape_type == "HalfCircle":
                return self.canvas.create_arc(*c1_min, *c2_max,
                                              start=180, extent=180,
                                              outline="gray", dash=(4, 2),
                                              style=tk.ARC)
            else:  # "QuarterCircle"
                return self.canvas.create_arc(*c1_min, *c2_max,
                                              start=270, extent=90,
                                              outline="gray", dash=(4, 2),
                                              style=tk.ARC)

        else:
            return None

    # ---------------------------
    # 7) Centroid Calculation
    # ---------------------------
    def calculate_composite_centroid(self):
        if not self.shapes:
            self.centroid_label.config(text="Composite Centroid: (N/A, N/A)")
            return

        total_area = 0.0
        sum_xA = 0.0
        sum_yA = 0.0

        for s in self.shapes:
            A = s.calculate_area()
            cx, cy = s.calculate_centroid()
            total_area += A
            sum_xA += cx * A
            sum_yA += cy * A

        if abs(total_area) < 1e-9:
            self.centroid_label.config(text="Composite Centroid: (N/A, N/A)")
            return

        comp_x = sum_xA / total_area
        comp_y = sum_yA / total_area
        self.centroid_label.config(
            text=f"Composite Centroid: ({comp_x:.2f}, {comp_y:.2f})"
        )

        # Draw a red cross
        ccx, ccy = to_canvas_coords(comp_x, comp_y)
        self.canvas.create_line(ccx - 5, ccy, ccx + 5, ccy, fill="red", width=2)
        self.canvas.create_line(ccx, ccy - 5, ccx, ccy + 5, fill="red", width=2)

    # >>> ADDED: Import Shapes
    def import_shapes(self):
        """
        Import shapes from a JSON file.
        """
        file_path = filedialog.askopenfilename(
            title="Import Shapes",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_shapes = []
            for shape_data in data.get("shapes", []):
                shape = Shape.from_dict(shape_data)
                if shape:
                    imported_shapes.append(shape)
                else:
                    print("Unknown shape type:", shape_data.get("type"))
            
            self.shapes.extend(imported_shapes)
            self.redraw_all()
            messagebox.showinfo("Import Successful", f"Imported {len(imported_shapes)} shapes.")
        
        except Exception as e:
            messagebox.showerror("Import Failed", f"An error occurred:\n{e}")
    # <<< ADDED

    # >>> ADDED: Export Shapes
    def export_shapes(self):
        """
        Export current shapes to a JSON file.
        """
        if not self.shapes:
            messagebox.showwarning("No Shapes", "There are no shapes to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Shapes",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            data = {
                "shapes": [shape.to_dict() for shape in self.shapes]
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Export Successful", f"Exported {len(self.shapes)} shapes.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")
    # <<< ADDED

    # >>> ADDED: Help Documentation
    def show_help(self):
        """
        Show help documentation in a message box.
        """
        help_text = """Interactive Centroid Finder - Help

    1. Adding Shapes:
    - Select a shape from the dropdown menu.
    - Click 'Add Shape (Mouse)' and use the mouse to draw the shape on the canvas.
    - Alternatively, click 'Add Shape by Coordinates' to input shape parameters manually.

    2. Importing Shapes:
    - Click the 'Import' button.
    - Select a JSON file containing shapes to load them onto the canvas.

    3. Exporting Shapes:
    - Click the 'Export' button.
    - Choose a location to save the current shapes to a JSON file.

    4. Recalculating Centroid:
    - Click 'Recalculate Centroid' to update the composite centroid based on all shapes.

    5. Deleting Shapes:
    - Click 'Delete Shape' to enter delete mode.
    - Click on a shape to remove it from the canvas.

    6. Composite Centroid:
    - The current composite centroid is displayed on the toolbar and marked with a red cross on the canvas.

    7. General Tips:
    - Ensure to save your shapes using the 'Export' feature to avoid losing data.
    - Imported shapes will retain their properties and can be further manipulated.
        """
        messagebox.showinfo("Help Documentation", help_text)

    # <<< ADDED

# ----------------------------------------------------------------
# Run the Application
# ----------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CentroidApp(root)
    root.mainloop()
