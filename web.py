from flask import jsonify, request
from helpers import generate_uuid, update
from helpers import generate_uuid, update, query
from escape_helpers import sparql_escape_uri, sparql_escape_string
from string import Template


@app.route("/search/<playername>", methods=["GET"])
def search(playername):
    result = query(Template("""
        PREFIX schema: <http://schema.org/>
        PREFIX ext: <http://example.com/>
        SELECT * WHERE { 
            ?namedPlayer schema:givenName $name.
            ?namedPos schema:competitor ?namedPlayer.
            ?round schema:event ?namedPos.
            ?hand schema:superEvent ?round.
            ?hand schema:description ?contract.
            ?hand ext:index ?index.
            ?hand schema:referee ?dealer.
            ?dealer schema:givenName ?dealerName.
            ?hand ext:gameScore ?point.
            ?point ext:value ?score.
            ?point ext:winner ?winner.
            ?winner schema:competitor ?player.
            ?player schema:givenName ?name.
        } LIMIT 100
    """).substitute(name=sparql_escape_string(playername)))

    # return result

    return """[
            {
                "dealer":"A",
                "contract":"Vraag mee",
                "activePlayers":[true, true, false, true],
                "pointsEarned":["2","2","-2","-2"],
                "pointsTotal":["2","2","-2","-2"]
            },
            {
                "dealer":"B",
                "contract":"Abondance 9",
                "activePlayers":[true, true, false, false],
                "pointsEarned":["-5","-5","15","-5"],
                "pointsTotal":[-3,-3,13,-7]
            },
            {
                "dealer":"C",
                "contract":"Alleen",
                "activePlayers":[true, true, false, false],
                "pointsEarned":["-12","4","4","4"],
                "pointsTotal":[-15,1,17,-3]
            }
        ]"""