# AI meeting minutes automation


## Overview

In order to realize the automation of meeting records, this project will hand over the recorded audio files to AI technology to automatically transcribe verbatim manuscripts and generate reports such as analysis and key arrangement. In order to free up the time and energy spent by manpower on meeting minutes.

## Project Structure

```
.
├── README.md
├── main.py
├── requirements.txt
├── src
│   ├── auto_summarize.py
│   └── speech_to_text.py
└── test
```

## Quick Start

### 1. Clone project

```bash
git clone ssh://git@biglab.buygta.today:8931/bigdata/ai-meeting-project.git
```

### 2. Setting .env with .env.example


### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. Launch it (Not yet under development)

```bash
python main.py
```

## Features

### 1. Speech to text:

Input audio files (mp3, m4a, wav) will be automatically converted to verbatim.

### 2. Generate focused reports

Analyze and generate key points of meeting minutes based on verbatim transcripts of meeting minutes.

### 3. Generate todo list

Analyze and generate meeting to-do items from verbatim transcripts of meeting minutes.

### 4. Give smart suggestions

Give smart suggestions based on to-do items.