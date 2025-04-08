# Link Building Categorization Tool

An automated tool that uses GPT-4 to categorize link building prospects in SEMrush's Link Building Tool. The script automatically processes prospects and assigns them to appropriate outreach strategy categories.

## Features

- Automated login to SEMrush
- Processes link building prospects one by one
- Uses GPT-4 to analyze and categorize prospects based on:
  - Domain
  - URL
  - Page snippet
  - Page type
- Automatically assigns prospects to categories:
  - Manual link
  - Directory/Catalogue
  - Add link to article
  - Product review
  - Link from mention
  - Guest post
  - Recover lost backlinks
- Detailed logging of all operations

## Prerequisites

- Python 3.6+
- Chrome browser
- ChromeDriver
- SEMrush account
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tomozilla/link-building-categorization.git
cd link-building-categorization
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Then edit `.env` with your credentials:
- OPENAI_API_KEY
- SEMRUSH_EMAIL
- SEMRUSH_PASSWORD
- LINK_BUILDING_TOOL_URL

## Usage

Run the script:
```bash
python categorize_list.py
```

The script will:
1. Log in to SEMrush
2. Navigate to your Link Building Tool project
3. Process each prospect automatically
4. Log all operations to a dated log file

## Logging

The script creates detailed logs in `semrush_processing_YYYYMMDD.log` with:
- Domain information
- GPT analysis
- Selected strategies
- Any errors or issues

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
