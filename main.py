import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from classifier import classify_dataset

class DataClassificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Classification Framework for AI/ML Projects")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 720)

        self.file_path = None
        self.df = None
        self.result = None
        self.chart_canvas = None

        self.setup_style()
        self.build_ui()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Metric.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Data Classification Framework",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="Classify institutional data by sensitivity and recommended usage",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 12))

        controls = ttk.LabelFrame(main, text="Dataset Selection", padding=10)
        controls.pack(fill="x", pady=(0, 10))

        self.path_var = tk.StringVar(value="No CSV selected")
        ttk.Entry(
            controls, textvariable=self.path_var, state="readonly"
        ).pack(side="left", fill="x", expand=True, padx=(0,8))

        ttk.Button(controls, text="Browse CSV", command=self.browse).pack(side="left", padx=3)
        ttk.Button(controls, text="Classify Data", command=self.classify).pack(side="left", padx=3)
        ttk.Button(controls, text="Export Report", command=self.export_report).pack(side="left", padx=3)
        ttk.Button(controls, text="Clear", command=self.clear).pack(side="left", padx=3)

        metrics = ttk.Frame(main)
        metrics.pack(fill="x", pady=(0,10))

        self.metric_vars = [
            tk.StringVar(value="Records\n—"),
            tk.StringVar(value="Columns\n—"),
            tk.StringVar(value="Confidential+\n—"),
            tk.StringVar(value="Average Score\n—")
        ]

        for var in self.metric_vars:
            box = ttk.LabelFrame(metrics, padding=8)
            box.pack(side="left", fill="x", expand=True, padx=3)
            ttk.Label(box, textvariable=var, style="Metric.TLabel", anchor="center").pack()

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)
        body.columnconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(body, text="Column-Level Classification", padding=6)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        cols = [
            ("Column", 150), ("Data Type", 90), ("Missing", 65),
            ("Score", 70), ("Classification", 150),
            ("Recommended Usage", 240), ("Reason", 280)
        ]

        self.tree = ttk.Treeview(
            table_frame, columns=[c[0] for c in cols], show="headings"
        )
        for name, width in cols:
            self.tree.heading(name, text=name)
            self.tree.column(name, width=width, anchor="center")

        vs = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        graph_frame = ttk.LabelFrame(body, text="Classification Distribution", padding=6)
        graph_frame.grid(row=1, column=0, sticky="nsew")
        self.graph_frame = graph_frame

        self.status_var = tk.StringVar(value="Ready — choose a CSV dataset.")
        ttk.Label(main, textvariable=self.status_var).pack(anchor="w", pady=(7,0))

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select CSV Dataset",
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self.file_path = path
            self.path_var.set(path)
            self.status_var.set("Dataset selected. Click Classify Data.")

    def classify(self):
        if not self.file_path:
            messagebox.showwarning("Dataset Required", "Please select a CSV file.")
            return

        try:
            self.df = pd.read_csv(self.file_path)
            if self.df.empty:
                raise ValueError("The dataset contains no records.")
            self.result = classify_dataset(self.df)
        except Exception as e:
            messagebox.showerror("Classification Error", str(e))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for _, r in self.result.iterrows():
            self.tree.insert("", "end", values=(
                r["Column"], r["Data Type"], r["Missing"],
                r["Sensitivity Score"], r["Classification"],
                r["Recommended Usage"], r["Reason"]
            ))

        counts = self.result["Classification"].value_counts()
        conf_plus = int(counts.get("Confidential",0) + counts.get("Highly Confidential",0))

        self.metric_vars[0].set(f"Records\n{len(self.df)}")
        self.metric_vars[1].set(f"Columns\n{len(self.df.columns)}")
        self.metric_vars[2].set(f"Confidential+\n{conf_plus}")
        self.metric_vars[3].set(f"Average Score\n{self.result['Sensitivity Score'].mean():.1f}")

        self.draw_graph(counts)

        self.status_var.set(
            f"Classification completed: {Path(self.file_path).name}"
        )

    def draw_graph(self, counts):
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        levels = ["Public", "Internal", "Confidential", "Highly Confidential"]
        values = [int(counts.get(x,0)) for x in levels]

        fig, ax = plt.subplots(figsize=(8,2.8))
        ax.bar(levels, values)
        ax.set_title("Number of Columns by Sensitivity Classification")
        ax.set_ylabel("Number of Columns")
        ax.set_ylim(bottom=0)
        ax.tick_params(axis="x", rotation=12)
        fig.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def export_report(self):
        if self.result is None:
            messagebox.showwarning("No Report", "Classify a dataset first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Classification Report",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx"), ("CSV report", "*.csv")]
        )
        if not path:
            return

        try:
            if path.lower().endswith(".xlsx"):
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    self.result.to_excel(writer, index=False, sheet_name="Classification")
                    summary = self.result["Classification"].value_counts().reindex(
                        ["Public","Internal","Confidential","Highly Confidential"], fill_value=0
                    ).reset_index()
                    summary.columns = ["Classification","Column Count"]
                    summary.to_excel(writer, index=False, sheet_name="Summary")
            else:
                self.result.to_csv(path, index=False)

            messagebox.showinfo("Export Complete", f"Report saved successfully:\n\n{path}")
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                "Could not export the report.\n\n"
                "For Excel export, install openpyxl with:\n"
                "pip install openpyxl\n\n" + str(e)
            )

    def clear(self):
        self.file_path = None
        self.df = None
        self.result = None
        self.path_var.set("No CSV selected")

        for var, text in zip(
            self.metric_vars,
            ["Records\n—","Columns\n—","Confidential+\n—","Average Score\n—"]
        ):
            var.set(text)

        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None

        self.status_var.set("Ready — choose a CSV dataset.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataClassificationApp(root)
    root.mainloop()
