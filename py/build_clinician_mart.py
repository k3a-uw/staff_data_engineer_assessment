import pandas as pd
import argparse
from datetime import datetime
import os
import sys
import yaml
"""
    CLINICIAN MART BUILDER
    This script collects two files (clinician and providers) and stacks them, with some minor transformations
    and saves the result to a folder.  Default behavior is to create stage files in a bronze/ folder for providence and
    the results in two ways, one as a "latest" version of the file (overwriting the previous version) and a "timestamp"
    version for providence.
    Example:
        ./bronze/clinician_raw_1234567890.csv
        ./bronze/provider_raw_1234567890.csv
        ./silver/clinician_mart_latest.csv
        ./silver/clinician_mart_1234567890.csv    
"""
__author__ = "Kevin Anderson"
__email__ = "KevinAndersonIT@gmail.com"


def get_config():
    """
    Parses command line arguments and provided configuration YAML, verify existence of folders, and return the full
    config in a single dictionary, including the two input files provided in the config.
    :return: A dictionary with full configuration.
    """
    arg_parser = argparse.ArgumentParser(description="This script combines clinician and provider data into one mart.")
    arg_parser.add_argument('-c', '--clinician', help="Relative file path to clinicians file.", required=True)
    arg_parser.add_argument('-p', '--provider', help="Relative file path to the providers file.", required=True)
    arg_parser.add_argument('-y', '--config', help="Relative file path of the configuration yaml for this script",
                            required=True),
    args = arg_parser.parse_args()

    # FIRST VERIFY CONFIGURATION FILE
    if not os.path.exists(args.config):
        print(f"UNABLE TO FIND CONFIG FILE, Please try again.")
        sys.exit(1)

    # PARSE CONFIG AND GET ADDITIONAL FILES AS NEEDED
    with open(args.config) as configfile:
        the_config = yaml.load(configfile, Loader=yaml.SafeLoader)

    errors = []
    paths_to_check = [args.clinician, args.provider, the_config['stage_folder'], the_config['mart_folder']]
    for p in paths_to_check:
        if not os.path.exists(p):
            errors.append(f"{p} is not a valid path.")

    if len(errors) > 0:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"One or more of your inputs are invalid, please verify.  For help type {os.path.basename(__file__)} -h")
        sys.exit(1)

    the_config['clinician_source'] = args.clinician
    the_config['provider_source'] = args.provider
    return the_config


def get_curr_ts_epoch_sec():
    """
    Returns the current system time in epoch second time.  This ensures there is no confusion
    about timezones as epoch sec is always seconds since 1970-1-1 0:00:00 UTC
    :return: int / bigint representing the current timestamp in epoch seconds.
    """
    return int(datetime.now().timestamp())


def get_curr_ts_zulu():
    """
    Returns the current system time in standard Zulu (UTC time format) (i.e. YYYY-MM-DDTHH:MM:SSZ)
    :return: String representation fo the current time in Zulu Format
    """
    zulu_fmt = '%Y-%m-%dT%H:%M:%SZ'
    return datetime.utcnow().strftime(zulu_fmt)


def transform_filter(df_data, field, values, inclusive=True):
    """
    Return a copy of the provided dataset that includes only rows with the provided field containing the
    prescribed list of values.  Can be used as inclusive return only rows with this value, or exclusive
    (inclusive=False) which will remove rows contained in values.
    :param df_data: The dataframe containing the data to be filtered.
    :param field: The column / field on which to filter.
    :param values: The list of possible values to consider for inclusion.
    :return: The provided dataframe to deduplicate.
    """
    if inclusive:
        return df_data.loc[df_data[field].isin(values), :]
    else:
        return df_data.loc[~df_data[field].isin(values), :]


def transform_dedup(df_data, fields, keep='first'):
    """
    Return a copy of the provided dataset that is deduplicated by the specified fields.
    Assumes a "keep first" structure.  Could implement a more interesting scoring method for which to choose
    but considering there are no duplicates in the provided data sets, it's unclear what would take precedence.
    :param df_data: The provided dataframe to deduplicate
    :param fields: A list of column names to be included in the duplication.
    :return: A copy of df_data with data removed.
    """
    return df_data.loc[~df_data.duplicated(subset=fields, keep=keep), :]


def transform_npi_split(x):
    """
    Transforms a given hyphenated NPI into the substring following the first hyphen (-).  If the object X is `None` or
    otherwise not castable as str `apply_npi_transform` will return an empty string.  Additionally, a string without
    a hyphen will be returned unmodified, containing a single hyphen at its end will also return an empty string.
    :param x: The string NPI to be transformed.
    :return: The transformed or empty string representing the NPI as described above.
    """
    if x is None:
        return ''
    else:
        try:
            str_x = x
            return x[x.find('-')+1:]
        except ValueError:
            return ''


if __name__ == "__main__":
    # GET CONFIG FROM COMMAND LINE
    config = get_config()

    # READ DATA FROM SOURCE FILES THESE FILES ARE KNOWN TO HAVE 4 ROWS TO IGNORE AT FRONT.
    df_raw_clinicians = pd.read_csv(config['clinician_source'], skiprows=4, na_filter="")
    df_raw_providers = pd.read_csv(config['provider_source'], skiprows=4, na_filter="")

    # SETS STAGE FILENAMES ./data/bronze/clinician_raw_188828128.csv
    tgt_file_clinicians = f"{config['stage_folder']}/clinician_raw_{get_curr_ts_epoch_sec()}.csv"
    tgt_file_providers = f"{config['stage_folder']}/provider_raw_{get_curr_ts_epoch_sec()}.csv"

    # WRITE THE RAW DATA BEFORE ANY MANIPULATIONS ARE PERFORMED.
    df_raw_providers.to_csv(tgt_file_clinicians, index=False)
    df_raw_clinicians.to_csv(tgt_file_providers, index=False)

    # BEGIN FORMING OF CLINICIAN MART
    df_clinician_mart = pd.DataFrame()

    # STACK COLUMNS WITH COMMON FIELD NAMES
    for col in config['target_cols']:
        tgt_col_name = col['name']
        c_col_name = col['source_cols']['clinicians']
        p_col_name = col['source_cols']['providers']
        df_clinician_mart[col['name']] = pd.concat([df_raw_clinicians[c_col_name],
                                                    df_raw_providers[p_col_name]])

    # TRANSFORMATIONS 1: FILTER FOR ONLY CLINICAL TITLE (DR.?)
    for incl_filter in config['standard_transforms']['inclusive_filters']:
        df_clinician_mart = transform_filter(df_clinician_mart, incl_filter['column'], incl_filter['values'])

    # TRANSFORMATIONS 2: TRANSFORM NPI TO ONLY POST HYPHEN values
    df_clinician_mart['npi'] = df_clinician_mart['npi'].apply(transform_npi_split)

    # TRANSFORMATIONS 3: DEDUPLICATE NPIS
    df_clinician_mart = transform_dedup(df_clinician_mart, ['npi'])

    target_file = f"{config['mart_folder']}/{config['target_prefix']}_%s.csv"
    df_clinician_mart.to_csv(target_file % 'latest', index=False)
    df_clinician_mart.to_csv(target_file % get_curr_ts_epoch_sec(), index=False)

    print(f"Done. Wrote {df_clinician_mart.shape[0]} rows to target")


##################   UNIT TESTS FOR PYTEST ###########################

def test_get_curr_ts_epoch_sec():
    curr_utc = datetime.utcnow()
    curr_timestamp = get_curr_ts_epoch_sec()
    curr_fr_timestamp = datetime.utcfromtimestamp(curr_timestamp)
    diff_secs = (curr_utc - curr_fr_timestamp).total_seconds()
    assert abs(diff_secs) < 5, "UTC Calculation should be be off by no more than 5 seconds."

def test_get_curr_ts_zulu():
    curr_utc = datetime.utcnow()
    funct_timestring = get_curr_ts_zulu()
    curr_timestring = curr_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert funct_timestring == curr_timestring, "Zulu timestring should be in pattern YYYY-MM-DDT:HH:MM:SSZ"

def test_transform_npi():
    tests = [
        ('1234567', '1234567'),  # NO HYPHEN
        ('12-123456', '123456'),  # SINGLE HYPHEN IN MIDDLE
        ('1-23-456', '23-456'),  # MULTIPLE HYPHENS
        ('-9999999', '9999999'),  # STARTING WITH HYPHEN
        ('9999999-', ''),  # ENDING WITH HYHPEN
        ('----', '---'),  # ALL HYPHENS
        (None, '') # NONE
    ]

    for test in tests:
        result = transform_npi_split(test[0])
        assert result == test[1], f"NPI Test: Expected {test[1]} got {result}"

def test_transform_dedup():
    col1 = [1,2,3,4,5,6,7]
    col2 = ['one','two','three','four','five','six','six']
    d = pd.DataFrame()
    d['col1'] = col1
    d['col2'] = col2

    # TEST KEEP FIRST
    result = transform_dedup(d, ['col2'], keep='first')

    col1_assert = [1,2,3,4,5,6]
    col2_assert = ['one','two','three','four','five','six']
    df_assert1 = pd.DataFrame()
    df_assert1['col1'] = col1_assert
    df_assert1['col2'] = col2_assert

    assert result.equals(df_assert1), "The generated Dataframes should equal (Keep First)"

    col1_assert = [1, 2, 3, 4, 5, 7]
    col2_assert = ['one', 'two', 'three', 'four', 'five', 'six']
    df_assert2 = pd.DataFrame()
    df_assert2['col1'] = col1_assert
    df_assert2['col2'] = col2_assert

    result2 = transform_dedup(d, ['col2'], keep='last')

    # COMPARE THE DATAFRAMES, WHILE IGNORING THEIR INDEXES
    assert result2.reset_index(drop=True).equals(df_assert2.reset_index(drop=True)), \
        "The generated Dataframes should equal (Keep Last)"

def test_transform_filter():
    col1 = [1,2,3,4,5,6,7]
    col2 = ['one','two','three','four','five','six','six']
    d = pd.DataFrame()
    d['col1'] = col1
    d['col2'] = col2

    # TEST KEEP FIRST
    result1 = transform_filter(d,field='col2', values=['one','two'], inclusive=True)

    col1_assert = [1,2]
    col2_assert = ['one','two']
    df_assert1 = pd.DataFrame()
    df_assert1['col1'] = col1_assert
    df_assert1['col2'] = col2_assert

    assert result1.reset_index(drop=True).equals(df_assert1.reset_index(drop=True)), \
        "The generated Dataframes should equal (Keep Last)"

    col1_assert = [3, 4, 5, 6, 7]
    col2_assert = ['three', 'four', 'five', 'six', 'six']
    df_assert2 = pd.DataFrame()
    df_assert2['col1'] = col1_assert
    df_assert2['col2'] = col2_assert

    result2 = transform_filter(d,field='col2', values=['one','two'], inclusive=False)
    print(result2)
    print(df_assert2)

    # COMPARE THE DATAFRAMES, WHILE IGNORING THEIR INDEXES
    assert result2.reset_index(drop=True).equals(df_assert2.reset_index(drop=True)), \
        "The generated Dataframes should equal (Keep Last)"
