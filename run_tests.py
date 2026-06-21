import runpy
import sys

TEST_FILES = [
    'placemux-company-funnel/tests/test_cleaning.py',
    'placemux-company-funnel/tests/test_metrics.py',
    'placemux-company-funnel/tests/test_funnel.py',
]

failures = 0
for tf in TEST_FILES:
    try:
        namespace = runpy.run_path(tf)
        for name, obj in namespace.items():
            if callable(obj) and name.startswith('test_'):
                try:
                    obj()
                    print(f'{tf}::{name} OK')
                except AssertionError as e:
                    print(f'{tf}::{name} FAIL: {e}')
                    failures += 1
    except Exception as e:
        print(f'Error running {tf}: {e}')
        failures += 1

if failures:
    print(f'Finished with {failures} failure(s)')
    sys.exit(1)
else:
    print('All tests passed')
    sys.exit(0)
