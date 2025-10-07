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
    ticket = dal.get_ticket(ticket_id)
    if not ticket:
        abort(404, "Ticket not found.")
    return render_template("view_ticket.html", ticket=ticket)

# new ticket page
@app.route("/new-ticket", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "Low").strip()

        if not name or not description:
            abort(400, "Name and description are required.")
        if not priority:
            abort(400, "Priority is required.")
        if len(name) > 100:
            abort(400, "Length of name must be 100 words or under.")
        if len(description) > 1000:
            abort(400, "Length of description must be 100 words or under.")

        dal.create_ticket(name, description, priority=priority)
        return redirect(url_for("index"))

    return render_template("new_ticket.html")

# close ticket
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    ticket = dal.get_ticket(ticket_id)
    if not ticket:
        abort(404, "Ticket not found.")
    if ticket.status == "Closed":
        abort(400, "Ticket has already been closed.")
    dal.set_status(ticket_id, "Closed")
    return redirect(url_for("index")) # back to homepage after close --shaun
    # hi shaun

if __name__ == "__main__":
    app.run(debug=True)
