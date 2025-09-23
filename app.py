from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# store tickets in memory using a python list until sql is properly integrated
tickets = []

# global ticket_id counter (temporary, sql will handle ticket ids later)
ticket_id = 1

# homepage
@app.route("/")
def index():
    # render the homepage and pass in-memory tickets
    return render_template("index.html", tickets=tickets)

# view ticket
@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return render_template("view_ticket.html", ticket=ticket)


# new ticket page
@app.route("/new-ticket", methods=["GET", "POST"])
def new_ticket():
    global ticket_id # use global ticket_id

    if request.method == "POST":
        # get values from form
        name = request.form.get("name")
        description = request.form.get("description")
        priority = request.form.get("priority")
        
        ticket = {
            "id": ticket_id,
            "name": name[:100], # max 100 chars
            "date": datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
            "description": description[:1000], # max 1000 chars
            "status": "Open", # open by default
            "priority": priority
        }
        tickets.append(ticket)
        ticket_id += 1

        return redirect(url_for("index")) # back to homepage
    
    return render_template("new_ticket.html")

# close ticket
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = "Closed"
            return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
