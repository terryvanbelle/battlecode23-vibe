"""Matchmaking and scrimmage requests, ported from siarnaq.

Sources (galaxy f343088):
  backend/siarnaq/api/teams/managers.py:11-90     generate_4regular_graph (verbatim)
  backend/siarnaq/api/teams/managers.py:163-253   TeamQuerySet.autoscrim
  backend/siarnaq/api/compete/serializers.py:400-465  ScrimmageRequestSerializer.validate / validate_requested_to /
                                                      to_internal_value
  backend/siarnaq/api/compete/views.py:942-1041   ScrimmageRequestViewSet.create (rate limit, pair cap, upward only)
  backend/siarnaq/api/compete/managers.py:155-235 ScrimmageRequestQuerySet.accept / reject / cancel
  backend/siarnaq/api/compete/models.py:612-635   determine_is_alternating / determine_order
  backend/siarnaq/api/compete/signals.py:33-70    auto_accept_reject_scrimmage

The request *rules* (ranked: shuffled order, random maps, no staff, rate limit, pair cap, upward-only) apply only
when episode.enforce_rules = 1. Integrity checks (opponent exists and has an accepted submission, not yourself,
known maps) always apply. Auto-accept is each team's auto_accept_reject_* setting, default 'A' in the replica.
"""
import random
import re

from . import db
from .db import PlayerOrder, SaturnStatus, ScrimmageRequestAcceptReject, ScrimmageRequestStatus, TeamStatus


class RequestError(Exception):
    """A refused scrimmage request. http is the status galaxy answers with (400, 409 or 429)."""

    def __init__(self, message, http=400):
        super().__init__(message)
        self.http = http


# ---------------------------------------------------------------- generate_4regular_graph (verbatim)
def generate_4regular_graph(n):
    """
    Generate a 4-regular graph on n nodes labelled 0 through n-1. The graph is
    guaranteed to have the following properties:

    1. For each edge between two nodes x and y, |x-y| is small. In fact, |x-y| <= 4.
    2. For each node x except 0 and n-1, its neighbors are not all <x or all >x.

    Parameters
    ----------
    n : int
        The number of nodes in the graph, must be at least 5

    Returns
    -------
    List[Tuple(int, int)]
        A list of undirected edges where nodes are numbered from 0 to n-1, inclusive.
    """
    # At a high level, this algorithm works as follows:
    # 1. Partition the nodes into contiguous groups of size between 5-9, inclusive.
    # 2. Apply a pre-determined regular graph to each partition.
    # 3. To ensure the min and max in each partition also receive smaller and larger
    #    neighbors, redirect some edges to cross into the neighboring partitions.
    if n < 5:
        raise ValueError("Not enough nodes for 4-regular graph")

    # Step 1: Partition into groups. We use groups of size between 5-9, but prefer using
    # the smaller sizes 5 and 6 whenever possible. We manually solve the base cases in
    # which random choices might not be safe.
    partition_base_cases = ".....567895566755565555565"
    partition_sizes, remaining = [], n
    while remaining:
        if remaining < len(partition_base_cases):
            m = int(partition_base_cases[remaining])
        else:
            m = random.randint(5, 6)
        partition_sizes.append(m)
        remaining -= m
    random.shuffle(partition_sizes)

    # Step 2: Apply pre-determined regular graphs.
    predetermined = {
        5: "01 02 03 04 12 13 14 23 24 34",
        6: "01 02 03 04 12 13 15 24 25 34 35 45",
        7: "01 02 03 04 12 13 14 25 26 35 36 45 46 56",
        8: "01 02 03 04 12 13 14 25 26 35 37 46 47 56 57 67",
        9: "01 02 03 04 12 13 14 23 25 36 47 48 56 57 58 67 68 78",
    }
    adj_list = {i: [] for i in range(n)}
    start = 0
    for m in partition_sizes:
        for i, j in predetermined[m].split():
            adj_list[start + int(i)].append(start + int(j))
            adj_list[start + int(j)].append(start + int(i))
        start += m

    # Step 3: Redirect edges. For each pair of nodes (A, B) on a partition boundary, we
    # select a random neighbor for each of them, and make the following swap:
    #                       \                   .----\--.
    #                  C---A \ B---D    ===>    C   A \ B   D
    #                         \                     '--\----'
    # This transformation preserves node degrees so the graph continues to be 4-regular.
    # To ensure we do not create edges that are too long, we do not allow C and D to be
    # the furthest neighbors from A and B. This prevents the redirection operation from
    # repeatedly acting on the same edge and making it longer and longer.
    start = 0
    for m in partition_sizes[:-1]:
        a, b = start + m - 1, start + m
        c = random.choice(sorted(adj_list[a])[1:])
        d = random.choice(sorted(adj_list[b])[:-1])
        for x, y in [(a, c), (b, d)]:
            adj_list[x].remove(y)
            adj_list[y].remove(x)
        for x, y in [(b, c), (a, d)]:
            adj_list[x].append(y)
            adj_list[y].append(x)
        start += m

    # Convert to edge-list representation.
    return [(i, j) for i in range(n) for j in adj_list[i] if j > i]


# ---------------------------------------------------------------- autoscrim
def check_best_of(best_of):
    """episodes/serializers.py AutoscrimSerializer: best_of = IntegerField(min_value=1). Galaxy refuses 0 or a
    negative count with a 400 before Episode.autoscrim runs; without this check best_of=0 queued matches with no maps
    (each failed 5 times and ended ERR) and a numeric string raised TypeError."""
    try:   # DRF IntegerField.to_internal_value: int(re_decimal.sub('', str(data))), so 3, '3' and 3.0 pass
        n = int(re.sub(r'\.0*\s*$', '', str(best_of)))
    except ValueError:
        raise ValueError(f'best_of must be an integer, got {best_of!r}') from None
    if n < 1:
        raise ValueError(f'best_of must be at least 1, got {n}')
    return n


def autoscrim_teams(conn, episode=db.EPISODE):
    """REGULAR teams with an active submission, by decreasing rating MEAN (galaxy: "We intentionally use the rating
    mean and not the penalized rating value ... We like high entropy!"). Galaxy leaves ties in database order; the
    replica breaks them by team id."""
    rows = conn.execute(
        'SELECT t.id AS pk, t.name, r.mean, '
        '  (SELECT s.id FROM submission s WHERE s.team=t.id AND s.accepted=1 ORDER BY s.id DESC LIMIT 1) '
        '  AS active_submission '
        'FROM team t JOIN rating r ON r.id=t.rating_id '
        "WHERE t.episode=? AND t.status='R' ORDER BY r.mean DESC, t.id", (episode,)).fetchall()
    return [dict(r) for r in rows if r['active_submission'] is not None]


def autoscrim(conn, *, episode=db.EPISODE, best_of=None):
    """TeamQuerySet.autoscrim: ranked best-of-k scrimmages for every team with an accepted submission. Each team gets
    exactly 4 matches, or a round-robin when there are 4 teams or fewer. Returns the new match ids (queued)."""
    ep = db.get_episode(conn, episode)
    best_of = check_best_of(ep['autoscrim_best_of'] if best_of is None else best_of)
    maps = list(db.public_maps(conn, episode).values())
    if best_of > len(maps):
        raise ValueError("Not enough maps available")

    with db.tx(conn):
        teams = autoscrim_teams(conn, episode)

        if len(teams) <= 4:
            # Round-robin for small pool
            edges = [(i, j) for j in range(len(teams)) for i in range(j)]
        else:
            edges = generate_4regular_graph(len(teams))

        # Shuffle the edge direction so that player turn order is not biased
        for i in range(len(edges)):
            if random.randint(0, 1):
                edges[i] = edges[i][::-1]

        # Shuffle the edge ordering so that match queue priority is not biased
        random.shuffle(edges)

        # Create the participations and matches (bulk_create order: all matches, then all participations, then maps)
        matches = [db.insert_match(conn, episode=episode, alternate_order=True, is_ranked=True, source='autoscrim')
                   for _ in edges]
        for edge, match in zip(edges, matches):
            for player_index, node in enumerate(edge):
                db.insert_participant(conn, team_id=teams[node]['pk'], submission_id=teams[node]['active_submission'],
                                      match_id=match, player_index=player_index)
        for match in matches:
            db.set_match_maps(conn, match, random.sample(maps, best_of))

    # Send them to Saturn
    db.enqueue(conn, matches)
    return matches


# ---------------------------------------------------------------- scrimmage requests
def determine_is_alternating(player_order):
    """Determine whether the player order should be alternating."""
    return player_order == PlayerOrder.SHUFFLED


def determine_order(player_order, requested_by, requested_to):
    """Determine the player order for the match (random for shuffled requests)."""
    match (player_order, random.getrandbits(1)):
        case (PlayerOrder.REQUESTER_FIRST, _) | (PlayerOrder.SHUFFLED, 0):
            return [requested_by, requested_to]
        case (PlayerOrder.REQUESTER_LAST, _) | (PlayerOrder.SHUFFLED, 1):
            return [requested_to, requested_by]
        case _:
            raise ValueError("Unknown color")


def validate_request(conn, *, requested_by, requested_to, is_ranked, player_order, map_names, episode=db.EPISODE):
    """Serializer + view checks of ScrimmageRequestViewSet.create. Returns the list of map ids to play.
    requested_by / requested_to are team rows. Raises RequestError."""
    ep = db.get_episode(conn, episode)
    rules = bool(ep['enforce_rules'])
    by_staff = db.is_staff(requested_by)

    # Permission HasTeamSubmission: the requester needs an accepted submission.
    if db.active_submission(conn, requested_by['id']) is None:
        raise RequestError('Requesting team has no accepted submission', 403)

    # validate_requested_to
    if requested_to['id'] == requested_by['id']:
        raise RequestError('Cannot request scrimmage against yourself')
    visible = requested_to['status'] in (TeamStatus.REGULAR, TeamStatus.STAFF)
    if db.active_submission(conn, requested_to['id']) is None or (rules and not by_staff and not visible):
        raise RequestError('No valid opponent found')

    if player_order not in PlayerOrder.ALL:
        raise RequestError(f'Unknown player_order {player_order!r}')

    # validate
    if rules and is_ranked:
        if by_staff:
            raise RequestError('Staff can only have unranked matches')
        if db.is_staff(requested_to):
            raise RequestError('Matches against staff must be unranked')
        if player_order != PlayerOrder.SHUFFLED:
            raise RequestError('Ranked matches must use shuffled order')

    # to_internal_value
    maps = db.public_maps(conn, episode)
    map_names = list(map_names or [])
    if rules and len(map_names) > db.MAX_MAPS_PER_SCRIMMAGE:
        raise RequestError(f'map_names: Ensure this field has no more than {db.MAX_MAPS_PER_SCRIMMAGE} elements.')
    if rules and is_ranked and map_names:
        raise RequestError('map_names: must be empty for ranked')
    elif not map_names and (is_ranked or not rules):
        # Ranked matches default to best-of-3. (The replica also gives unranked requests 3 random maps when
        # rules are off and none are named.)
        map_names = random.sample(list(maps.keys()), ep['autoscrim_best_of'] if not rules else 3)
    if not map_names:
        raise RequestError('map_names: must not be empty')
    bad = [name for name in map_names if name not in maps]
    if bad:
        raise RequestError(f'The following maps were invalid: {bad}')
    map_ids = [maps[name] for name in map_names]

    if not rules:
        return map_ids

    # views.create
    if is_ranked and not ep['is_allowed_ranked_scrimmage']:
        raise RequestError('Ranked matches are currently disabled.', 409)

    past_hour = db.ago(hours=1)
    # requests initiated by requestor in past hour
    existing_requests_from_requestor = conn.execute(
        'SELECT COUNT(*) FROM scrimmage_request WHERE requested_by=? AND is_ranked=? AND created>=?',
        (requested_by['id'], int(bool(is_ranked)), past_hour)).fetchone()[0]
    # matches involving requestor in past hour
    match_count = conn.execute(
        'SELECT COUNT(*) FROM match_participant mp JOIN match m ON m.id=mp.match '
        'WHERE mp.team=? AND m.episode=? AND m.is_ranked=? AND m.created>=?',
        (requested_by['id'], episode, int(bool(is_ranked)), past_hour)).fetchone()[0]
    max_matches = ep['ranked_scrimmage_hourly_limit'] if is_ranked else ep['unranked_scrimmage_hourly_limit']
    # check number of matches requested + run in past hour (rate limiting)
    if existing_requests_from_requestor + match_count >= max_matches:
        raise RequestError('You have requested too many scrimmages in the past hour.', 429)
    # check if too many ranked scrimmages requested between two teams
    if is_ranked:
        existing_requests = conn.execute(
            'SELECT COUNT(*) FROM scrimmage_request WHERE requested_by=? AND is_ranked=1 AND created>=? '
            'AND requested_to=?', (requested_by['id'], past_hour, requested_to['id'])).fetchone()[0]
        existing_matches = conn.execute(
            'SELECT COUNT(*) FROM match m WHERE m.is_ranked=1 AND m.status IN (?,?,?,?) '
            'AND EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND team=?) '
            'AND EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND team=?)',
            (*SaturnStatus.ACTIVE, requested_by['id'], requested_to['id'])).fetchone()[0]
        if existing_requests + existing_matches >= db.MAX_SCRIMMAGES_AGAINST_TEAM:
            raise RequestError('You have too many running scrimmages or requests with this team.', 409)
    # stop teams from scrimmaging lower ranked teams
    if is_ranked:
        v1 = db.get_rating(conn, requested_by['rating_id'])['value']
        v2 = db.get_rating(conn, requested_to['rating_id'])['value']
        if v1 > v2:
            raise RequestError('You cannot request a ranked scrimmage against a team ranked lower than you.', 409)
    return map_ids


def create_request(conn, *, requested_by, requested_to, is_ranked, player_order=PlayerOrder.SHUFFLED,
                   map_names=None, episode=db.EPISODE):
    """POST /api/compete/<ep>/request/: validate, save, then auto accept/reject per the opponent's setting.
    Returns (request_id, status, match_id or None)."""
    with db.tx(conn):
        by = db.get_team(conn, requested_by, episode)
        to = db.get_team(conn, requested_to, episode)
        map_ids = validate_request(conn, requested_by=by, requested_to=to, is_ranked=is_ranked,
                                   player_order=player_order, map_names=map_names, episode=episode)
        rid = conn.execute(
            'INSERT INTO scrimmage_request(episode, created, status, is_ranked, requested_by, requested_to, '
            'player_order) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (episode, db.now(), ScrimmageRequestStatus.PENDING, 1 if is_ranked else 0, by['id'], to['id'],
             player_order)).lastrowid
        for i, m in enumerate(map_ids):
            conn.execute('INSERT INTO request_map(request, map, sort) VALUES (?, ?, ?)', (rid, m, i))
        # signals.auto_accept_reject_scrimmage
        setting = to['auto_accept_reject_ranked'] if is_ranked else to['auto_accept_reject_unranked']
    if setting == ScrimmageRequestAcceptReject.AUTO_ACCEPT:
        matches = accept(conn, [rid])
        return rid, ScrimmageRequestStatus.ACCEPTED, (matches[0] if matches else None)
    if setting == ScrimmageRequestAcceptReject.AUTO_REJECT:
        reject(conn, [rid])
        return rid, ScrimmageRequestStatus.REJECTED, None
    return rid, ScrimmageRequestStatus.PENDING, None


def accept(conn, request_ids):
    """ScrimmageRequestQuerySet.accept: pending requests -> ACCEPTED, one queued match each. Returns match ids."""
    matches = []
    with db.tx(conn):
        ep_ranked_ok = {}
        requests = [conn.execute("SELECT * FROM scrimmage_request WHERE id=? AND status='P'", (r,)).fetchone()
                    for r in request_ids]
        requests = [r for r in requests if r is not None]
        for req in requests:
            if req['is_ranked']:
                ep = ep_ranked_ok.setdefault(req['episode'], db.get_episode(conn, req['episode']))
                if ep['enforce_rules'] and not ep['is_allowed_ranked_scrimmage']:
                    raise RequestError('Ranked matches are currently disabled.', 409)
        for req in requests:
            conn.execute("UPDATE scrimmage_request SET status='Y' WHERE id=?", (req['id'],))
            subs = {t: db.active_submission(conn, t) for t in (req['requested_by'], req['requested_to'])}
            if None in subs.values():
                raise RequestError('A team in the request has no accepted submission', 409)
            match = db.insert_match(conn, episode=req['episode'], is_ranked=bool(req['is_ranked']),
                                    alternate_order=determine_is_alternating(req['player_order']),
                                    source='request', request_id=req['id'])
            order = determine_order(req['player_order'], req['requested_by'], req['requested_to'])
            for player_index, team_id in enumerate(order):
                db.insert_participant(conn, team_id=team_id, submission_id=subs[team_id], match_id=match,
                                      player_index=player_index)
            db.set_match_maps(conn, match, [r['map'] for r in conn.execute(
                'SELECT map FROM request_map WHERE request=? ORDER BY sort, id', (req['id'],))])
            matches.append(match)
    # Send them to Saturn
    db.enqueue(conn, matches)
    return matches


def reject(conn, request_ids):
    with db.tx(conn):
        for r in request_ids:
            conn.execute("UPDATE scrimmage_request SET status='N' WHERE id=? AND status='P'", (r,))


def cancel_request(conn, request_ids):
    """ScrimmageRequestQuerySet.cancel: pending requests are deleted."""
    with db.tx(conn):
        for r in request_ids:
            if conn.execute("SELECT 1 FROM scrimmage_request WHERE id=? AND status='P'", (r,)).fetchone():
                conn.execute('DELETE FROM request_map WHERE request=?', (r,))
                conn.execute('DELETE FROM scrimmage_request WHERE id=?', (r,))
