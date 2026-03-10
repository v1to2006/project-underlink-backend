from flask import Flask, jsonify, request

from app.db import get_cursor

app = Flask(__name__)


def normalize_username(value: str | None) -> str:
    return (value or "").strip().lower()


def bad_request(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def get_or_create_player(username: str):
    with get_cursor() as (_, cursor):
        cursor.execute(
            "SELECT id, username, progress_index, completed FROM players WHERE username = %s",
            (username,),
        )
        player = cursor.fetchone()

        if player:
            return player

        cursor.execute("INSERT INTO players (username) VALUES (%s)", (username,))
        player_id = cursor.lastrowid

        return {
            "id": player_id,
            "username": username,
            "progress_index": 0,
            "completed": 0,
        }


def fetch_route_and_opened(cursor, player_id: int):
    cursor.execute(
        """
        SELECT pra.order_index, a.ident AS icao_code
        FROM player_route_airports pra
        JOIN airport a ON a.ident = pra.airport_ident
        WHERE pra.player_id = %s
        ORDER BY pra.order_index ASC
        """,
        (player_id,),
    )
    route_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT a.ident AS icao_code
        FROM player_opened_airports poa
        JOIN airport a ON a.ident = poa.airport_ident
        WHERE poa.player_id = %s
        ORDER BY poa.opened_at ASC, poa.id ASC
        """,
        (player_id,),
    )
    opened_rows = cursor.fetchall()

    return route_rows, [row["icao_code"] for row in opened_rows]


@app.get("/")
def home():
    return "deep drift backend running"


@app.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = normalize_username(payload.get("username"))

    if not username:
        return bad_request("username is required")

    player = get_or_create_player(username)

    with get_cursor() as (_, cursor):
        route_rows, opened_airports = fetch_route_and_opened(cursor, player["id"])

    return jsonify(
        {
            "player_id": player["id"],
            "username": player["username"],
            "progress_index": int(player["progress_index"]),
            "completed": bool(player["completed"]),
            "route": [row["icao_code"] for row in route_rows],
            "opened_airports": opened_airports,
        }
    )


@app.post("/start")
def start():
    payload = request.get_json(silent=True) or {}
    username = normalize_username(payload.get("username"))

    if not username:
        return bad_request("username is required")

    player = get_or_create_player(username)

    with get_cursor() as (_, cursor):
        cursor.execute(
            "DELETE FROM player_opened_airports WHERE player_id = %s",
            (player["id"],),
        )
        cursor.execute(
            "DELETE FROM player_route_airports WHERE player_id = %s",
            (player["id"],),
        )
        cursor.execute(
            "UPDATE players SET progress_index = 0, completed = FALSE WHERE id = %s",
            (player["id"],),
        )

        cursor.execute(
            """
            SELECT
                a.ident AS icao_code,
                a.name,
                a.iso_country AS country_code
            FROM airport a
            WHERE a.type IN ('small_airport', 'medium_airport', 'large_airport')
            ORDER BY RAND()
            LIMIT 5
            """
        )
        selected_airports = cursor.fetchall()

        if len(selected_airports) < 5:
            return bad_request("not enough airports in database", 500)

        for index, airport in enumerate(selected_airports, start=1):
            cursor.execute(
                """
                INSERT INTO player_route_airports (player_id, airport_ident, order_index)
                VALUES (%s, %s, %s)
                """,
                (player["id"], airport["icao_code"], index),
            )

    return jsonify(
        {
            "route": [
                {
                    "order_index": index,
                    "icao_code": airport["icao_code"],
                    "name": airport["name"],
                    "country_code": airport["country_code"],
                }
                for index, airport in enumerate(selected_airports, start=1)
            ],
            "progress_index": 0,
            "completed": False,
        }
    )


@app.post("/update")
def update():
    payload = request.get_json(silent=True) or {}
    username = normalize_username(payload.get("username"))
    icao_code = (payload.get("icao_code") or "").strip().upper()

    if not username:
        return bad_request("username is required")

    if not icao_code:
        return bad_request("icao_code is required")

    player = get_or_create_player(username)

    with get_cursor() as (_, cursor):
        cursor.execute(
            """
            SELECT airport_ident
            FROM player_route_airports
            WHERE player_id = %s AND airport_ident = %s
            """,
            (player["id"], icao_code),
        )
        route_match = cursor.fetchone()

        if not route_match:
            return bad_request("Airport is not in current route")

        cursor.execute(
            """
            SELECT id
            FROM player_opened_airports
            WHERE player_id = %s AND airport_ident = %s
            """,
            (player["id"], icao_code),
        )
        already_opened = cursor.fetchone()

        if already_opened:
            return bad_request("Airport already opened")

        cursor.execute(
            """
            INSERT INTO player_opened_airports (player_id, airport_ident)
            VALUES (%s, %s)
            """,
            (player["id"], icao_code),
        )

        cursor.execute(
            "UPDATE players SET progress_index = progress_index + 1 WHERE id = %s",
            (player["id"],),
        )
        cursor.execute(
            "SELECT progress_index FROM players WHERE id = %s",
            (player["id"],),
        )

        row = cursor.fetchone()
        if row is None:
            return bad_request("Player not found", 404)

        progress_index = int(row["progress_index"])
        completed = progress_index >= 5

        if completed:
            cursor.execute(
                "UPDATE players SET completed = TRUE WHERE id = %s",
                (player["id"],),
            )

        cursor.execute(
            """
            SELECT a.ident AS icao_code
            FROM player_opened_airports poa
            JOIN airport a ON a.ident = poa.airport_ident
            WHERE poa.player_id = %s
            ORDER BY poa.opened_at ASC, poa.id ASC
            """,
            (player["id"],),
        )
        opened_airports = [row["icao_code"] for row in cursor.fetchall()]

    return jsonify(
        {
            "success": True,
            "progress_index": progress_index,
            "completed": completed,
            "opened_airports": opened_airports,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)