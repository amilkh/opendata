# merged_survey_csv_py

Python script to standardize and merge survey CSV data from Toyama, Ishikawa, and Fukui prefectures

## Overview

This project is a tool for converting survey data collected from three prefectures (Toyama, Ishikawa, and Fukui) into a unified format and merging them into CSV files.

### Key Features

- **Data Standardization**: Convert CSV data in different formats from each prefecture to a unified format
- **Column Mapping**: Column name mapping using JSON files
- **Data Preprocessing**: Normalizing line codes, anonymizing member IDs, standardizing date formats
- **Information Source Flag Generation**: Automatically generate flags for various media and channels from information source data
- **CSV Merging**: Consolidate converted data into a single file
- **Automatic Data Download**: Automatically retrieve the latest data from GitHub repositories and public data sources
- **File Splitting by Year**: Split output files by year
- **Automatic Cleanup**: Automatically delete old output files before processing

## File Structure

```
merged_survey_csv_py/
├── download_data.py           # Data download script
├── convert_toyama.py          # Toyama prefecture data conversion script
├── convert_ishikawa.py        # Ishikawa prefecture data conversion script
├── convert_fukui.py           # Fukui prefecture data conversion script
├── merge_survey.py            # Main execution script (download + convert + merge)
├── .github/
│   └── workflows/
│       └── run_python.yml     # GitHub Actions automation settings
├── input/                     # Input data
│   ├── toyama/
│   │   ├── toyama.csv                    # Toyama survey data (auto-downloaded)
│   │   └── column_mapping_toyama.json    # Toyama column mapping definition
│   ├── ishikawa/
│   │   ├── ishikawa.csv                  # Ishikawa survey data (auto-downloaded)
│   │   └── column_mapping_ishikawa.json  # Ishikawa column mapping definition
│   └── fukui/
│       ├── fukui.csv                     # Fukui survey data (merged after auto-download)
│       ├── fukui_2023.csv                # Fukui 2023 data (auto-downloaded)
│       ├── fukui_2024.csv                # Fukui 2024 data (auto-downloaded)
│       └── column_mapping_fukui.json     # Fukui column mapping definition
├── output/                    # Converted data
│   ├── toyama/
│   │   ├── toyama_converted.csv          # Converted data (not pushed to GitHub)
│   │   ├── toyama_converted_2023.csv     # 2023 split data
│   │   ├── toyama_converted_2024.csv     # 2024 split data
│   │   └── ...
│   ├── ishikawa/
│   │   ├── ishikawa_converted.csv        # Converted data (not pushed to GitHub)
│   │   ├── ishikawa_converted_2023.csv   # 2023 split data
│   │   ├── ishikawa_converted_2024.csv   # 2024 split data
│   │   └── ...
│   └── fukui/
│       ├── fukui_converted.csv           # Converted data (not pushed to GitHub)
│       ├── fukui_converted_2023.csv      # 2023 split data
│       ├── fukui_converted_2024.csv      # 2024 split data
│       └── ...
└── output_merge/              # Merged data
    ├── merged_survey.csv      # Final output file (not pushed to GitHub)
    ├── merged_survey_2023.csv # 2023 split data
    ├── merged_survey_2024.csv # 2024 split data
    └── ...
```

For detailed execution instructions and data conversion details, please refer to the [Developer Documentation](docs/development.md).

## Automatic Execution (GitHub Actions)

This project automatically updates data daily using GitHub Actions.

### Execution Schedule

- **Execution Time**: 6:00 AM every day (Japan Standard Time)
- **Execution Content**:
  1. Download latest data
  2. Data conversion and merging
  3. File splitting by year
  4. Automatic push to GitHub

### Files Pushed to GitHub

Only the following files are pushed to GitHub:

- Year-split merged files: `output_merge/merged_survey_*.csv`
- Year-split converted files: `output/*/*_converted_*.csv`
- Input data: `input/toyama/toyama.csv`, `input/ishikawa/ishikawa.csv`, `input/fukui/fukui_*.csv`

The following files are not pushed due to `.gitignore` (may exceed 50MB):

- `output_merge/merged_survey.csv`
- `output/toyama/toyama_converted.csv`
- `output/ishikawa/ishikawa_converted.csv`
- `output/fukui/fukui_converted.csv`
- `input/fukui/fukui.csv`

## Notes

- Input CSV files must be in UTF-8 encoding
- Column mapping JSON files must be in valid JSON format
- Output directories are created automatically
- If an error occurs, detailed error messages will be displayed in the console

## License

- [CC-BY (Attribution)](https://creativecommons.org/licenses/by/4.0/) Hokuriku Inbound Tourism DX and Data Consortium

- Anyone is free to use this data as long as you provide attribution to the source.

## Attribution

(This tourism survey data aggregation program is a modified version of the following works.)

- For Toyama Prefecture data: [Toyama Prefecture Data Collaboration Platform CKAN Toyama Prefecture Tourism Web Survey Data](https://ckan.tdcp.pref.toyama.jp/dataset/kanko_data), Toyama Prefecture, [CC-BY (Attribution)](https://opendefinition.org/licenses/cc-by/)

- For Ishikawa Prefecture data: [Ishikawa Tourism QR Survey Data - Aggregated Data - Tabular Data - All Areas](https://sites.google.com/view/milli-ishikawa-pref/data), Ishikawa Prefecture, [CC-BY (Attribution) 2.1](http://creativecommons.org/licenses/by/2.1/jp/)

- For Fukui Prefecture data: [Open data published by Fukui Prefecture Tourism Data System "FTAS"](https://github.com/code4fukui/fukui-kanko-survey), Fukui Tourist Association, [CC-BY (Attribution)](https://creativecommons.org/licenses/by/4.0/)
