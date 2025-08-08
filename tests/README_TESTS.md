# Events Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the `getEvents` function in `data_collections/events.py`.

## Test Structure

### Main Test Classes

1. **TestGetEvents**: Core functionality tests
   - Basic RSS feed parsing
   - Error handling for malformed feeds
   - Field extraction (When, Location, and Description)
   - Data type handling

2. **TestGetEventsRegexPatterns**: Regex-specific tests
   - Title parentheses removal patterns
   - Description field cleaning
   - Case-insensitive matching

3. **TestGetEventsErrorHandling**: Exception handling tests
   - Network errors
   - Parsing errors
   - Malformed data handling

4. **TestGetEventsDataTypes**: Data type validation
   - Integer, boolean, list, and dict values in fields
   - Type conversion handling

5. **TestGetEventsIntegrationScenarios**: Real-world scenarios
   - Complex RSS feed structures
   - Multiple feed processing
   - Batch operations

6. **TestGetEventsEdgeCases**: Edge case coverage
   - Multiline values
   - Special characters
   - Performance with large datasets
   - Duplicate fields

## Running Tests

### Run all tests

```bash
python -m unittest tests.events_test
```

### Run specific test class

```bash
python -m unittest tests.events_test.TestGetEvents
```

### Run with verbose output

```bash
python -m unittest tests.events_test -v
```

### Run with coverage

```bash
coverage run -m unittest tests.events_test
coverage report
coverage html
```

## Test Coverage Areas

- **Input Validation**: Empty URLs, None values, invalid formats
- **RSS Parsing**: Valid feeds, malformed XML, bozo feeds
- **Field Extraction**: When/Location parsing, description cleaning
- **Data Types**: Strings, integers, lists, dicts in various fields
- **Edge Cases**: Unicode, HTML entities, very long text
- **Error Handling**: Network errors, parsing errors, exceptions
- **Performance**: Large feeds, concurrent processing

## Mock Strategy

The tests use `unittest.mock.patch` to mock the `feedparser.parse` function, allowing controlled testing of various scenarios without actual network calls.

## Test Data

- `sample_return`: Basic valid RSS feed structure
- Various inline test data for specific scenarios
- Edge cases with special characters, Unicode, and HTML entities

## Notes

- Tests are isolated and don't require network access
- Each test method is independent and can run in any order
- Mocking ensures consistent, reproducible results
- Performance tests validate processing efficiency.