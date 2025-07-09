# Data Collections Documentation

## Purpose

This directory of the project focuses on how data is collected and managed. Data is extracted from various sources using automated scripts via our YAML GitHub Workflows. Once gathered, the data is formatted and stored in `runningCSV.csv`, making it easy for our data-processing subteam to use.

In this document, you will learn how our data is stored after being extracted from these various sources. This document is mainly for our data-processing subteam to understand our storage containers.

## `runningCSV.csv` Format

Below is how the `runningCSV.csv` file is formatted

| Column | Meaning |
| --- | --- |
| **Type** | Indicator to **separate** the type of career-development item — `Event`, `Job`, or `Internship`. |
| **Title** | Title of the event, job, or internship. |
| **Description** | Description of the item. |
| **whenDate** | event date or application deadline. |
| **pubDate** | original publication date on the source site. |
| **entryDate** | date the item was ingested into the system. |