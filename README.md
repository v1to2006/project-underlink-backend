# Project UNDERLINK Backend

Backend service for the Project UNDERLINK / DEEP DRIFT game client.

It provides:

* player login and save loading
* new expedition generation
* airport progression updates
* airport detail lookup by ICAO code

The Godot client connects to this backend over HTTP and uses it to store expedition progress between sessions.

## Related Documentation

See [design.md](design.md).

That file contains the backend design overview, including:

* the Flask + MariaDB stack
* what each endpoint does
* request and response examples
* how player progression is stored
* how route generation works
* how `/start` resets expedition state
* how `/update` advances airport progress
* the database schema for players and route tracking
* the overall structure

If you want to understand how the backend is supposed to work before editing code, start there.

## How to Start

### 1. Start Database

Run this in the project root:

```bash
docker compose up -d
```

This starts the MariaDB container and initializes the database from the SQL files in `db/init`.

### 2. Install Backend Dependencies

Run this in the `backend` folder:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Flask App

Run this in the `backend` folder:

```bash
python -m flask --app app.main run
```

### 4. Backend URL

```text
http://127.0.0.1:5000
```

## Main Endpoints

### `POST /login`

Loads a player by username.
If the player does not exist yet, creates a new one.
Returns the current expedition state, including route, opened airports, progress index, and completion state.

### `POST /start`

Starts a fresh expedition for the current player.
Clears previous route progress, resets expedition state, selects 5 airports, and returns the new route.

### `POST /update`

Marks an airport as completed for the current player.
Validates that the airport belongs to the player’s route, updates progress, and marks the expedition completed when the final airport is reached.

### `GET /airport?icao_code=XXXX`

Returns detailed airport information for a specific ICAO code.
This is used by the Godot client to display airport details in the in-game terminal.

## Database Overview

The backend uses MariaDB and stores expedition state in dedicated player progress tables.

Main gameplay-related tables:

* `players`
* `player_route_airports`
* `player_opened_airports`

Reference data tables include:

* `country` / `countries`
* `airport` / `airports`

The exact schema and flow notes are documented in [design.md](design.md).

## Notes

* The database runs in Docker.
* The Flask backend is started manually.
* If you change SQL init files and want a full clean re-init, remove the database volume and recreate the container.
* This backend is meant to be used together with the Godot client repository.
