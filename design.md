# Backend Design

- Flask
- MariaDB

3 endpoints:
- `POST /login`
- `POST /start`
- `POST /update`

---

# Endpoints

## 1) `POST /login`

### Input
- `username`

### What it does
- finds player by username
- if player does not exist, creates a new player
- returns current player progress
- returns current route
- returns opened airports

### Request example

    {
      "username": "aleksei"
    }

### Response example

    {
      "player_id": 1,
      "username": "aleksei",
      "progress_index": 2,
      "completed": false,
      "route": [
        "EFHK",
        "EETN",
        "EDDB",
        "EHAM",
        "LEZG"
      ],
      "opened_airports": [
        "EFHK",
        "EETN"
      ]
    }

### New player response example

    {
      "player_id": 2,
      "username": "newplayer",
      "progress_index": 0,
      "completed": false,
      "route": [],
      "opened_airports": []
    }

---

## 2) `POST /start`

### Input
- `username`

### What it does
- finds player
- clears old current game data
- picks 5 random airports from `airports`
- saves them as the player's new current route
- clears opened airports
- resets progress to `0`
- sets `completed = false`
- returns the selected route

### Request example

    {
      "username": "aleksei"
    }

### Response example

    {
      "route": [
        {
          "order_index": 1,
          "icao_code": "EFHK",
          "name": "Helsinki Airport",
          "country_code": "FI"
        },
        {
          "order_index": 2,
          "icao_code": "EETN",
          "name": "Tallinn Airport",
          "country_code": "EE"
        },
        {
          "order_index": 3,
          "icao_code": "EDDB",
          "name": "Berlin Brandenburg Airport",
          "country_code": "DE"
        },
        {
          "order_index": 4,
          "icao_code": "EHAM",
          "name": "Amsterdam Airport Schiphol",
          "country_code": "NL"
        },
        {
          "order_index": 5,
          "icao_code": "LEZG",
          "name": "Zaragoza Airport",
          "country_code": "ES"
        }
      ],
      "progress_index": 0,
      "completed": false
    }

### DB actions performed by `/start`

    DELETE FROM player_opened_airports WHERE player_id = ?;
    DELETE FROM player_route_airports WHERE player_id = ?;

    UPDATE players
    SET progress_index = 0,
        completed = FALSE
    WHERE id = ?;

Then insert 5 newly selected route airports into `player_route_airports`.

---

## 3) `POST /update`

### Input
- `username`
- `icao_code`

### What it does
- finds player
- verifies airport is in player's current route
- verifies airport is not already opened
- adds airport to opened airports
- increments progress
- if progress becomes `5`, sets `completed = true`
- returns updated state

### Request example

    {
      "username": "aleksei",
      "icao_code": "EDDB"
    }

### Response example

    {
      "success": true,
      "progress_index": 3,
      "completed": false,
      "opened_airports": [
        "EFHK",
        "EETN",
        "EDDB"
      ]
    }

### Final airport response example

    {
      "success": true,
      "progress_index": 5,
      "completed": true,
      "opened_airports": [
        "EFHK",
        "EETN",
        "EDDB",
        "EHAM",
        "LEZG"
      ]
    }

### Error example

    {
      "success": false,
      "error": "Airport already opened"
    }

### Another error example

    {
      "success": false,
      "error": "Airport is not in current route"
    }

---

# Database Schema

## 1) `countries`

    CREATE TABLE countries (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        code CHAR(2) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL
    );

---

## 2) `airports`

    CREATE TABLE airports (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        icao_code CHAR(4) NOT NULL UNIQUE,
        name VARCHAR(150) NOT NULL,
        country_id BIGINT NOT NULL,
        latitude DECIMAL(9,6) NULL,
        longitude DECIMAL(9,6) NULL,
        FOREIGN KEY (country_id) REFERENCES countries(id)
    );

---

## 3) `players`

    CREATE TABLE players (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        progress_index INT NOT NULL DEFAULT 0,
        completed BOOLEAN NOT NULL DEFAULT FALSE,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

---

## 4) `player_route_airports`

Stores the player's current 5-airport route.

    CREATE TABLE player_route_airports (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        player_id BIGINT NOT NULL,
        airport_id BIGINT NOT NULL,
        order_index INT NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (airport_id) REFERENCES airports(id),
        UNIQUE (player_id, order_index),
        UNIQUE (player_id, airport_id)
    );

---

## 5) `player_opened_airports`

Stores which airports from the current route were already opened.

    CREATE TABLE player_opened_airports (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        player_id BIGINT NOT NULL,
        airport_id BIGINT NOT NULL,
        opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (airport_id) REFERENCES airports(id),
        UNIQUE (player_id, airport_id)
    );

---

# How Data Works

## `players`
Stores:
- player identity
- current progress index
- completed flag

## `player_route_airports`
Stores:
- the 5 airports selected by `/start`
- the order in which they belong to the player's current route

## `player_opened_airports`
Stores:
- which route airports the player has already reached/opened

---

# `/start` Flow

1. Find player by username
2. Delete rows from `player_opened_airports`
3. Delete rows from `player_route_airports`
4. Reset `players.progress_index = 0`
5. Reset `players.completed = false`
6. Select 5 random airports
7. Insert them into `player_route_airports` with `order_index` values `1..5`
8. Return route to client

---

# `/update` Flow

1. Find player by username
2. Find airport by `icao_code`
3. Verify airport exists in `player_route_airports` for that player
4. Verify airport does not already exist in `player_opened_airports`
5. Insert airport into `player_opened_airports`
6. Increment `players.progress_index`
7. If `progress_index = 5`, set `completed = true`
8. Return updated data

---

# Final Prototype Structure

## Endpoints
- `POST /login`
- `POST /start`
- `POST /update`

## Tables
- `countries`
- `airports`
- `players`
- `player_route_airports`
- `player_opened_airports`