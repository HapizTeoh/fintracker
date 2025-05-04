# Welcome to Fintracker

## Description
A personal finance tracker that allows users to manage expenses. Built on Python and Streamlit

### Data
Data is using personal collected data stored in a CSV file. 
The csv file should be name in the following format
```
data/budget-YYYY.csv
```

### To run
```
# Install dependencies
pip3 install -r requirements.txt

# Set up csv file
For now, rename your test file to the filename below
data/budget-2024.csv

# Run the app
streamlit run visualize/About.py
```

## Development

### Best practices

1. Do not merge to main directly
2. Branch naming convention

    | Type        | Purpose                                     | Example                          |
    |-------------|---------------------------------------------|----------------------------------|
    | `feature/`  | New feature or enhancement                  | `feature/add-login-page`         |
    | `bugfix/`   | Fixing a bug                                | `bugfix/fix-header-overlap`      |
    | `hotfix/`   | Urgent fix on production                    | `hotfix/payment-crash`           |
    | `chore/`    | Minor task (e.g. updating deps, config)     | `chore/update-packages`          |
    | `refactor/` | Code refactoring without feature change     | `refactor/simplify-auth-flow`    |
    | `docs/`     | Documentation updates                       | `docs/add-api-usage`             |
    | `test/`     | Test-related work                           | `test/add-login-tests`           |
    | `release/`  | Preparing or tagging a new release version  | `release/v1.2.0`                  |
