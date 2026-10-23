import pytest
import json
from types import MethodType

from src.calculator import ValidationError
from src import ui
from src.ui import FIELD_SETS, KNOWN_TESTS, calculate


def test_ui_calculate_calls_shared_engine_for_each_supported_mode():
    inputs = {
        "a-priori": {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0},
        "post-hoc": {"tails": 2, "d": 0.5, "alpha": 0.05, "n1": 64, "n2": 64},
        "sensitivity": {"tails": 2, "alpha": 0.05, "power": 0.8, "n1": 64, "n2": 64},
        "criterion": {"tails": 2, "d": 0.5, "power": 0.8, "n1": 64, "n2": 64},
        "compromise": {"tails": 2, "d": 0.5, "n1": 64, "n2": 64, "beta_alpha_ratio": 1.0},
    }
    for mode, parameters in inputs.items():
        assert calculate("t2-indep", mode, parameters)["status"] == "success"
        assert FIELD_SETS[mode]


def test_ui_does_not_fake_unsupported_family_results():
    assert "anova-oneway" in KNOWN_TESTS
    with pytest.raises(ValidationError, match="Bilinmeyen test ailes"):
        calculate("not-a-test", "post-hoc", {})


class _Var:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class _Label:
    def __init__(self):
        self.values = {}

    def configure(self, **kwargs):
        self.values.update(kwargs)


class _Output:
    def __init__(self):
        self.text = ""

    def delete(self, *_args):
        self.text = ""

    def insert(self, _index, text):
        self.text = text


def test_ui_calculate_callback_presents_engine_metrics_and_graph(monkeypatch):
    ui_instance = ui.PowerAnalysisUI.__new__(ui.PowerAnalysisUI)
    ui_instance.test_var = _Var("t2-indep")
    ui_instance.mode_var = _Var("a-priori")
    ui_instance.tails_var = _Var("2")
    ui_instance.field_vars = {
        "d": _Var("0.5"), "alpha": _Var("0.05"),
        "power": _Var("0.8"), "ratio": _Var("1"),
    }
    ui_instance.status_label = _Label()
    ui_instance.output = _Output()
    captured = {}
    real_calculate = ui.calculate
    calls = []

    def calculate_spy(test, mode, parameters):
        calls.append((test, mode, parameters))
        return real_calculate(test, mode, parameters)

    def show_result(self, result):
        rows, graph = ui.prepare_result_view(result)
        captured.update(result=result, rows=dict(rows), graph=graph)

    monkeypatch.setattr(ui, "calculate", calculate_spy)
    ui_instance._show_results = MethodType(show_result, ui_instance)
    ui_instance._clear_results = lambda: None
    ui_instance._calculate()

    assert calls == [("t2-indep", "a-priori", {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0})]
    assert captured["result"]["n1"] == captured["result"]["n2"] == 64
    assert captured["rows"]["Grup 1 örneklem N1"] == "64"
    assert captured["rows"]["Grup 2 örneklem N2"] == "64"
    assert captured["rows"]["Hedef güç"] == "0.8"
    assert captured["rows"]["Gerçekleşen güç"] == "0.80146"
    assert captured["rows"]["Kritik t"] == "1.97897"
    graph = captured["graph"]
    assert graph["distribution"] == "t"
    assert len(graph["x"]) == len(graph["null_pdf"]) == len(graph["alternative_pdf"]) == 241
    assert graph["critical_values"] == [-captured["result"]["critical_t"], captured["result"]["critical_t"]]
    assert graph["alternative_pdf"] != graph["null_pdf"]
    assert graph["alpha_area_label"] == "α/2"
    assert graph["alpha_probability"] == pytest.approx(0.05, abs=1e-10)
    assert graph["beta_probability"] == pytest.approx(1 - captured["result"]["actual_power"], abs=1e-10)
    assert "Hesaplama tamamlandı" in ui_instance.status_label.values["text"]
    assert json.loads(ui_instance.output.text)["status"] == "success"


def test_ui_shows_readable_validation_error_instead_of_silently_swallowing(monkeypatch):
    ui_instance = ui.PowerAnalysisUI.__new__(ui.PowerAnalysisUI)
    ui_instance.test_var = _Var("t2-indep")
    ui_instance.mode_var = _Var("a-priori")
    ui_instance.tails_var = _Var("2")
    ui_instance.field_vars = {"d": _Var("0"), "alpha": _Var("0.05"), "power": _Var("0.8"), "ratio": _Var("1")}
    ui_instance.status_label = _Label()
    ui_instance.output = _Output()
    ui_instance._clear_results = lambda: None
    ui_instance._calculate()
    assert "Girdileri kontrol edin" in ui_instance.status_label.values["text"]
    assert json.loads(ui_instance.output.text)["status"] == "error"


@pytest.mark.parametrize(("test", "parameters"), [
    ("t2-indep", {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0}),
    ("t-paired", {"tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.8}),
    ("anova-oneway", {"f": 0.25, "alpha": 0.05, "power": 0.8, "groups": 5}),
    ("chi2-contingency", {"w": 0.3, "alpha": 0.05, "power": 0.8, "df": 5}),
    ("multireg-r2", {"f2": 0.15, "alpha": 0.05, "power": 0.8, "predictors": 2}),
])
def test_graph_data_uses_valid_result_for_each_supported_family(test, parameters):
    result = calculate(test, "a-priori", parameters)
    graph = ui.build_graph_data(result)
    assert graph["distribution"] in {"t", "F", "χ²"}
    assert graph["ncp"] == result["ncp"]
    assert len(graph["x"]) == len(graph["null_pdf"]) == len(graph["alternative_pdf"])
    assert graph["critical_values"]
    assert graph["alpha_probability"] == pytest.approx(result["alpha"], abs=2e-6)
    assert graph["beta_probability"] == pytest.approx(1 - result.get("actual_power", result["power"]), abs=1e-10)


class _Canvas:
    def __init__(self):
        self.items = []

    def winfo_width(self):
        return 900

    def winfo_height(self):
        return 420

    def delete(self, *_args):
        self.items.clear()

    def create_line(self, *args, **kwargs):
        self.items.append(("line", args, kwargs))

    def create_text(self, *args, **kwargs):
        self.items.append(("text", args, kwargs))

    def create_polygon(self, *args, **kwargs):
        self.items.append(("polygon", args, kwargs))


def test_graph_renderer_shades_and_labels_alpha_beta_areas():
    result = calculate("t2-indep", "a-priori", {
        "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0,
    })
    canvas = _Canvas()
    ui.draw_graph(canvas, ui.build_graph_data(result))
    labels = [item[2].get("text") for item in canvas.items if item[0] == "text"]
    shaded_areas = [item for item in canvas.items if item[0] == "polygon"]
    assert labels.count("α/2") >= 2  # left and right rejection tails
    assert "β" in labels
    assert len(shaded_areas) >= 3  # two alpha tails and the beta area


# ---- Input error messages -------------------------------------------------

@pytest.mark.parametrize(("name", "text", "expected"), [
    ("alpha", "abc", "alpha: 0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir."),
    ("alpha", "0", "alpha: 0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir."),
    ("alpha", "1.5", "alpha: 0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir."),
    ("power", "nan", "power: 0 ile 1 arasında (0 ve 1 hariç) bir sayı girilmelidir."),
    ("d", "0", "d: 0'dan büyük bir sayı girilmelidir."),
    ("dz", "-1", "dz: 0'dan büyük bir sayı girilmelidir."),
    ("ratio", "inf", "ratio: 0'dan büyük bir sayı girilmelidir."),
    ("n1", "12.5", "n1: 2 veya daha büyük bir tam sayı girilmelidir."),
    ("n1", "1", "n1: 2 veya daha büyük bir tam sayı girilmelidir."),
    ("groups", "x", "groups: 2 veya daha büyük bir tam sayı girilmelidir."),
    ("df", "0", "df: 1 veya daha büyük bir tam sayı girilmelidir."),
    ("predictors", "-3", "predictors: 1 veya daha büyük bir tam sayı girilmelidir."),
])
def test_parse_field_value_reports_field_and_real_constraint(name, text, expected):
    with pytest.raises(ValidationError) as caught:
        ui.parse_field_value(name, text)
    assert str(caught.value) == expected
    assert caught.value.field == name


def test_parse_field_value_empty_and_valid_values():
    with pytest.raises(ValidationError, match=r"^alpha: değer boş bırakılamaz; 0 ile 1 arasında"):
        ui.parse_field_value("alpha", "  ")
    assert ui.parse_field_value("n1", " 64 ") == 64 and isinstance(ui.parse_field_value("n1", "64"), int)
    assert ui.parse_field_value("alpha", "0.05") == 0.05
    assert ui.parse_field_value("d", "1e-3") == 0.001


def test_ui_parser_rules_agree_with_engine_validation():
    """Values the UI parser accepts must not be rejected by the engine as out of range for that field."""
    base = {"alpha": 0.05, "power": 0.8, "d": 0.5, "ratio": 1.0, "n1": 64, "n2": 64}
    for name in ("alpha", "power", "d", "ratio", "n1", "n2"):
        for text in ("-1", "0", "1", "0.5", "2", "1.5", "64"):
            try:
                value = ui.parse_field_value(name, text)
            except ValidationError:
                value = None
            engine_params = {"tails": 2, **base, name: value if value is not None else float(text)}
            try:
                calculate("t2-indep", "post-hoc" if name in {"n1", "n2"} else "a-priori",
                          {k: v for k, v in engine_params.items()
                           if k in ({"tails", "d", "alpha", "n1", "n2"} if name in {"n1", "n2"} else
                                    {"tails", "d", "alpha", "power", "ratio"})})
                engine_rejects = False
            except ValidationError as error:
                engine_rejects = error.code in {"OUT_OF_RANGE", "INVALID_VALUE"} and error.field == name
            if name in {"n1", "n2"} and "." in text:
                engine_rejects = True  # engine requires int type; UI parser rejects fractional text
            assert (value is None) == engine_rejects, (name, text)


@pytest.mark.parametrize(("field_values", "expected_field", "forbidden"), [
    ({"alpha": "abc"}, "alpha", "could not convert"),
    ({"d": "0"}, "d", "pozitif olmalıdır"),
])
def test_ui_callback_shows_field_message_without_python_error(field_values, expected_field, forbidden):
    ui_instance = ui.PowerAnalysisUI.__new__(ui.PowerAnalysisUI)
    ui_instance.test_var, ui_instance.mode_var, ui_instance.tails_var = _Var("t2-indep"), _Var("a-priori"), _Var("2")
    values = {"d": "0.5", "alpha": "0.05", "power": "0.8", "ratio": "1"} | field_values
    ui_instance.field_vars = {k: _Var(v) for k, v in values.items()}
    ui_instance.status_label, ui_instance.output = _Label(), _Output()
    cleared = []
    ui_instance._clear_results = lambda: cleared.append(True)
    ui_instance._calculate()
    status = ui_instance.status_label.values["text"]
    assert f"{expected_field}:" in status and forbidden not in status
    payload = json.loads(ui_instance.output.text)
    assert payload["status"] == "error" and payload["field"] == expected_field
    assert cleared == [True]


def test_ui_callback_non_integer_sample_size_message():
    ui_instance = ui.PowerAnalysisUI.__new__(ui.PowerAnalysisUI)
    ui_instance.test_var, ui_instance.mode_var, ui_instance.tails_var = _Var("t2-indep"), _Var("post-hoc"), _Var("2")
    ui_instance.field_vars = {k: _Var(v) for k, v in {"d": "0.5", "alpha": "0.05", "n1": "12.5", "n2": "64"}.items()}
    ui_instance.status_label, ui_instance.output = _Label(), _Output()
    ui_instance._clear_results = lambda: None
    ui_instance._calculate()
    assert "n1: 2 veya daha büyük bir tam sayı girilmelidir." in ui_instance.status_label.values["text"]
    assert "invalid literal" not in ui_instance.status_label.values["text"]


# ---- Graph axes and label placement ----------------------------------------

def test_nice_ticks_are_round_and_inside_range():
    ticks, decimals = ui.nice_ticks(-5.5, 5.5)
    assert ticks == [-4.0, -2.0, 0.0, 2.0, 4.0] and decimals == 0
    ticks, decimals = ui.nice_ticks(0.0, 0.43)
    assert ticks[0] == 0.0 and ticks[-1] <= 0.43 and decimals >= 1
    assert all(b > a for a, b in zip(ticks, ticks[1:]))
    with pytest.raises(ValueError):
        ui.nice_ticks(1.0, 1.0)


class _RecordingCanvas(_Canvas):
    pass


def _render(test, parameters, mode="a-priori"):
    result = calculate(test, mode, parameters)
    graph = ui.build_graph_data(result)
    canvas = _RecordingCanvas()
    ui.draw_graph(canvas, graph)
    return graph, canvas


@pytest.mark.parametrize(("test", "parameters"), [
    ("t2-indep", {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0}),
    ("t-paired", {"tails": 1, "dz": 0.5, "alpha": 0.05, "power": 0.8}),
    ("anova-oneway", {"f": 0.25, "alpha": 0.05, "power": 0.8, "groups": 5}),
    ("chi2-contingency", {"w": 0.3, "alpha": 0.05, "power": 0.8, "df": 5}),
    ("multireg-r2", {"f2": 0.15, "alpha": 0.05, "power": 0.8, "predictors": 2}),
])
def test_graph_axes_have_numeric_ticks_matching_data_range(test, parameters):
    graph, canvas = _render(test, parameters)
    width, height = 900, 420
    left, right, top, bottom = ui.PLOT_MARGINS[0], width - ui.PLOT_MARGINS[1], ui.PLOT_MARGINS[2], height - ui.PLOT_MARGINS[3]
    x_ticks, y_ticks = [], []
    for kind, args, kwargs in canvas.items:
        text = kwargs.get("text", "") if kind == "text" else ""
        try:
            value = float(text)
        except ValueError:
            continue
        if kwargs.get("anchor") == "n":
            x_ticks.append((args[0], value))
        elif kwargs.get("anchor") == "e":
            y_ticks.append((args[1], value))
    assert len(x_ticks) >= 3 and len(y_ticks) >= 3
    xmin, xmax = min(graph["x"]), max(graph["x"])
    ymax = max(max(graph["null_pdf"]), max(graph["alternative_pdf"])) * 1.08
    for px, value in x_ticks:  # label position must map back to the labelled data value
        assert xmin - 1e-9 <= value <= xmax + 1e-9
        assert px == pytest.approx(left + (value - xmin) / (xmax - xmin) * (right - left), abs=1e-6)
    for py, value in y_ticks:
        assert 0 <= value <= ymax
        assert py == pytest.approx(bottom - value / ymax * (bottom - top), abs=1e-6)
    xs = sorted(px for px, _ in x_ticks)
    assert all(b - a >= 36 for a, b in zip(xs, xs[1:])), "x tick labels would overlap"
    ys = sorted(py for py, _ in y_ticks)
    assert all(b - a >= 14 for a, b in zip(ys, ys[1:])), "y tick labels would overlap"


def test_alpha_labels_avoid_curves_and_critical_lines_and_shading_is_unchanged():
    graph, canvas = _render("t2-indep", {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.8, "ratio": 1.0})
    curves = [kwargs for kind, args, kwargs in canvas.items if kind == "line" and "smooth" in kwargs]
    assert len(curves) == 2
    points = []
    for kind, args, kwargs in canvas.items:
        if kind == "line" and "smooth" in kwargs:
            points += list(zip(args[0::2], args[1::2]))
    criticals = [args[0] for kind, args, kwargs in canvas.items if kind == "line" and kwargs.get("dash") == (5, 3) and args[0] == args[2]]
    alpha_labels = [args for kind, args, kwargs in canvas.items if kind == "text" and kwargs.get("text") == "α/2" and kwargs.get("anchor") != "w"]
    assert len(alpha_labels) == 2 and len(criticals) == 2
    for x, y in alpha_labels:
        assert not any(abs(px - x) <= 16 and abs(py - y) <= 8 for px, py in points)
        assert all(abs(cx - x) > 16 for cx in criticals)
    assert len([i for i in canvas.items if i[0] == "polygon"]) == 3
    assert any(i[0] == "text" and i[2].get("text") == "β" for i in canvas.items)


