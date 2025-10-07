from flask import Flask, render_template, request, redirect, url_for, abort
from titanhelp_dal.dal import TitanHelpDAL

app = Flask(__name__)

# initialize DAL (creates titanhelp.db if not exists)
dal = TitanHelpDAL("titanhelp.db")

# homepage
@app.route("/")
def index():
    # fetch all tickets from DAL
    tickets = dal.list_tickets()
    return render_template("index.html", tickets=tickets)

# view ticket
@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    # fetch a single ticket from DAL
    try:
        ticket = dal.get_ticket(ticket_id)
    except Exception as e:
        code = 500
        error = f"Unexpected Error\n{e}"
        abort(code, error)
    if not ticket:
        code = 404
        error = "Ticket not found."
        abort(code, error)
    return render_template("view_ticket.html", ticket=ticket)

# new ticket page
@app.route("/new-ticket", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "Low").strip()

        if not name or not description:
            code = 400
            error = "Name and description are required."
            abort(code, error)

        if not priority:
            code = 400
            error = "Priority is required."
            abort(code, error)
        if len(name) > 100:
            code = 400
            error = "Length of name must be 100 words or under."
            abort(code, error)
        if len(description) > 1000:
            code = 400
            error = "Length of description must be 100 words or under."
            abort(code, error)

        try: 
            dal.create_ticket(name, description, priority=priority)
        except ValueError as e:
            code = 400,
            error = f"ValueError\n{e}"
            abort(code, error)
        except Exception as e:
            code = 500
            error = f"Unexpected Error\n{e}"
            abort(code, error)

        return redirect(url_for("index"))

    return render_template("new_ticket.html")

# close ticket
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    try: 
        ticket = dal.get_ticket(ticket_id)
    except ValueError as e:
        code = 400
        error = f"ValueError\n{e}"
        abort(code, error)
    except Exception as e:
        code = 500
        error= f"Unexpected Error\n{e}"
        abort(code, error)

    if not ticket:
        code = 404
        error = "Ticket not found."
        abort(code, error)
    if ticket.status == "Closed":
        code = 400
        error = "Ticket has already been closed."
        abort(code, error)

    try:
        dal.set_status(ticket_id, "Closed")
    except ValueError as e:
        code = 400
        error = f"ValueError\n{e}"
        abort(code, error)
    except Exception as e:
        code = 500
        error = f"Unexpected Error\n{e}"
        abort(code, error)

    return redirect(url_for("index")) # back to homepage after close --shaun
    # hi shaun

if __name__ == "__main__":
    app.run(debug=True)
