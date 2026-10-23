"""Tkinter interface for the shared power-analysis engine."""

import json
import logging
import math
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from scipy import stats

from src.calculator import compute_power_analysis, SUPPORTED_MODES, ValidationError

KNOWN_TESTS = (
    "t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2",
)
FIELD_SETS = {
    "a-priori": ("d", "alpha", "power", "ratio"),
    "post-hoc": ("d", "alpha", "n1", "n2"),
    "sensitivity": ("alpha", "power", "n1", "n2"),
    "criterion": ("d", "power", "n1", "n2"),
    "compromise": ("d", "n1", "n2", "beta_alpha_ratio"),
}
EFFECT_FIELDS = {"t2-indep": "d", "t-paired": "dz", "anova-oneway": "f",
                 "chi2-contingency": "w", "multireg-r2": "f2"}
STRUCTURE_FIELDS = {"t2-indep": ("n1", "n2"), "t-paired": ("n_total",),
                    "anova-oneway": ("n_total", "groups"),
                    "chi2-contingency": ("n_total", "df"),
                    "multireg-r2": ("n_total", "predictors")}
INTEGER_FIELDS = {"n1", "n2", "n_total", "groups", "df", "predictors"}
LABELS = {
    "d": "Cohen's d", "dz": "Effect size dz", "f": "Effect size f",
    "w": "Effect size w", "f2": "Effect size f²", "alpha": "Alfa (α)",
    "power": "Güç (1−β)", "target_power": "Hedef güç", "actual_power": "Gerçekleşen güç",
    "ratio": "Tahsis oranı N2/N1", "n1": "Grup 1 örneklem N1",
    "n2": "Grup 2 örneklem N2", "n_total": "Toplam örneklem N",
    "groups": "Grup sayısı", "df": "Serbestlik derecesi (df)",
    "df1": "Pay serbestlik derecesi (df1)", "df2": "Payda serbestlik derecesi (df2)",
    "predictors": "Yordayıcı sayısı", "beta_alpha_ratio": "Beta/alfa oranı",
    "beta": "Beta (β)", "ncp": "Noncentrality (δ/λ)", "critical_t": "Kritik t",
    "critical_f": "Kritik F", "critical_chi2": "Kritik χ²", "tails": "Kuyruk sayısı",
}
DEFAULTS = {
    "alpha": "0.05", "power": "0.80", "ratio": "1.0", "beta_alpha_ratio": "1.0",
    "d": "0.5", "dz": "0.5", "f": "0.25", "w": "0.3", "f2": "0.15",
    "n1": "64", "n2": "64", "n_total": "100", "groups": "5", "df": "5", "predictors": "2",
}
RESULT_ORDER = (
    "n1", "n2", "n_total", "alpha", "target_power", "actual_power", "power",
    "d", "dz", "f", "w", "f2", "tails", "ratio", "groups", "predictors",
    "df", "df1", "df2", "critical_t", "critical_f", "critical_chi2", "ncp", "beta",
)


def _logger() -> logging.Logger:
    logger = logging.getLogger("gpower.ui")
    if not logger.handlers:
        try:
            log_dir = Path(__file__).resolve().parents[1] / "logs"
            log_dir.mkdir(exist_ok=True)
            handler = logging.FileHandler(log_dir / "ui.log", encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        except OSError:
            logging.basicConfig(level=logging.INFO)
    return logger


def fields_for(test: str, mode: str) -> tuple[str, ...]:
    fields = ["tails"] if test in {"t2-indep", "t-paired"} else []
    if mode != "sensitivity":
        fields.append(EFFECT_FIELDS[test])
    fields.extend({
        "a-priori": ("alpha", "power"), "post-hoc": ("alpha",),
        "sensitivity": ("alpha", "power"), "criterion": ("power",),
        "compromise": ("beta_alpha_ratio",),
    }[mode])
    if test == "t2-indep" and mode == "a-priori":
        fields.append("ratio")
    if mode != "a-priori":
        fields.extend(STRUCTURE_FIELDS[test])
    else:
        fields.extend(field for field in STRUCTURE_FIELDS[test] if field in {"groups", "df", "predictors"})
    return tuple(fields)


# Input rules mirror src.calculator._validate_dispatch so UI messages state the real constraint.
INTEGER_MINIMUM = {"n1": 2, "n2": 2, "n_total": 2, "groups": 2, "df": 1, "predictors": 1}
OPEN_UNIT_INTERVAL_FIELDS = {"alpha", "power"}
POSITIVE_FIELDS = {"d", "dz", "f", "w", "f2", "ratio", "beta_alpha_ratio"}


def parse_field_value(name: str, text: str):
    """Convert one entry's text to the engine type or raise ValidationError naming the field."""
    text = text.strip()
    if name in INTEGER_MINIMUM:
        expectation = f"{INTEGER_MINIMUM[name]} veya daha büyük bir tam sayı girilmelidir."
    elif name in OPEN_UNIT_INTERVAL_FIELDS:
        expectation = "0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir."
    elif name in POSITIVE_FIELDS:
        expectation = "0'dan büyük bir sayı girilmelidir."
    else:
        expectation = "geçerli bir sayı girilmelidir."
    message = f"{name}: {expectation}"
    if not text:
        raise ValidationError(f"{name}: değer boş bırakılamaz; {expectation}", "MISSING_PARAM", name)
    if name in INTEGER_MINIMUM:
        try:
            value = int(text)
        except ValueError:
            raise ValidationError(message, "INVALID_VALUE", name) from None
        if value < INTEGER_MINIMUM[name]:
            raise ValidationError(message, "OUT_OF_RANGE", name)
        return value
    try:
        value = float(text)
    except ValueError:
        raise ValidationError(message, "INVALID_VALUE", name) from None
    if not math.isfinite(value):
        raise ValidationError(message, "INVALID_VALUE", name)
    if name in OPEN_UNIT_INTERVAL_FIELDS and not 0 < value < 1:
        raise ValidationError(message, "OUT_OF_RANGE", name)
    if name in POSITIVE_FIELDS and value <= 0:
        raise ValidationError(message, "OUT_OF_RANGE", name)
    return value


def calculate(test: str, mode: str, parameters: dict) -> dict:
    """Use the same calculation engine as the CLI, MCP server and agent."""
    return compute_power_analysis(test, mode, **parameters)


def format_result_fields(result: dict) -> list[tuple[str, str]]:
    """Convert actual result fields into readable UI rows without inventing values."""
    rows = []
    for key in RESULT_ORDER:
        if key not in result:
            continue
        value = result[key]
        rendered = f"{value:.6g}" if isinstance(value, float) else str(value)
        label = "Hedef güç" if key == "power" and result.get("mode") == "a-priori" else LABELS.get(key, key)
        rows.append((label, rendered))
    return rows


def build_graph_data(result: dict, points: int = 241) -> dict:
    """Sample null and alternative densities using the distribution/result parameters."""
    if result.get("status") != "success":
        raise ValueError("Grafik için başarılı bir hesaplama sonucu gerekli.")
    if points < 20:
        raise ValueError("Grafik örnek sayısı en az 20 olmalıdır.")
    test = result.get("test")
    ncp = float(result["ncp"])
    if not math.isfinite(ncp):
        raise ValueError("Hesaplama sonucu geçerli bir noncentrality değeri içermiyor.")

    if test in {"t2-indep", "t-paired"}:
        df = float(result["df"])
        critical = float(result["critical_t"])
        tails = int(result["tails"])
        xmax = max(5.0, abs(ncp) + 4.0, critical + 3.0)
        xmin = -xmax
        x = [xmin + i * (xmax - xmin) / (points - 1) for i in range(points)]
        null_pdf = stats.t.pdf(x, df)
        alternative_pdf = stats.nct.pdf(x, df, ncp)
        critical_values = [-critical, critical] if tails == 2 else [critical]
        alpha_mask = [value <= -critical or value >= critical for value in x] if tails == 2 else [value >= critical for value in x]
        beta_mask = [abs(value) < critical for value in x] if tails == 2 else [value < critical for value in x]
        alpha_probability = float(stats.t.cdf(-critical, df) + stats.t.sf(critical, df)) if tails == 2 else float(stats.t.sf(critical, df))
        beta_probability = float(stats.nct.cdf(critical, df, ncp) - stats.nct.cdf(-critical, df, ncp)) if tails == 2 else float(stats.nct.cdf(critical, df, ncp))
        distribution = "t"
    elif test in {"anova-oneway", "multireg-r2"}:
        df1, df2 = float(result["df1"]), float(result["df2"])
        critical = float(result["critical_f"])
        xmax = max(float(stats.f.ppf(0.999, df1, df2)), critical + 2.0, ncp + 4.0, 5.0)
        x = [i * xmax / (points - 1) for i in range(points)]
        null_pdf = stats.f.pdf(x, df1, df2)
        alternative_pdf = stats.ncf.pdf(x, df1, df2, ncp)
        critical_values = [critical]
        alpha_mask = [value >= critical for value in x]
        beta_mask = [value < critical for value in x]
        alpha_probability = float(stats.f.sf(critical, df1, df2))
        beta_probability = float(stats.ncf.cdf(critical, df1, df2, ncp))
        distribution = "F"
    elif test == "chi2-contingency":
        df = float(result["df"])
        critical = float(result["critical_chi2"])
        xmax = max(float(stats.chi2.ppf(0.999, df)), critical + 4.0, ncp + 4.0, 8.0)
        x = [i * xmax / (points - 1) for i in range(points)]
        null_pdf = stats.chi2.pdf(x, df)
        alternative_pdf = stats.ncx2.pdf(x, df, ncp)
        critical_values = [critical]
        alpha_mask = [value >= critical for value in x]
        beta_mask = [value < critical for value in x]
        alpha_probability = float(stats.chi2.sf(critical, df))
        beta_probability = float(stats.ncx2.cdf(critical, df, ncp))
        distribution = "χ²"
    else:
        raise ValueError(f"Grafik için desteklenmeyen test: {test}")

    null_values = [float(value) for value in null_pdf]
    alternative_values = [float(value) for value in alternative_pdf]
    if not all(math.isfinite(value) and value >= 0 for value in null_values + alternative_values):
        raise ValueError("İstatistik dağılımından geçerli grafik verisi oluşturulamadı.")
    return {
        "distribution": distribution,
        "x": [float(value) for value in x],
        "null_pdf": null_values,
        "alternative_pdf": alternative_values,
        "critical_values": critical_values,
        "ncp": ncp,
        "alpha_mask": alpha_mask,
        "beta_mask": beta_mask,
        # Exact theoretical areas corresponding to the rendered regions.
        "alpha_probability": alpha_probability,
        "beta_probability": beta_probability,
        "alpha_area_label": "α/2" if test in {"t2-indep", "t-paired"} and tails == 2 else "α",
    }


def prepare_result_view(result: dict) -> tuple[list[tuple[str, str]], dict]:
    """Build the UI metrics and plot samples from one engine result."""
    return format_result_fields(result), build_graph_data(result)


# Plot margins (left, right-inset, top, bottom-inset) shared by the renderer and its verification.
PLOT_MARGINS = (60, 18, 25, 40)


def nice_ticks(low: float, high: float, target: int = 6) -> tuple[list[float], int]:
    """Return round tick positions inside [low, high] and the decimals needed to print them."""
    if not (math.isfinite(low) and math.isfinite(high)) or high <= low:
        raise ValueError("Eksen aralığı geçerli değil.")
    raw = (high - low) / target
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if raw <= m * magnitude)
    decimals = next((d for d in range(7) if abs(round(step, d) - step) < 1e-9 * max(1.0, step)), 6)
    first = math.ceil(low / step - 1e-9)
    ticks = []
    index = first
    while index * step <= high + 1e-9 * step:
        ticks.append(round(index * step, 10) + 0.0)
        index += 1
    return ticks, decimals


def draw_graph(canvas, graph_data: dict) -> None:
    """Draw distribution curves and critical values to the Tk canvas."""
    canvas.delete("all")
    width = max(320, int(canvas.winfo_width()))
    height = max(210, int(canvas.winfo_height()))
    left, right, top, bottom = PLOT_MARGINS[0], width - PLOT_MARGINS[1], PLOT_MARGINS[2], height - PLOT_MARGINS[3]
    x_values = graph_data["x"]
    null_values = graph_data["null_pdf"]
    alt_values = graph_data["alternative_pdf"]
    if len(x_values) < 2 or len(x_values) != len(null_values) or len(x_values) != len(alt_values):
        raise ValueError("Grafik verilerinin uzunlukları uyumlu değil.")
    xmax, xmin = max(x_values), min(x_values)
    ymax = max(max(null_values), max(alt_values))
    if not math.isfinite(ymax) or ymax <= 0 or xmax <= xmin:
        raise ValueError("Grafik için geçerli eksen aralığı oluşturulamadı.")
    ymax *= 1.08

    def point(x, y):
        return (left + (x - xmin) / (xmax - xmin) * (right - left),
                bottom - y / ymax * (bottom - top))

    null_pixels = [point(xv, yv) for xv, yv in zip(x_values, null_values)]
    curve_pixels = null_pixels + [point(xv, yv) for xv, yv in zip(x_values, alt_values)]
    critical_pixels = [point(c, 0)[0] for c in graph_data["critical_values"]]

    def free_alpha_label_spot(first, last, values):
        """Find a spot just above the H0 curve near the tail mass that touches no curve or critical line.

        Returns None when no clear spot exists so the caller keeps the original placement.
        """
        weights = values[first:last + 1]
        total = sum(weights)
        if total <= 0:
            return None
        centroid = sum(x_values[first + i] * w for i, w in enumerate(weights)) / total
        base_x, _ = point(centroid, 0)
        half_w, half_h = 16, 8
        for shift in (0, -14, 14, -28, 28, -42, 42):
            cx = base_x + shift
            if cx - half_w < left + 2 or cx + half_w > right - 2:
                continue
            curve_y = min((py for px_, py in null_pixels if abs(px_ - cx) <= half_w), default=bottom)
            for lift in range(14, 75, 10):
                cy = min(bottom - 8, curve_y) - lift
                if cy - half_h < top + 16:
                    break
                if any(abs(px_ - cx) <= half_w + 3 and abs(py - cy) <= half_h + 3 for px_, py in curve_pixels):
                    continue
                if any(abs(cxl - cx) <= half_w + 3 for cxl in critical_pixels):
                    continue
                return cx, cy
        return None

    def shade_mask(mask, values, color, label):
        start = None
        segments = []
        for index, selected in enumerate(mask + [False]):
            if selected and start is None:
                start = index
            elif not selected and start is not None:
                segments.append((start, index - 1))
                start = None
        for first, last in segments:
            indices = list(range(first, last + 1))
            coords = [left if first == 0 else point(x_values[first], 0)[0], bottom]
            for index in indices:
                coords.extend(point(x_values[index], values[index]))
            coords.extend([right if last == len(x_values) - 1 else point(x_values[last], 0)[0], bottom])
            canvas.create_polygon(*coords, fill=color, outline="", stipple="gray25")
            # Alpha labels go to clear space above the H0 curve near the tail; otherwise (and for beta)
            # keep the original placement in the lower portion of the shaded interval.
            spot = free_alpha_label_spot(first, last, values) if label.startswith("α") else None
            if spot is not None:
                label_x, label_y = spot
            else:
                midpoint = (first + last) // 2
                label_x, _ = point(x_values[midpoint], 0)
                label_y = bottom - (bottom - top) * 0.12
            canvas.create_text(label_x, label_y, text=label, fill=color, font=("Segoe UI", 9, "bold"))

    y_ticks, y_decimals = nice_ticks(0.0, ymax)
    for tick in y_ticks:
        _, yy = point(xmin, tick)
        if tick > 0:
            canvas.create_line(left, yy, right, yy, fill="#e4e8ef", width=1)
        canvas.create_line(left - 4, yy, left, yy, fill="#526174", width=1)
        canvas.create_text(left - 7, yy, text=f"{tick:.{y_decimals}f}", anchor="e", fill="#526174", font=("Segoe UI", 8))
    x_ticks, x_decimals = nice_ticks(xmin, xmax)
    for tick in x_ticks:
        xx, _ = point(tick, 0)
        canvas.create_line(xx, bottom, xx, bottom + 4, fill="#526174", width=1)
        canvas.create_text(xx, bottom + 6, text=f"{tick:.{x_decimals}f}", anchor="n", fill="#526174", font=("Segoe UI", 8))
    canvas.create_line(left, top, left, bottom, fill="#526174", width=1)
    canvas.create_line(left, bottom, right, bottom, fill="#526174", width=1)
    alpha_label = graph_data.get("alpha_area_label", "α")
    shade_mask(graph_data["alpha_mask"], null_values, "#168343", alpha_label)
    shade_mask(graph_data["beta_mask"], alt_values, "#b45309", "β")
    for values, color in ((null_values, "#2563eb"), (alt_values, "#e4572e")):
        coords = []
        for xv, yv in zip(x_values, values):
            coords.extend(point(xv, yv))
        canvas.create_line(*coords, fill=color, width=2, smooth=False)
    for critical in graph_data["critical_values"]:
        if xmin <= critical <= xmax:
            xx, _ = point(critical, 0)
            canvas.create_line(xx, top, xx, bottom, fill="#159447", width=2, dash=(5, 3))
    canvas.create_text((left + right) / 2, height - 12, text=f"Test istatistiği ({graph_data['distribution']})", fill="#263244")
    canvas.create_text(12, (top + bottom) / 2, text="Yoğunluk", angle=90, fill="#263244")
    legend = (("#2563eb", "H0"), ("#e4572e", "H1"), ("#168343", alpha_label),
              ("#b45309", "β"), ("#159447", "Kritik değer"))
    legend_x = left + 8
    for color, label in legend:
        if label == "Kritik değer":
            canvas.create_line(legend_x, top + 5, legend_x + 22, top + 5, fill=color, width=2, dash=(5, 3))
        else:
            canvas.create_line(legend_x, top + 5, legend_x + 22, top + 5, fill=color, width=2)
        canvas.create_text(legend_x + 26, top + 5, text=label, anchor="w", fill="#263244")
        legend_x += 57 if label not in {"Kritik değer"} else 115


class PowerAnalysisUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("G*Power Clone — Güç Analizi")
        root.geometry("1180x780")
        root.minsize(900, 650)
        self.test_var = tk.StringVar(value="t2-indep")
        self.mode_var = tk.StringVar(value="a-priori")
        self.tails_var = tk.StringVar(value="2")
        self.field_vars: dict[str, tk.StringVar] = {}
        self.result_labels: dict[str, ttk.Label] = {}
        self.graph_data: dict | None = None

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        calculator_tab = ttk.Frame(notebook, padding=12)
        agent_tab = ttk.Frame(notebook, padding=12)
        notebook.add(calculator_tab, text="Güç analizi")
        notebook.add(agent_tab, text="AI agent / MCP")
        self._build_calculator(calculator_tab)
        self._build_agent(agent_tab)

    def _build_calculator(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=0, minsize=330)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        inputs = ttk.Frame(parent)
        inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        results = ttk.Frame(parent)
        results.grid(row=0, column=1, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(1, weight=1)

        ttk.Label(inputs, text="Test ailesi").grid(row=0, column=0, sticky="w", pady=4)
        test_box = ttk.Combobox(inputs, textvariable=self.test_var, values=KNOWN_TESTS, state="readonly")
        test_box.grid(row=0, column=1, sticky="ew", pady=4)
        test_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_fields())
        ttk.Label(inputs, text="Analiz modu").grid(row=1, column=0, sticky="w", pady=4)
        mode_box = ttk.Combobox(inputs, textvariable=self.mode_var, values=sorted(SUPPORTED_MODES), state="readonly")
        mode_box.grid(row=1, column=1, sticky="ew", pady=4)
        mode_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_fields())
        self.tails_label = ttk.Label(inputs, text="Kuyruk sayısı")
        self.tails_label.grid(row=2, column=0, sticky="w", pady=4)
        self.tails_box = ttk.Combobox(inputs, textvariable=self.tails_var, values=("1", "2"), state="readonly")
        self.tails_box.grid(row=2, column=1, sticky="ew", pady=4)
        self.fields_frame = ttk.LabelFrame(inputs, text="Girdiler", padding=8)
        self.fields_frame.grid(row=3, column=0, columnspan=2, sticky="new", pady=8)
        self.status_label = ttk.Label(inputs, text="Eğitim ve istatistiksel planlama içindir.", wraplength=310)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Button(inputs, text="Hesapla", command=self._calculate).grid(row=5, column=0, sticky="w", pady=8)
        inputs.columnconfigure(1, weight=1)

        self.result_frame = ttk.LabelFrame(results, text="Hesaplama sonuçları", padding=8)
        self.result_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.result_frame.columnconfigure(1, weight=1)
        self.graph_canvas = tk.Canvas(results, background="white", highlightthickness=1,
                                      highlightbackground="#c8d0da", height=310)
        self.graph_canvas.grid(row=1, column=0, sticky="nsew")
        self.graph_canvas.bind("<Configure>", self._redraw_graph)
        self.output = ScrolledText(results, height=7, wrap="word")
        self.output.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.output.insert("1.0", "Parametreleri girip Hesapla düğmesine basın. Sonuçlar ve dağılım grafiği burada gösterilir.")
        self._refresh_fields()

    def _refresh_fields(self) -> None:
        for child in self.fields_frame.winfo_children():
            child.destroy()
        self.field_vars.clear()
        for row, name in enumerate(fields_for(self.test_var.get(), self.mode_var.get())):
            if name == "tails":
                continue
            ttk.Label(self.fields_frame, text=LABELS.get(name, name)).grid(row=row, column=0, sticky="w", padx=4, pady=3)
            variable = tk.StringVar(value=DEFAULTS.get(name, ""))
            self.field_vars[name] = variable
            ttk.Entry(self.fields_frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=4, pady=3)
        self.fields_frame.columnconfigure(1, weight=1)
        if self.test_var.get() in {"t2-indep", "t-paired"}:
            self.tails_label.grid()
            self.tails_box.grid()
        else:
            self.tails_label.grid_remove()
            self.tails_box.grid_remove()
        self.status_label.configure(text="Eğitim ve istatistiksel planlama içindir. Gerçek kişi/klinik verisi girmeyin.")

    def _show_results(self, result: dict) -> None:
        for child in self.result_frame.winfo_children():
            child.destroy()
        self.result_labels.clear()
        rows, graph_data = prepare_result_view(result)
        if not rows:
            raise ValueError("Hesaplama motoru gösterilebilir sonuç alanı döndürmedi.")
        for row, (label, value) in enumerate(rows):
            key = next((name for name in RESULT_ORDER if LABELS.get(name, name) == label), label)
            ttk.Label(self.result_frame, text=label).grid(row=row // 3, column=(row % 3) * 2, sticky="w", padx=(3, 8), pady=2)
            value_label = ttk.Label(self.result_frame, text=value, font=("Segoe UI", 9, "bold"))
            value_label.grid(row=row // 3, column=(row % 3) * 2 + 1, sticky="w", padx=(0, 16), pady=2)
            self.result_labels[key] = value_label
        self.graph_data = graph_data
        draw_graph(self.graph_canvas, self.graph_data)

    def _clear_results(self) -> None:
        self.graph_data = None
        self.graph_canvas.delete("all")
        for child in self.result_frame.winfo_children():
            child.destroy()
        self.result_labels.clear()

    def _redraw_graph(self, _event=None) -> None:
        if self.graph_data is not None:
            try:
                draw_graph(self.graph_canvas, self.graph_data)
            except Exception:
                _logger().exception("Grafik yeniden çizilirken hata oluştu")

    def _calculate(self) -> None:
        try:
            test, mode = self.test_var.get(), self.mode_var.get()
            parameters = {}
            if test in {"t2-indep", "t-paired"}:
                parameters["tails"] = int(self.tails_var.get())
            for name, variable in self.field_vars.items():
                parameters[name] = parse_field_value(name, variable.get())
            result = calculate(test, mode, parameters)
            self._show_results(result)
            text = json.dumps(result, indent=2, ensure_ascii=False)
            self.status_label.configure(text="Hesaplama tamamlandı; sonuç değerleri ve dağılım grafiği güncellendi.", foreground="#176b36")
        except (TypeError, ValueError, ValidationError) as error:
            _logger().info("Kullanıcı girdisi veya analiz hatası: %s", error, exc_info=True)
            text = json.dumps({"status": "error", "message": str(error), "field": getattr(error, "field", None)},
                              ensure_ascii=False, indent=2)
            self._clear_results()
            self.status_label.configure(text=f"Hesaplama yapılamadı. Girdileri kontrol edin: {error}", foreground="#a32929")
        except Exception as error:
            _logger().exception("UI hesaplama/sonuç/grafik akışı başarısız oldu")
            text = json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False, indent=2)
            self._clear_results()
            self.status_label.configure(text=f"Hesaplama başarısız oldu: {error}", foreground="#a32929")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)

    def _build_agent(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text=("Bu bölüm doğal dil isteğini LLM yapılandırması varsa MCP power_analysis aracına gönderir. "
                  "API anahtarı yoksa hesaplamayı taklit etmez; kurulum mesajı gösterir. "
                  "Yalnızca kurgusal/eğitim amaçlı senaryo girin; kişisel veya klinik bilgi göndermeyin."),
            wraplength=900,
        ).pack(anchor="w", pady=(0, 8))
        self.agent_input = ScrolledText(parent, height=5, wrap="word")
        self.agent_input.pack(fill="x", expand=False, pady=4)
        self.agent_button = ttk.Button(parent, text="Agent ile analiz et", command=self._run_agent)
        self.agent_button.pack(anchor="w", pady=6)
        self.agent_status = ttk.Label(parent, text="")
        self.agent_status.pack(anchor="w", pady=2)
        self.agent_output = ScrolledText(parent, height=14, wrap="word")
        self.agent_output.pack(fill="both", expand=True, pady=4)

    def _run_agent(self) -> None:
        from src.agent import GPowerAgent

        if str(self.agent_button["state"]) == "disabled":
            return
        question = self.agent_input.get("1.0", "end").strip()
        self.agent_button.configure(state="disabled")
        self.agent_status.configure(text="Agent isteği işliyor…")
        self.agent_output.delete("1.0", "end")
        self.agent_output.insert("1.0", "LLM yanıtı ve MCP hesabı bekleniyor. API yapılandırılmadıysa agent bunu açıkça bildirecek.")

        def run_agent():
            try:
                response = GPowerAgent().process_query(question)
            except Exception as error:
                _logger().exception("Agent arayüz akışı başarısız oldu")
                response = f"Agent işlemi başarısız oldu: {error}"
            self.root.after(0, self._finish_agent, response)

        threading.Thread(target=run_agent, daemon=True).start()

    def _finish_agent(self, response: str) -> None:
        self.agent_output.delete("1.0", "end")
        self.agent_output.insert("1.0", response)
        self.agent_button.configure(state="normal")
        self.agent_status.configure(text="İşlem tamamlandı.")


def main() -> None:
    root = tk.Tk()
    PowerAnalysisUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
