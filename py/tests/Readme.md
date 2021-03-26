# Test File Descriptions

## Test 1:  Happy Path / Smoke Test
This test is a simple happy path test to make sure things run as expected with a subset of standard provided records.
- _clinician_smoke.csv_ - subset of initial clinician file containing standard/expected data for clinicians (15 records)
- _provider_smoke.csv_ - subset of initial clinician file containing standard/expected data for providers (15 records)
- _assertion_smoke.csv_ - the expected result of the script (12 records)

## Test 2: Duplicates
This test ensures the de-duplication within and across files is performing as expected.
- _clinician_dup.csv_ - file containing clinicians that are duplicated within this file, and across the provider file (11 records)
- _provider_dup.csv_ - file containing providers that are duplicated within this file and records duplicated across files (10 records)
- _assertion_dup.csv_ - the expected result of duplicate test (9 records)

## Test 3a: Clinician Filter: Empty
This test ensures no failure when ALL records are filtered out.  An empty file should result.
- _clinician_filter_empty.csv_ - file containing no clinician titles (No Dr.) (5 Records)
- _provider_filter_empty.csv_ - file containing no clinician titles (No Dr.) (5 Records)
- _assertion_filter_empty.csv_ - the expected result of filter empty test (0 Records)

## Test 3a: Clinician Filter: Mixed
This test verifies that the proper filter is being applied, and the resulting file contains no "Dr."
- _clinician_filter_mixed.csv_ - file containing no clinician titles (No Dr.)
- _provider_filter_mixed.csv_ - file containing no clinician titles (No Dr.)
- _assertion_filter_mixed.csv_ - the expected result of filter mixed test

## Test 4: NPI Transform
This test makes sure that the NPIs that are written do so with various inputs such as multiple hyphens, no hyphens, or single hyphens at the end fo the number.
- _clinician_npi.csv_ - file containing a mixture of NPI configurations
- _clinician_npi.csv_ - file containing a mixture of NPI configurations
- _assertion_npi.csv_ - the expected results of the npi transform test