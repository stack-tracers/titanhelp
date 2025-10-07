from flask import Flask, render_template, request, redirect, url_for, abort
from titanhelp_dal.dal import TitanHelpDAL

app = Flask(__name__)

# initialize DAL (creates titanhelp.db if not exists)
dal = TitanHelpDAL("titanhelp.db")

# homepage
@app.route("/")
def index():
    try:
        # fetch all tickets from DAL
        tickets = dal.list_tickets()
    except Exception as e:
        return render_template("error.html", code=500, error=f"Database Connection Failed: {e}"), 500
    return render_template("index.html", tickets=tickets)

# view ticket
@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    # fetch a single ticket from DAL
    try:
        ticket = dal.get_ticket(ticket_id)
    except Exception as e:
        return render_template("error.html", code=500, error=f"Unexpected Error: {e}"), 500

    if not ticket:
        return render_template("error.html", code="404", error="Ticket not found."), 404
    return render_template("view_ticket.html", ticket=ticket), 200

# new ticket page
@app.route("/new-ticket", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "Low").strip()

        if not name or not description:
            return render_template("new_ticket.html", code=400, error="Name and description are required."), 400
        if not priority:
            return render_template("new_ticket.html", code=400, error="Priority Level is required."), 400
        if len(name) > 100:
            return render_template("new_ticket.html", code=400, error="Length of name must be 100 words or under."), 400
        if len(description) > 1000:
            return render_template("new_ticket.html", code=400, error="Length of description must be 100 words or under."), 400

        try: 
            dal.create_ticket(name, description, priority=priority)
        except ValueError as e:
            return render_template("error.html", code=400, error=f"ValueError: {e}"), 400
        except Exception as e:
            return render_template("error.html", code=500, error=f"Unexpected Error: {e}"), 500

        return render_template("new_ticket.html", msg=f"Successfully Created Ticket"), 201

    return render_template("new_ticket.html"), 200

# close ticket
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    try: 
        ticket = dal.get_ticket(ticket_id)
    except ValueError as e:
         return render_template("error.html", ticket=ticket, code=400, error=f"ValueError: {e}"), 400
    except Exception as e:
        return render_template("error.html", ticket=ticket, code=500, error=f"Unexpected Error: {e}"), 500

    if not ticket:
        return render_template("error.html", code=404, error="Ticket not found."), 404

    if ticket.status == "Closed":
        return render_template("error.html", code=400, error="Ticket has already been closed."), 400

    try:
        dal.set_status(ticket_id, "Closed")
    except ValueError as e:
        return render_template("error.html", code=400, error=f"ValueError: {e}"), 400
    except Exception as e:
        return render_template("error.html", code=500, error=f"Unexpected Error: {e}"), 500

    return redirect(url_for("index")) # back to homepage after close --shaun

# simple error page
# send users to this page instead of index when dealing with existing tickets
# if users are sent to index with an error the tickets will not load
@app.route("/error")
def error():
    return render_template("error.html", info="How did you get here?"), 418

if __name__ == "__main__":
    app.run(debug=True)
