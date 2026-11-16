RC-Filter-Verifier-

A Python-based automated verification framework designed to evaluate analog circuit designs against theoretical specifications without manual oscilloscope or waveform inspection. Developed as part of an independent engineering portfolio for hardware/software test automation roles.
🚀 Overview

In automated engineering evaluation workflows (such as AI-assisted circuit synthesis or automated grading pipelines), generated netlists must be programmatically verified against strict electrical performance criteria.

This tool:

    Executes batch-mode SPICE simulations (ngspice) on target netlists.
    Parses AC frequency response data via NumPy.
    Computes exact -3 dB cutoff frequencies using linear interpolation.
    Validates pass/fail compliance against defined engineering tolerances.
    Generates comparative Bode diagrams via Matplotlib and outputs structured JSON verification reports.

📂 Project Structure

rc_filter_verifier/
│
├── verify_filter.py         # Main test runner, parser, and verification engine
├── rc_valid.cir             # Reference low-pass filter netlist (fc = 1000 Hz)
├── rc_faulty_cap.cir        # Edge-case test: Wrong capacitor value (fc ~ 100 Hz)
├── rc_open_circuit.cir      # Edge-case test: Broken topology / floating node
├── bode_verification_plot.png # Generated frequency response visualization
└── requirements.txt         # Python dependencies

📊 Test Cases & Automated RubricTest CaseNetlist FileDescriptionExpected Result1. Reference Designrc_valid.cir$R = 1\text{k}\Omega$, $C = 159.15\text{nF}$PASS (fc = 1000 Hz $\pm$ 2%)2. Faulty Componentrc_faulty_cap.cir$C = 1.59\mu\text{F}$ (Incorrect value)FAIL (Out of tolerance deviation)3. Broken Topologyrc_open_circuit.cirFloating output node (No RC attenuation)FAIL (-3 dB threshold unreachable)🛠️ Installation & ExecutionPrerequisitesLinux (Pop!_OS / Ubuntu)ngspice simulator installed on host systemPython 3.8+Setup & RunBash# 1. Clone repository and navigate to folder
cd rc_filter_verifier

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install numpy scipy matplotlib

# 4. Run automated test suite
python verify_filter.py
📄 Sample JSON OutputJSON[
    {
        "test_case": "Valid Reference Design",
        "expected_cutoff_hz": 1000.0,
        "measured_cutoff_hz": 1000.03,
        "error_percentage": 0.003,
        "tolerance_percentage": 2.0,
        "passed": true,
        "error_reason": null
    },
    {
        "test_case": "Faulty Component (Wrong Cap)",
        "expected_cutoff_hz": 1000.0,
        "measured_cutoff_hz": 99.88,
        "error_percentage": 90.012,
        "tolerance_percentage": 2.0,
        "passed": false,
        "error_reason": "Cutoff frequency deviation (90.01%) exceeds 2.0% tolerance."
    }
]
EOF
---



```bash
cat << 'EOF' > requirements.txt
numpy>=1.20.0
scipy>=1.6.0
matplotlib>=3.3.0
EOF
