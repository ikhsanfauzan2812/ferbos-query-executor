# Ferbos Query Executor

A Home Assistant custom integration that provides SQLite database querying capabilities through WebSocket API.

## Features

- Execute SQLite queries against Home Assistant's database (`home-assistant_v2.db`)
- Support for both SELECT and non-SELECT queries
- WebSocket API endpoint: `ferbos/query`
- Secure local database access within Home Assistant Core

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/ikhsanfauzan2812/ferbos-query-executor`
5. Select "Integration" as the category
6. Click "Add"
7. Find "Ferbos Query Executor" in the integration list and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/ferbos_query_executor` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Ferbos Query Executor"
4. Click to add the integration

## Usage

### WebSocket API

Connect to Home Assistant's WebSocket API and send queries:

```json
{
  "id": 1,
  "type": "ferbos/query",
  "args": {
    "query": "SELECT * FROM states WHERE entity_id LIKE ? LIMIT 10",
    "params": ["sensor.%"]
  }
}
```

### Response Format

**SELECT queries:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "success": true,
    "data": [
      {"entity_id": "sensor.temperature", "state": "23.5", ...},
      ...
    ]
  }
}
```

**Non-SELECT queries:**
```json
{
  "id": 1,
  "type": "result", 
  "success": true,
  "result": {
    "success": true,
    "data": {
      "rowcount": 1,
      "lastrowid": 12345
    }
  }
}
```

## Security

- Only local database access (no remote connections)
- Runs within Home Assistant Core process
- No external network dependencies
- Parameterized queries supported to prevent SQL injection

## License

MIT License
