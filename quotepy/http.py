#!/usr/bin/env python
from random import randint
from sqlalchemy import func
from math import ceil

from flask import Flask, redirect, abort, url_for, render_template, request

from quotepy.models import session, Quote

# Some pagination
class Paginator:
    def __init__(self, query, page, per_page=20):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = query.count()

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    @property
    def items(self):
        return self.query\
                       .offset(self.page * self.per_page)\
                       .limit(self.per_page)\
                       .all()

# TODO move all of this to a config file
app = Flask(__name__)
app.debug = True

# TODO get these from the same config
@app.context_processor
def inject_globals():

    # Oh god, do we really need two queries? NO!
    approved = session.query(Quote)\
                   .filter(Quote.status == "accepted")\
                   .count()

    pending = session.query(Quote)\
                  .filter(Quote.status == "pending")\
                  .count()

    return dict(
            SITE_TITLE="screddit bash",
            QUOTES_APPROVED=approved,
            QUOTES_PENDING=pending
            )

@app.route("/")
def index():
    return redirect(url_for("latest"))

@app.route("/latest")
def latest():
    """The latest quotes as sorted by submission date."""

    quotes = session\
                .query(Quote)\
                .filter(Quote.status=="accepted")\
                .order_by(Quote.pub_date.desc())\
                .limit(10)\
                .all()

    return render_template(
            "listing.html",
            quotes=quotes,
            pagetitle="latest"
            )

@app.route("/browse", defaults={"page": 1})
@app.route("/browse/page/<int:page>")
def browse(page):
    """Browse through all the quotes sorted by their submission dates."""

    quotes = session\
                .query(Quote)\
                .filter(Quote.status=="accepted")\
                .order_by(Quote.pub_date)\

    paginator = Paginator(quotes, page)

    return render_template(
            "listing.html",
            page=page,
            pagination=paginator,
            quotes=paginator.items,
            pagetitle="browse"
            )

    return render_template("listing.html")

@app.route("/top")
def top():
    quotes = session\
                .query(Quote)\
                .filter(Quote.status=="accepted")\
                .order_by(Quote.score.desc())\
                .limit(20)\
                .all()

    return render_template(
            "listing.html",
            quotes=quotes,
            pagetitle="top"
            )

    return render_template("listing.html")

@app.route("/random")
def random():
    """A random set of quotes."""
    max_id, min_id = session\
                         .query(func.max(Quote.id),
                                func.min(Quote.id))\
                          .first()

    # Pick a 100
    ids = [randint(min_id, max_id) for _ in range(100)]

    # Get them and pray 20 are not deleted/pending/non-accepted
    quotes = session\
                .query(Quote)\
                .filter(Quote.status=="accepted")\
                .filter(Quote.id.in_(ids))\
                .limit(20)\
                .all()

    return render_template(
            "listing.html",
            quotes=quotes,
            pagetitle="random"
            )

    return render_template("listing.html")

@app.route("/view/<int:quote_id>")
def view(quote_id):
    """View a specifc quote"""

    quote = session\
               .query(Quote)\
               .filter(Quote.id==quote_id)\
               .limit(1)\
               .first()

    if quote is None:
        return abort(404)

    return render_template(
            "single.html",
            quote=quote,
            pagetitle="#%s" % (quote.id,)
            )

    return render_template("listing.html")

@app.route("/vote/<string:quote_id>", methods=["POST"])
def vote(quote_id):
    """Up or down!"""
    quote = session\
               .query(Quote)\
               .filter(Quote.id==quote_id)\
               .limit(1)\
               .first()

    if quote is None:
        return abort(404)

    try:
        direction = int(request.form["direction"])
    except ValueError:
        return abort(400)

    if not direction in (-1, 1):
        return abort(400)

    quote.score += direction

    session.add(quote)
    session.commit()

    return str(quote.score)

@app.route("/add", methods=["GET"])
def add_form():
    return render_template("add.html",
               pagetitle="add")

@app.route("/add", methods=["POST"])
def add_handler():
    # Check if this is an actual quote. We do this *very* naively
    if not "quote" in request.form:
        return render_template("add.html", message="wtf")

    # Maybe validate? Nah.
    quote = Quote(raw=request.form["quote"])

    session.add(quote)
    session.commit()

    return redirect(url_for("view", quote_id=quote.id))

def main():
    app.run("0.0.0.0", 5001)

if __name__ == "__main__":
    main()
