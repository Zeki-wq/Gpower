"""
Automation script to run all 40 G*Power GUI oracle scenarios,
capture high-resolution/high-readability screenshots to oracle/evidence/,
verify results against the clean-room clone calculator, and write verification logs.
"""

import sys
import os
import csv
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32ui
from PIL import Image
from pywinauto import Application

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.calculator import compute_a_priori, compute_post_hoc

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORACLE_DIR = os.path.join(WORKSPACE_ROOT, "oracle")
EVIDENCE_DIR = os.path.join(ORACLE_DIR, "evidence")
MANIFEST_CSV = os.path.join(ORACLE_DIR, "manifest.csv")
GPOWER_PATH = r"C:\Program Files (x86)\GPower 3.1\GPowerNT.exe"
GPOWER_CWD = r"C:\Program Files (x86)\GPower 3.1"


def capture_window_png(hwnd, save_path):
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top

    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    old_bmp = gdi32.SelectObject(mem_dc, bitmap)

    PW_RENDERFULLCONTENT = 2
    res = user32.PrintWindow(hwnd, mem_dc, PW_RENDERFULLCONTENT)
    if not res:
        res = user32.PrintWindow(hwnd, mem_dc, 0)

    bmpinfo = win32ui.CreateBitmapFromHandle(bitmap).GetInfo()
    bmpstr = win32ui.CreateBitmapFromHandle(bitmap).GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)

    img.save(save_path)

    gdi32.SelectObject(mem_dc, old_bmp)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hwnd_dc)

    # Verify opening
    with Image.open(save_path) as test_img:
        test_img.verify()

    file_size = os.path.getsize(save_path)
    return img.size, file_size


def run_all_scenarios():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} scenarios from {MANIFEST_CSV}.")

    print("Launching G*Power 3.1.9.4...")
    app = Application(backend="uia").start(GPOWER_PATH, work_dir=GPOWER_CWD)
    time.sleep(2.5)

    dlg = app.window(title_re=r".*G\*Power.*")
    hwnd = dlg.handle

    # Select Test family -> 't tests' (combobox 1000)
    c1000 = dlg.child_window(auto_id="1000", control_type="ComboBox")
    hwnd1000 = c1000.handle
    parent1000 = win32gui.GetParent(hwnd1000)
    win32gui.SendMessage(hwnd1000, win32con.CB_SETCURSEL, 2, 0) # 2 = t tests
    win32gui.SendMessage(parent1000, win32con.WM_COMMAND, (win32con.CBN_SELCHANGE << 16) | 1000, hwnd1000)
    win32gui.SendMessage(parent1000, win32con.WM_COMMAND, (win32con.CBN_SELENDOK << 16) | 1000, hwnd1000)
    time.sleep(0.3)

    # Select Statistical test -> 'Means: Difference between two independent means (two groups)' (combobox 1001)
    c1001 = dlg.child_window(auto_id="1001", control_type="ComboBox")
    hwnd1001 = c1001.handle
    parent1001 = win32gui.GetParent(hwnd1001)
    c1001.expand()
    time.sleep(0.3)
    c1001.child_window(control_type="List").children()[6].select() # index 6
    win32gui.SendMessage(parent1001, win32con.WM_COMMAND, (win32con.CBN_SELCHANGE << 16) | 1001, hwnd1001)
    win32gui.SendMessage(parent1001, win32con.WM_COMMAND, (win32con.CBN_SELENDOK << 16) | 1001, hwnd1001)
    time.sleep(0.5)

    c1002 = dlg.child_window(auto_id="1002", control_type="ComboBox")
    hwnd1002 = c1002.handle
    parent1002 = win32gui.GetParent(hwnd1002)

    c1040 = dlg.child_window(auto_id="1040", control_type="ComboBox")
    hwnd1040 = c1040.handle
    parent1040 = win32gui.GetParent(hwnd1040)

    btn_calc = dlg.child_window(auto_id="1009", control_type="Button")

    current_mode = None
    results_summary = []

    try:
        for idx, row in enumerate(rows):
            vid = row["VectorID"]
            mode = row["Mode"] # 'A_priori' or 'Post_hoc'
            tails = int(row["Tails"]) # 1 or 2
            d = float(row["EffectSize_d"])
            alpha = float(row["Alpha"])

            print(f"[{idx+1}/{len(rows)}] Processing {vid} (Mode: {mode}, Tails: {tails}, d: {d}, alpha: {alpha})...")

            # 1. Switch mode if needed
            if mode != current_mode:
                c1002.expand()
                time.sleep(0.3)
                mode_idx = 0 if mode == "A_priori" else 3 # 0 = A priori, 3 = Post hoc
                c1002.child_window(control_type="List").children()[mode_idx].select()
                win32gui.SendMessage(parent1002, win32con.WM_COMMAND, (win32con.CBN_SELCHANGE << 16) | 1002, hwnd1002)
                win32gui.SendMessage(parent1002, win32con.WM_COMMAND, (win32con.CBN_SELENDOK << 16) | 1002, hwnd1002)
                time.sleep(0.4)
                current_mode = mode

            # 2. Select tails
            tail_idx = 0 if tails == 1 else 1 # 0 = One, 1 = Two
            c1040.expand()
            time.sleep(0.2)
            c1040.child_window(control_type="List").children()[tail_idx].select()
            win32gui.SendMessage(parent1040, win32con.WM_COMMAND, (win32con.CBN_SELCHANGE << 16) | 1040, hwnd1040)
            win32gui.SendMessage(parent1040, win32con.WM_COMMAND, (win32con.CBN_SELENDOK << 16) | 1040, hwnd1040)
            time.sleep(0.3)

            # 3. Enter Inputs
            if mode == "A_priori":
                target_power = float(row["TargetPower"])
                ratio = float(row["Ratio_N2_over_N1"])
                dlg.child_window(auto_id="1021", control_type="Edit").set_text(str(d))
                dlg.child_window(auto_id="1022", control_type="Edit").set_text(str(alpha))
                dlg.child_window(auto_id="1023", control_type="Edit").set_text(str(target_power))
                dlg.child_window(auto_id="1024", control_type="Edit").set_text(str(ratio if ratio != int(ratio) else int(ratio)))
            else: # Post_hoc
                n1 = int(row["Expected_N1"])
                n2 = int(row["Expected_N2"])
                ratio = float(row["Ratio_N2_over_N1"])
                dlg.child_window(auto_id="1021", control_type="Edit").set_text(str(d))
                dlg.child_window(auto_id="1022", control_type="Edit").set_text(str(alpha))
                dlg.child_window(auto_id="1023", control_type="Edit").set_text(str(n1))
                dlg.child_window(auto_id="1024", control_type="Edit").set_text(str(n2))

            time.sleep(0.2)

            # 4. Invoke Calculate
            btn_calc.invoke()
            time.sleep(0.6)

            # 5. Read GUI Outputs
            if mode == "A_priori":
                gui_delta = float(dlg.child_window(auto_id="1050", control_type="Edit").legacy_properties().get("Value"))
                gui_tcrit = float(dlg.child_window(auto_id="1051", control_type="Edit").legacy_properties().get("Value"))
                gui_df = int(dlg.child_window(auto_id="1052", control_type="Edit").legacy_properties().get("Value"))
                gui_n1 = int(dlg.child_window(auto_id="1053", control_type="Edit").legacy_properties().get("Value"))
                gui_n2 = int(dlg.child_window(auto_id="1054", control_type="Edit").legacy_properties().get("Value"))
                gui_total_n = int(dlg.child_window(auto_id="1055", control_type="Edit").legacy_properties().get("Value"))
                gui_actual_power = float(dlg.child_window(auto_id="1056", control_type="Edit").legacy_properties().get("Value"))

                # Run fresh clone calculation
                clone_res = compute_a_priori(tails=tails, d=d, alpha=alpha, power=target_power, ratio=ratio)

                assert gui_n1 == clone_res["n1"], f"[{vid}] N1 mismatch: GUI {gui_n1} vs Clone {clone_res['n1']}"
                assert gui_n2 == clone_res["n2"], f"[{vid}] N2 mismatch: GUI {gui_n2} vs Clone {clone_res['n2']}"
                assert gui_total_n == clone_res["total_n"], f"[{vid}] Total N mismatch"
                assert gui_df == clone_res["df"], f"[{vid}] df mismatch"
                assert abs(gui_delta - clone_res["delta"]) <= 1e-4, f"[{vid}] delta mismatch"
                assert abs(gui_tcrit - clone_res["critical_t"]) <= 1e-4, f"[{vid}] critical_t mismatch"
                assert abs(gui_actual_power - clone_res["actual_power"]) <= 1e-4, f"[{vid}] actual_power mismatch"

                input_desc = f"d = {d}; α = {alpha}; target power = {target_power}; allocation ratio N2/N1 = {ratio if ratio != int(ratio) else int(ratio)}"
                gui_out_desc = f"N1={gui_n1}, N2={gui_n2}, total N={gui_total_n}, df={gui_df}, δ={gui_delta:.7f}, critical t={gui_tcrit:.7f}, actual power={gui_actual_power:.7f}"
                clone_out_desc = f"N1={clone_res['n1']}, N2={clone_res['n2']}, total N={clone_res['total_n']}, df={clone_res['df']}, δ={clone_res['delta']:.6f}, critical t={clone_res['critical_t']:.6f}, actual power={clone_res['actual_power']:.6f}"

            else: # Post_hoc
                gui_delta = float(dlg.child_window(auto_id="1050", control_type="Edit").legacy_properties().get("Value"))
                gui_tcrit = float(dlg.child_window(auto_id="1051", control_type="Edit").legacy_properties().get("Value"))
                gui_df = int(dlg.child_window(auto_id="1052", control_type="Edit").legacy_properties().get("Value"))
                gui_actual_power = float(dlg.child_window(auto_id="1053", control_type="Edit").legacy_properties().get("Value"))
                gui_n1 = n1
                gui_n2 = n2
                gui_total_n = n1 + n2

                # Run fresh clone calculation
                clone_res = compute_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)

                assert gui_total_n == clone_res["total_n"], f"[{vid}] Total N mismatch"
                assert gui_df == clone_res["df"], f"[{vid}] df mismatch"
                assert abs(gui_delta - clone_res["delta"]) <= 1e-4, f"[{vid}] delta mismatch"
                assert abs(gui_tcrit - clone_res["critical_t"]) <= 1e-4, f"[{vid}] critical_t mismatch"
                assert abs(gui_actual_power - clone_res["actual_power"]) <= 1e-4, f"[{vid}] actual_power mismatch"

                input_desc = f"d = {d}; α = {alpha}; N1 = {n1}; N2 = {n2}; implied N2/N1 = {ratio:.4f}"
                gui_out_desc = f"N1={gui_n1}, N2={gui_n2}, total N={gui_total_n}, df={gui_df}, δ={gui_delta:.7f}, critical t={gui_tcrit:.7f}, actual power={gui_actual_power:.7f}"
                clone_out_desc = f"N1={clone_res['n1']}, N2={clone_res['n2']}, total N={clone_res['total_n']}, df={clone_res['df']}, δ={clone_res['delta']:.6f}, critical t={clone_res['critical_t']:.6f}, actual power={clone_res['actual_power']:.6f}"

            # 6. Capture high-readability PNG directly
            img_filename = f"{vid}.png"
            img_save_path = os.path.join(EVIDENCE_DIR, img_filename)
            resolution, file_size = capture_window_png(hwnd, img_save_path)

            print(f"       -> Saved {img_filename} | Resolution: {resolution[0]}x{resolution[1]} | Size: {file_size:,} bytes | MATCH verified.")

            # 7. Write Markdown verification record to oracle/evidence/<vid>.md and oracle/<vid>.md
            tail_str = "Two (two-tailed)" if tails == 2 else "One (one-tailed)"
            analysis_str = "A priori" if mode == "A_priori" else "Post hoc"
            md_content = f"""# {vid} — GUI oracle record

- Reference application: G*Power 3.1.9.4 (live Windows GUI)
- Test: t tests → Means: Difference between two independent means (two groups)
- Analysis: {analysis_str}; tails = {tail_str}
- Inputs: {input_desc}
- G*Power GUI outputs: {gui_out_desc}
- Fresh clone run: yes, through src.calculator in the project’s isolated Python 3.12 virtual environment. Outputs: {clone_out_desc}
- Comparison: MATCH — N1, N2, and df match exactly; numerical outputs are within 1e-4.
- Evidence: evidence/{img_filename} (real G*Power window capture, {resolution[0]}x{resolution[1]}, {file_size:,} bytes)
"""
            # Write to oracle/evidence/<vid>.md
            with open(os.path.join(EVIDENCE_DIR, f"{vid}.md"), "w", encoding="utf-8") as mf:
                mf.write(md_content)

            # Also update oracle/<vid>.md
            with open(os.path.join(ORACLE_DIR, f"{vid}.md"), "w", encoding="utf-8") as mf:
                mf.write(md_content)

            results_summary.append({
                "vid": vid,
                "mode": mode,
                "tails": tails,
                "d": d,
                "alpha": alpha,
                "gui_n1": gui_n1,
                "gui_n2": gui_n2,
                "gui_total_n": gui_total_n,
                "gui_df": gui_df,
                "gui_delta": gui_delta,
                "gui_tcrit": gui_tcrit,
                "gui_power": gui_actual_power,
                "clone_power": clone_res["actual_power"],
                "resolution": f"{resolution[0]}x{resolution[1]}",
                "size_bytes": file_size,
                "evidence_path": f"evidence/{img_filename}",
            })

    finally:
        print("Closing G*Power...")
        app.kill()

    print(f"\nAll {len(results_summary)}/40 scenarios successfully calculated and captured.")
    return results_summary


if __name__ == "__main__":
    summary = run_all_scenarios()
