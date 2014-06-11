import logging, requests, json

from flask import Flask, render_template, request, redirect, url_for, jsonify

import acs.db, acs.data, worldcup.fixtures, util.geo

app = Flask(__name__)

# setup logging
logging.basicConfig(filename='world-cup.log',level=logging.DEBUG)
logger = logging.getLogger('world-cup-server')
logger.info("---------------------------------------------------------------------------")

# connect to database
db = acs.db.CensusDataManager('sqlite:///acs.db')
logger.info("Connected to db")

picker = worldcup.fixtures.Picker()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/select-zipcode")
def select_zip_code():
    return render_template('select-zip-code.html')

@app.route("/picks/zipcode/<zip_code>")
def picks_for_zip_code(zip_code):
    logger.debug("Picks for Zip: "+zip_code)
    tract_id2s = db.tractId2sInZipCode(zip_code)
    logger.debug("   found "+str(len(tract_id2s))+" tracts: "+" ".join(tract_id2s))
    pop_map = db.countryPopulationByTractId2List(tract_id2s)
    games = picker.by_population(pop_map)[:5]
    return render_template('games.html', games=games)

@app.route("/picks/location/<lat>/<lng>")
def picks_for_location(lat,lng):
    try:
        logger.debug("Picks for location: ["+str(lat)+","+str(lng)+"]")
        place = util.geo.reverse_geocode(lat,lng)
        logger.debug("  location details: "+json.dumps(place))
        tract_id2 = place['Block']['FIPS'][:-4]
        pop_map = db.countryPopulationByTractId2(tract_id2)
        games = picker.by_population(pop_map)[:5]
        return render_template('games.html', games=games)
    except:
        # geocoding failed for some reason, so fall back to making user pick location by zip
        logger.error("Couldn't get picks for ["+str(lat)+","+str(lng)+"]")
        return render_template('select-zip-code.html',
            error="Sorry, we couldn't automatically find your location!")

if __name__ == "__main__":
    app.debug = True
    app.run()
