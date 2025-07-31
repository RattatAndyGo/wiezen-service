from flask import jsonify, request
from helpers import generate_uuid, update
from helpers import generate_uuid, update, query
from escape_helpers import sparql_escape_uri, sparql_escape_string
from string import Template


@app.route("/search/<playername>", methods=["GET"])
def search(playername):
    result = {}

    # Get all rounds the player participated in
    round_query = query(Template("""
        PREFIX schema: <http://schema.org/>
        SELECT DISTINCT ?round WHERE { 
            ?namedPlayer schema:givenName $name.
            ?namedPos schema:competitor ?namedPlayer.
            ?round schema:event ?namedPos.
        } LIMIT 100
    """).substitute(name=sparql_escape_string(playername)))

    rounds = []

    for roundbinding in round_query["results"]["bindings"]:
        round = {}
        round_uri = roundbinding["round"]["value"]

        # Get all the players from the specific round
        player_query = query(Template("""
            PREFIX schema: <http://schema.org/>
            PREFIX ext: <http://example.com/>
            SELECT DISTINCT ?name WHERE { 
                $round schema:event ?pos.
                ?pos schema:competitor ?player.
                ?player schema:givenName ?name.
                ?pos ext:value ?index.
            } ORDER BY ?index
        """).substitute(round=sparql_escape_uri(round_uri)))
        playernames = [playerbinding["name"]["value"] for playerbinding in player_query["results"]["bindings"]]
        round["players"] = playernames

        # Get all the hands from the specific route
        hand_query = query(Template("""
            PREFIX schema: <http://schema.org/>
            PREFIX ext: <http://example.com/>
            SELECT DISTINCT ?hand ?contract ?dealerName WHERE { 
                ?hand schema:superEvent $round.
                ?hand schema:description ?contract.
                ?hand ext:index ?index.
                ?hand schema:referee ?dealer.
                ?dealer schema:givenName ?dealerName.
            } ORDER BY ?index
        """).substitute(round=sparql_escape_uri(round_uri)))

        # List for calculation cumulative scores
        points_total = [0 for _ in range(4)]
        games = []

        for handbinding in hand_query["results"]["bindings"]:
            game = {}
            hand_uri = handbinding["hand"]["value"]

            # Get the scores from the specific hand
            point_query = query(Template("""
                PREFIX ext: <http://example.com/>
                SELECT DISTINCT ?point ?score WHERE { 
                    $hand ext:gameScore ?point.
                    ?point ext:value ?score.
                    ?point ext:winner ?position.
                    ?position ext:value ?index.
                } ORDER BY ?index
            """).substitute(hand=sparql_escape_uri(hand_uri)))

            points_earned = [int(pointbinding["score"]["value"]) for pointbinding in point_query["results"]["bindings"]]
            points_total = [points_earned[i] + points_total[i] for i in range(4)]

            active_players_query = query(Template("""
                PREFIX schema: <http://schema.org/>
                SELECT DISTINCT ?name WHERE { 
                    $hand schema:homeTeam ?player.
                    ?player schema:givenName ?name.
                }
            """).substitute(hand=sparql_escape_uri(hand_uri)))

            active_playernames = [playerbinding["name"]["value"] for playerbinding in active_players_query["results"]["bindings"]]
            active_players = [playername for playername in playernames if playername in active_playernames]             

            game = {
                "dealer": handbinding["dealerName"]["value"],
                "contract": handbinding["contract"]["value"],
                "activePlayers": active_players,
                "pointsEarned": points_earned,
                "pointsTotal": points_total
            }

            games.append(game)
        round["games"] = games
        rounds.append(round)
    result["rounds"] = rounds
    
    return jsonify(result)