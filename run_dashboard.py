"""Helper to launch the Streamlit dashboard locally."""
import os
import sys

script = os.path.join('placemux-company-funnel', 'src', 'dashboard', 'app.py')
if not os.path.exists(script):
    print('Dashboard script not found:', script)
    sys.exit(1)

print('Run the dashboard with:')
print('  python -m streamlit run', script)
