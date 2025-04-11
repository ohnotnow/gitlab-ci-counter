# GitLab CI Minutes Usage Calculator

This Python script calculates the GitLab CI minutes used by selected projects within a specified timeframe. It is designed to work with self-hosted or private GitLab instances using the GitLab API.

## Features

- Supports specifying multiple group and project IDs
- Fetches pipelines and jobs updated within a given timeframe (default: past 30 days)
- Outputs CI minutes used per project and the overall total

## Requirements

- Python 3.8+
- A personal access token for the GitLab instance with API access permissions
- The [`uv`](https://docs.astral.sh/uv/) tool for managing dependencies and running the script

## Installation

1. Clone the repository:

   ```bash
   git clone <REPO_URL>
   cd <REPO_NAME>
   ```

2. Install dependencies using [`uv`](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

## Configuration

Set the following environment variables before running the script:

- `GITLAB_URL` — Base URL of your GitLab instance (e.g. `https://gitlab.example.com`)
- `GITLAB_TOKEN` — Your GitLab personal access token

You can export them in your shell or use a `.env` manager:

```bash
export GITLAB_URL=https://gitlab.example.com
export GITLAB_TOKEN=your_personal_access_token
```

Group and project IDs can be hardcoded in the script or passed as parameters by modifying the `main()` call or extending argument parsing.

## Usage

To run the script with default options:

```bash
uv run main.py
```

To specify a different number of days (e.g., past 60 days):

```bash
uv run main.py --days 60
```

### Output

The script prints:
- Number of discovered projects
- A line-by-line breakdown of each project and its CI minutes
- A CSV-style summary with project ID, name, and CI minutes used

## Notes

- If no `GROUP_IDS` or `PROJECT_IDS` are specified in the script, the script fetches all accessible projects.
- Only successful jobs with a recorded duration are counted.

## License

This project is licensed under the MIT License.
