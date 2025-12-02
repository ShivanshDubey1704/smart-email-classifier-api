# 📧 Smart Email Classifier API

ML-powered email classification API that automatically categorizes emails into spam, important, promotional, social, and general categories with intelligent priority scoring.

## Features

- **Multi-Category Classification**: Spam, Important, Promotional, Social, General
- **Priority Scoring**: 1-10 scale for email importance
- **Confidence Metrics**: Classification confidence percentage
- **Batch Processing**: Classify multiple emails simultaneously
- **Feature Detection**: Identifies suspicious patterns and links
- **Action Recommendations**: Suggests folder placement and actions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

## API Endpoints

### POST /classify
Classify a single email

**Request:**
```json
{
  "subject": "Meeting Tomorrow at 3 PM",
  "body": "Hi, just confirming our meeting scheduled for tomorrow...",
  "sender": "john@company.com"
}
```

**Response:**
```json
{
  "email_id": "a3f5d8c9b2e1",
  "category": "important",
  "confidence": 85.5,
  "priority": 9,
  "scores": {
    "spam": 0,
    "promotional": 0,
    "important": 2,
    "social": 0
  },
  "recommendation": "Flag for immediate attention",
  "timestamp": "2025-12-02T18:30:00"
}
```

### POST /batch-classify
Classify multiple emails at once

**Request:**
```json
{
  "emails": [
    {"subject": "...", "body": "...", "sender": "..."},
    {"subject": "...", "body": "...", "sender": "..."}
  ]
}
```

## Categories

- **Spam**: Suspicious, phishing, or unwanted emails
- **Important**: Urgent business, financial, or time-sensitive emails
- **Promotional**: Marketing, sales, and promotional content
- **Social**: Social media notifications and updates
- **General**: Regular correspondence

## Tech Stack

- Flask
- Python 3.8+
- Machine Learning (Pattern Recognition)

## Author

Shivansh Dubey
