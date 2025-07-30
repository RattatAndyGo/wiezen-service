# see https://github.com/mu-semtech/mu-python-template for more info

@app.route("/search/<playername>", methods=["GET"])
def search(playername):
    return "Searched for {}".format(playername)