from flask import *
from flask_dance.contrib.google import make_google_blueprint, google
import database.controller as controller
import json
import os

app = Flask(__name__)
app.secret_key = "secret"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

with open("credentials.json") as credentials:
    cred = json.load(credentials)

app.config["GOOGLE_OAUTH_CLIENT_ID"] = cred["clientID"]
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = cred["clientSecret"]
googleLogin = make_google_blueprint(scope = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"])
app.register_blueprint(googleLogin, url_prefix = "/login")

connection = controller.connect()

def getUser(email):
    for entry in controller.retrieve(connection):
        if entry["email"] == email:
            return entry
    return False

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """ login/create account for user and show dashboard """
    if not google.authorized:
        return redirect(url_for("google.login"))
    response = google.get("/oauth2/v1/userinfo")
    assert response.ok, response.text
    response = response.json()
    userData = getUser(response["email"])
    if not userData:
        controller.create(connection, 0, response["name"], response["picture"], response["email"], 0)
        session["data"] = userData
        return render_template("dashboard.html", data = userData)
    else:
        session["data"] = userData
        return render_template("dashboard.html", data = userData)

@app.route("/transaction", methods = ["GET", "POST"])
def transaction():
    reward = 10
    """ make a transaction """
    if request.method == "GET":
        return render_template("transaction.html")
    elif request.method == "POST":
        try:
            data = session["data"]
        except:
            return redirect(url_for("dashboard"))
        try:
            amount = request.form["amount"]
            senderID = data["id"]
            senderCoins = data["coins"]
            if senderCoins < int(amount):
                return render_template("message.html", first = "You don't have enough AarushCoin!", second = f"Earn more, than you can make your transaction of {amount}AC")
            reciverEmail = request.form["rec-email"]
            reciever = getUser(reciverEmail)
            reciverID = reciever["id"]
            recieverCoins = reciever["coins"]
            senderCoins += reward
            senderCoins -= int(amount)
            recieverCoins += int(amount)
            controller.update(connection, senderID, "coins", senderCoins)
            controller.update(connection, reciverID, "coins", recieverCoins)
            return render_template("message.html", first = "Your transaction is complete!", second = "The amount of AC you requested has been sent to your recipent! It may take a few moments for the changes to appear across the site.")
        except TypeError:
            return render_template("message.html", first = "Either that user does not exist, or you're trying to send some coins to yourself...", second = "If it's the former, check the email for typos or ask the recipent to sign up for AarushCoin. If it's the other one, idk... ask Aarush for some coins?")
        except ValueError:
            return render_template("message.html", first = "The number is not in the correct format!", second = "Check if the amount is a whole number that is also positive.")
        except:
            return render_template("message.html", first = "Something went wrong", second = "That's never good. The system alerted Aarush about this.")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True)