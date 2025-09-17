# API Reference

## POST `/register`
Registers new miner

Header requirements:
- api_key (str) -- API key

Request body:
```json
{
  "tag": "miner_tag",
  "name": "miner_name",
  "model": "miner_model"
}
```

Response:
```json
{
  "message": "Registered successfully"
}
```

## POST `/record`
Add new metrics record for miner

Header requirements:
- api_key (str) -- API key

Request:
```json
{
  "tag": "miner_tag",
  "hashrate": 15.15,
  "power": 23.23,
  "voltage": 202.2,
  "time": "2025-09-17T12:34:56"
}
```

Response:
```json
{
  "message": "Recorded successfully"
}
```

## GET `/devices`
Returns list of all registered miners

Header requirements:
- api_key (str) -- API key

Response:
```json
[
  {
    "tag": "miner_tag",
    "name": "miner_name",
    "model": "miner_model",
    "is_active": true
  },
  {
    "tag": "miner_tag2",
    "name": "miner_name2",
    "model": "miner_model2",
    "is_active": false
  },
  ...
]
```

## GET `/{tag}/metrics`
Returns the last metrics of the miner if it is active.

Header requirements:
- api_key (str) -- API key
- tag (str) -- miner tag

Response if the miner is **inactive**:
```json
{
  "tag": "miner_tag",
  "active": false,
  "message": "The miner is inactive"
}
```

Response if the miner is **active**:
```json
{
  "tag": "miner-001",
  "active": true,
  "hashrate": 1050,
  "power": 1200,
  "voltage": 12,
  "time": "2025-09-17T12:34:56"
}
```

## GET `/{tag}/history`
Returns the last N hours (and M points) parameter changes of the miner.

Header requirements:
- api_key (str) -- API key
- tag (str) -- miner tag
- param (str) -- parameter to track (hashrate, voltage, etc.)
- last_hours (int) -- period of metric history in hours. Optional argument, 24 set by default
- points (int) -- how much points to get. Optional argument, 500 set by default

Response:
```json
{
  "tag": "miner_tag",
  "active": true,
  "param": "hashrate",
  "last_hours": 24,
  "points": 5,
  "data": [
    {
      "time": "2025-09-17T10:00:00",
      "value": 1000
    },
    ...
  ]
}
```
