"""galaxy-lite: a private, stdlib-only replica of the Battlecode judging core (siarnaq + saturn), for battlecode-dev.

Design: research/prior/GALAXY.md sections 6.4 and 6.5. Modules:
  db.py           SQLite schema (galaxy table, field and enum names), data dir, small helpers
  rating.py       Penalized Elo (teams/models.py Rating) + MatchParticipant.try_rating_update + the rating pump
  matchmaking.py  generate_4regular_graph + autoscrim (teams/managers.py), scrimmage requests and their rules
  worker.py       saturn replacement: claim -> compile/execute -> report (RUN/OK!/TRY/ERR) -> rating pump
  api.py          JSON read models + http.server API on 127.0.0.1:8023
The CLI is tools/replica.py. Nothing here talks to any network service; the only network socket is the API's
listener on the loopback interface.
"""
