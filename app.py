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
        return render_template("index.html", code=500, error=f"Database Connection Failed: {e}")
    return render_template("index.html", tickets=tickets)

# view ticket
@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    # fetch a single ticket from DAL
    try:
        ticket = dal.get_ticket(ticket_id)
    except Exception as e:
        return render_template("index.html", code=500, error=f"Unexpected Error: {e}")

    if not ticket:
        return render_template("index.html", code=404, error="Ticket not found.")
    return render_template("view_ticket.html", ticket=ticket)

# new ticket page
@app.route("/new-ticket", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "Low").strip()

        if not name or not description:
            return render_template("new_ticket.html", code=400, error="Name and description are required.")
        if not priority:
            return render_template("new_ticket.html", code=400, error="Priority Level is required.")
        if len(name) > 100:
            return render_template("new_ticket.html", code=400, error="Length of name must be 100 words or under.")
        if len(description) > 1000:
            return render_template("new_ticket.html", code=400, error="Length of description must be 100 words or under.")

        try: 
            dal.create_ticket(name, description, priority=priority)
        except ValueError as e:
            return render_template("new_ticket.html", code=400, error=f"ValueError: {e}")
        except Exception as e:
            return render_template("new_ticket.html", code=500, error=f"Unexpected Error: {e}")

        return redirect(url_for("index"))

    return render_template("new_ticket.html")

# close ticket
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    try: 
        ticket = dal.get_ticket(ticket_id)
    except ValueError as e:
         return render_template("view_ticket.html", ticket=ticket, code=400, error=f"ValueError: {e}")
    except Exception as e:
        return render_template("view_ticket.html", ticket=ticket, code=500, error=f"Unexpected Error: {e}")

    if not ticket:
        return render_template("index.html", code=404, error="Ticket not found.")

    if ticket.status == "Closed":
        return render_template("index.html", code=400, error="Ticket has already been closed.")

    try:
        dal.set_status(ticket_id, "Closed")
    except ValueError as e:
        return render_template("index.html", code=400, error=f"ValueError: {e}")
    except Exception as e:
        return render_template("index.html", code=500, error=f"Unexpected Error: {e}")

    return redirect(url_for("index")) # back to homepage after close --shaun
    # hi shaun

if __name__ == "__main__":
    app.run(debug=True)
