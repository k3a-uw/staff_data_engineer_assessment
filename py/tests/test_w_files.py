import filecmp
import sys

# TEST 1 SMOKE TEST

run_file = 'build_clinician_mart.py'
config_file = './configs/clinician_mart.yml'
output_file = './data/silver/clinician_mart_latest.csv'

tests = [
    {
        "Name": "Smoke",
        "clin_file": './tests/clinician_smoke.csv',
        "prov_file": './tests/provider_smoke.csv',
        "assertion": './tests/assertion_smoke.csv'
    },
    {
        "Name": "Duplicates",
        "clin_file": './tests/clinician_duplicates.csv',
        "prov_file": './tests/provider_duplicates.csv',
        "assertion": './tests/assertion_duplicates.csv'
    },
    {
        "Name": "FilterEmpty",
        "clin_file": './tests/clinician_filter_empty.csv',
        "prov_file": './tests/provider_filter_empty.csv',
        "assertion": './tests/assertion_filter_empty.csv'
    },
    {
        "Name": "FilterMixed",
        "clin_file": './tests/clinician_filter_mixed.csv',
        "prov_file": './tests/provider_filter_mixed.csv',
        "assertion": './tests/assertion_filter_mixed.csv'
    },
    {
        "Name": "NPI Transform",
        "clin_file": './tests/clinician_npi.csv',
        "prov_file": './tests/provider_npi.csv',
        "assertion": './tests/assertion_npi.csv'
    }
]


tmpArgs = sys.argv

for test in tests:
    with open(run_file, "rb") as src:
        code = src.read()
        sys.argv = [run_file,
                    '-c', test['clin_file'],
                    '-p', test['prov_file'],
                    '-y', config_file]

        exec(code)

        print(f"Running test:{test['Name']}...", end="")
        assert(filecmp.cmp(output_file, test['assertion']))
        print(f"PASSED")


sys.argv = tmpArgs