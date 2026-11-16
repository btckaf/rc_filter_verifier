import subprocess
import numpy as np
import matplotlib.pyplot as plt
import json
import os

def run_spice_simulation(netlist_file):
    result = subprocess.run(
        (["flatpak-spawn", "--host", "ngspice", "-b", netlist_file] if os.path.exists("/.flatpak-info") else ["ngspice", "-b", netlist_file]),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"SPICE Simulation Error in {netlist_file}:\n{result.stderr}")

def analyze_ac_response(case_name, output_file, expected_fc=1000.0, tolerance_pct=2.0):
    if not os.path.exists(output_file):
        return {
            "test_case": case_name,
            "passed": False,
            "error_reason": "Simulation output file missing."
        }, None, None

    data = np.loadtxt(output_file)
    freqs = data[:, 0]
    v_out = data[:, 1]
    target_v = 1.0 / np.sqrt(2)  # -3 dB point (~0.7071 V)

    # Edge-case check: Does the signal actually cross the -3dB threshold?
    if np.min(v_out) > target_v or np.max(v_out) < target_v:
        return {
            "test_case": case_name,
            "expected_cutoff_hz": expected_fc,
            "measured_cutoff_hz": None,
            "error_percentage": None,
            "passed": False,
            "error_reason": "Cutoff frequency (-3dB threshold) not reached within sweep range."
        }, freqs, v_out

    # Interpolate exact cutoff frequency
    measured_fc = float(np.interp(target_v, v_out[::-1], freqs[::-1]))
    error_pct = abs(measured_fc - expected_fc) / expected_fc * 100.0
    passed = bool(error_pct <= tolerance_pct)

    report = {
        "test_case": case_name,
        "expected_cutoff_hz": expected_fc,
        "measured_cutoff_hz": round(measured_fc, 2),
        "error_percentage": round(error_pct, 3),
        "tolerance_percentage": tolerance_pct,
        "passed": passed,
        "error_reason": None if passed else f"Cutoff frequency deviation ({round(error_pct, 2)}%) exceeds {tolerance_pct}% tolerance."
    }
    return report, freqs, v_out

def generate_bode_plot(plot_data, filename="bode_verification_plot.png"):
    plt.figure(figsize=(10, 5))
    for label, freqs, v_out in plot_data:
        if freqs is not None and v_out is not None:
            gain_db = 20 * np.log10(np.maximum(v_out, 1e-12))
            plt.semilogx(freqs, gain_db, linewidth=2, label=label)

    plt.axhline(-3.01, color="red", linestyle="--", linewidth=1, label="-3 dB Cutoff Threshold")
    plt.axvline(1000.0, color="green", linestyle=":", linewidth=1.2, label="Target fc (1000 Hz)")
    plt.title("Automated SPICE Verification: RC Low-Pass Frequency Response")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.grid(True, which="both", linestyle="-", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

if __name__ == "__main__":
    test_cases = [
        ("Valid Reference Design", "rc_valid.cir", "out_valid.txt"),
        ("Faulty Component (Wrong Cap)", "rc_faulty_cap.cir", "out_faulty.txt"),
        ("Broken Topology (Open Circuit)", "rc_open_circuit.cir", "out_open.txt"),
    ]

    full_report = []
    plot_series = []

    for name, netlist, out_txt in test_cases:
        run_spice_simulation(netlist)
        report, freqs, v_out = analyze_ac_response(name, out_txt)
        full_report.append(report)
        plot_series.append((name, freqs, v_out))

    generate_bode_plot(plot_series)
    print(json.dumps(full_report, indent=4))
    print("\nBode grafiği kaydedildi: bode_verification_plot.png")
