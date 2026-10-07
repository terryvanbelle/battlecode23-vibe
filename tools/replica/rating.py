"""Penalized Elo and lazy, creation-ordered rating finalization, ported from siarnaq.

Sources (galaxy f343088):
  backend/siarnaq/settings.py:322-327           TEAMS_ELO_INITIAL/K/SCALE/PENALTY
  backend/siarnaq/api/teams/models.py:13-58     class Rating (save, step, expected_score)
  backend/siarnaq/api/compete/models.py:299-345 Match.try_rating_update
  backend/siarnaq/api/compete/models.py:435-542 MatchParticipant.get_old_rating / try_rating_update
  backend/siarnaq/api/teams/signals.py:14-28    copy_rating_to_profile (db.copy_rating_to_profile)

Galaxy runs try_rating_update from Cloud Tasks (one task per match whenever a match is saved or a team's previous
participation is finalized). Here pump() replaces the queue: it repeats Match.try_rating_update over every match
that still has an unrated participant, in match-creation (pk) order, until a pass finalizes nothing. Because each
side steps from both teams' ratings just before the match, the result depends only on each team's chain order,
never on completion order.
"""
from . import db
from .db import SaturnStatus

TEAMS_ELO_INITIAL = 1500.0
TEAMS_ELO_K = 24.0
TEAMS_ELO_SCALE = 400.0
TEAMS_ELO_PENALTY = 0.85


class Rating:
    """An immutable Penalized Elo rating (mean, n, value). id is None until saved (Django's _state.adding)."""

    __slots__ = ('id', 'mean', 'n', 'value')

    def __init__(self, mean=TEAMS_ELO_INITIAL, n=0, id=None, value=None):
        self.id = id
        self.mean = mean
        self.n = n
        # Rating.value defaults to 0 and is recomputed by save(); an unsaved default Rating() has value 0, which is
        # also what the formula gives for mean 1500, n 0.
        self.value = penalized(mean, n) if value is None else value

    @classmethod
    def from_row(cls, row):
        return None if row is None else cls(row['mean'], row['n'], row['id'], row['value'])

    def save(self, conn):
        """Rating.save: value = mean - TEAMS_ELO_INITIAL * TEAMS_ELO_PENALTY ** n, then insert."""
        self.value = penalized(self.mean, self.n)
        self.id = db.insert_rating(conn, self.mean, self.n)
        return self

    def step(self, opponent_ratings, score):
        """Produce the new rating after a specific match is played (unsaved; the caller saves it)."""
        e_self = self.expected_score(opponent_ratings)
        new_mean = self.mean + TEAMS_ELO_K * (score - e_self)
        return Rating(mean=new_mean, n=self.n + 1)

    def expected_score(self, opponent_ratings):
        """Return the expected score against a given set of opponents."""
        total = 0
        for r in opponent_ratings:
            diff = self.mean - r.mean
            total += 1 / (1 + 10 ** (-diff / TEAMS_ELO_SCALE))
        return total / len(opponent_ratings)

    def __repr__(self):
        return f'Rating(id={self.id}, mean={self.mean:.3f}, n={self.n}, value={self.value:.3f})'


def penalized(mean, n):
    return mean - TEAMS_ELO_INITIAL * TEAMS_ELO_PENALTY ** n


def delta_mean(mean_self, mean_opp, wins, losses):
    """Change of mean for one ranked match won `wins` games to `losses` (two players): 24 * (S - E)."""
    me = Rating(mean_self)
    return me.step([Rating(mean_opp)], wins / (wins + losses)).mean - mean_self


# ---------------------------------------------------------------- MatchParticipant / Match finalization
def get_old_rating(conn, participant):
    """MatchParticipant.get_old_rating: the rating just before this participation, or None if unknown.
    With no previous participation, a default (unsaved) Rating() -- the team's first match."""
    if participant['previous_participation'] is not None:
        prev = conn.execute('SELECT rating_id FROM match_participant WHERE id=?',
                            (participant['previous_participation'],)).fetchone()
        if prev['rating_id'] is None:
            return None  # Previous rating, if known
        return Rating.from_row(db.get_rating(conn, prev['rating_id']))
    return Rating()  # Default for first ever match


def is_finalized(match):
    return match['status'] in SaturnStatus.FINALIZED


def participant_try_rating_update(conn, participant, match, opponents):
    """MatchParticipant.try_rating_update, line for line. Returns the new rating id, or None if not finalized.
    `participant` and `opponents` are match_participant rows read before this match's update began."""
    if participant['rating_id'] is not None:
        return None  # Participant rating is already finalized.

    old_rating = get_old_rating(conn, participant)
    if old_rating is None:
        return None  # Participant rating is not ready to finalize.

    # Matches are unranked if they were supposed to be unranked, or if they ended unsuccessfully.
    is_unranked = (not match['is_ranked']) or (is_finalized(match) and match['status'] != SaturnStatus.COMPLETED)

    rating = None
    if is_unranked:
        if old_rating.id is None:
            # If this is a default-constructed rating, save it to the database.
            # Occurs when this is the team's first-ever match.
            old_rating.save(conn)
        rating = old_rating
    elif is_finalized(match):
        opponent_ratings = [get_old_rating(conn, o) for o in opponents]
        if participant['score'] is None or any(o['score'] is None for o in opponents):
            return None  # galaxy would raise TypeError; a COMPLETED match always has scores here
        total_score = participant['score'] + sum(o['score'] for o in opponents)
        if all(r is not None for r in opponent_ratings):
            if total_score == 0:
                # galaxy divides by zero here (GALAXY.md section 7 item 5); the worker never reports such a result,
                # so this only happens after a manual edit. Leave the chain blocked, as galaxy does.
                return None
            rating = old_rating.step(opponent_ratings, participant['score'] / total_score).save(conn)
        # else: Opponent rating blocks participant from finalize.

    if rating is not None:
        conn.execute('UPDATE match_participant SET rating_id=? WHERE id=?', (rating.id, participant['id']))
        db.copy_rating_to_profile(conn, participant['team'], rating.id)
        return rating.id
    return None


def match_try_rating_update(conn, match_id):
    """Match.try_rating_update. Returns the number of participations finalized."""
    match = conn.execute('SELECT * FROM match WHERE id=?', (match_id,)).fetchone()
    if match['is_ranked'] and not is_finalized(match):
        return 0  # Match ratings are not ready to finalize.
    parts = db.participants(conn, match_id)
    done = 0
    with db.tx(conn):
        for p in parts:
            if participant_try_rating_update(conn, p, match, [o for o in parts if o['id'] != p['id']]) is not None:
                done += 1
    return done


def pump(conn, max_passes=1000):
    """The rating pump (replaces Cloud Tasks): Match.try_rating_update over every match with an unrated
    participant, in creation order, repeated until a pass finalizes nothing. Returns participations finalized."""
    total = 0
    with db.tx(conn):
        for _ in range(max_passes):
            pending = [r['match'] for r in conn.execute(
                'SELECT DISTINCT match FROM match_participant WHERE rating_id IS NULL ORDER BY match')]
            done = sum(match_try_rating_update(conn, m) for m in pending)
            total += done
            if done == 0:
                break
    return total
