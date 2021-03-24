import pandas as pd
import argparse
from datetime import datetime
import os
import sys


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


def transform_dedup(df_data, fields, keep='last'):
    """
    Return a copy of the provided dataset that is deduplicated by the specified fields.
    Assumes a "keep last" structure.  Could implement a more interesting scoring method for which to choose
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
    arg_parser = argparse.ArgumentParser(description="This script combines clinician and provider data into one mart.")
    arg_parser.add_argument('-c', '--clinician', help="Relative file path to clinicians file.", required=True)
    arg_parser.add_argument('-p', '--provider', help="Relative file path to the providers file.", required=True)
    args = arg_parser.parse_args()

    if not (os.path.exists(args.clinician) and os.path.exists(args.provider)):
        print("Input File Not Found")  # TODO LOG ERROR
        sys.exit(1)

    # LOAD DATA FROM PROVIDED CSVS INTO MEMORY
    src_file_clinicians = args.clinician
    src_file_providers = args.provider

    df_raw_clinicians = pd.read_csv(src_file_clinicians, skiprows=4, na_filter="")
    df_raw_providers = pd.read_csv(src_file_providers, skiprows=4, na_filter="")

    # COPY DATA INTO STAGE (BRONZE)
    # TODO PARAMETERIZE TARGETS
    tgt_file_clinicians = f'data/bronze/clinician_raw_{get_curr_ts_epoch_sec()}.csv'
    tgt_file_providers = f'data/bronze/provider_raw_{get_curr_ts_epoch_sec()}.csv'

    df_raw_providers.to_csv(tgt_file_clinicians, index=False)
    df_raw_clinicians.to_csv(tgt_file_providers, index=False)

    # MAP_LIST IS A 3-TUPLE THAT HAS TARGET COLUMN, SOURCE1 COLUMN AND SOURCE2 COLUMN
    # TODO PARAMETERIZE MAPPING FILE
    map_list = [
        ('given_name', 'provider first', 'first name'),
        ('sur_name', 'provider last', 'last_name'),
        ('email_address', 'email address', 'email'),
        ('gender', 'Sex', 'gender'),
        ('care_center_name', 'Care Center Name', 'Care Center'),
        ('languages', 'primary language', 'languages'),
        ('NPI', 'NPI', 'NPI'),
        ('title', 'title', 'title')
    ]

    # BEGIN FORMING OF CLINICIAN MART
    df_clinician_mart = pd.DataFrame()

    # STACK COLUMNS WITH COMMON FIELD NAMES
    for m in map_list:
        df_clinician_mart[m[0]] = pd.concat([df_raw_clinicians[m[1]], df_raw_providers[m[2]]])

    # TRANSFORMATIONS 1: FILTER FOR ONLY CLINICAL TITLE (DR.?)
    df_clinician_mart = transform_filter(df_clinician_mart, 'title', ['Dr'])

    # TRANSFORMATIONS 2: TRANSFORM NPI TO ONLY POST HYPHEN values
    df_clinician_mart['NPI'] = df_clinician_mart['NPI'].apply(transform_npi_split)

    # TRANSFORMATIONS 3: DEDUPLICATE NPIS
    df_clinician_mart = transform_dedup(df_clinician_mart, ['NPI'])

    # TODO PARAMETERIZE TARGETS
    df_clinician_mart.to_csv('./data/silver/clinician_mart_latest.csv', index=False)
    df_clinician_mart.to_csv(f'./data/silver/clinician_mart_{get_curr_ts_epoch_sec()}', index=False)

    print(f"Done. Wrote {df_clinician_mart.shape[0]} rows to target")
