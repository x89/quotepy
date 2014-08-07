#!/usr/bin/env python
import sys

from quotepy.models import Base, engine, session, Quote

def main():
    args = sys.argv[1:]

    if args:
        if args[0] == "init_db":
            Base.metadata.create_all(engine)
        
        if args[0] == "drop_db":
            Base.metadata.drop_all(engine)

        if args[0] == "accept":
            quote = session.query(Quote).filter(Quote.quote_id == args[1]).first()

            quote.status = "accepted"

            session.add(quote)
            session.commit()

            print("quote #%s accepted" % (quote.quote_id,))

        if args[0] == "remove":
            quote = session.query(Quote).filter(Quote.quote_id == args[1]).first()

            quote.status = "removed"

            session.add(quote)
            session.commit()

        if args[0] == "really_remove":
            quote = session.query(Quote).filter(Quote.quote_id == args[1]).first()

            session.delete(quote)
            session.commit()

        if args[0] == "import":
            import json
            import datetime

            # Read some JSON from David's export from stdin
            data = json.loads(sys.stdin.read())

            quotes = []

            # No validation LET'S DO THIS LIVE
            for entry in data:
                i = entry["id"]
                q = entry["quote"]
                d = datetime.datetime.fromtimestamp(entry["timestamp"])
                s = entry["popularity"]

                quote = Quote(raw=q)

                quote.bash_id = i

                quote.pub_date = d
                quote.chg_date = d
                quote.acc_date = d

                quote.status = "accepted"

                quote.score = s

                quotes.append(quote)

            session.add_all(quotes)
            session.commit()

if __name__ == "__main__":
    main()
