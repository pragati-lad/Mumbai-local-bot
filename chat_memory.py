# ==================================================
# Chatbot Memory - Conversation Context Tracking
# ==================================================
# Remembers stations, time, and line across turns
# Fills missing info from previous queries
# ==================================================


CONTEXT_TRIGGERS = {
    "what about", "and from", "and to", "also", "how about",
    "after", "before", "around", "same but", "change to",
    "instead", "switch to", "from there"
}


def resolve_query(query, stations, query_time, context):
    """
    Fill missing stations/time from conversation context.
    Returns updated (stations, query_time).
    """
    if not context:
        return stations, query_time

    q = query.lower().strip()

    last_src = context.get("last_source")
    last_dst = context.get("last_dest")
    last_time = context.get("last_time")

    has_context_trigger = any(trigger in q for trigger in CONTEXT_TRIGGERS)

    # 0 stations found but context has stations — reuse them
    if len(stations) == 0 and (last_src or last_dst):
        # Only reuse if query looks like a follow-up
        if has_context_trigger or query_time is not None:
            if last_src:
                stations.append(last_src)
            if last_dst:
                stations.append(last_dst)

    # 1 station found — combine with context
    elif len(stations) == 1:
        new_station = stations[0]

        if "from" in q and last_dst:
            # "from Andheri?" → new source + old dest
            stations = [new_station, last_dst]
        elif "to" in q and last_src:
            # "to Churchgate?" → old source + new dest
            stations = [last_src, new_station]
        elif last_src and last_dst:
            # Ambiguous — assume replacing source, keep dest
            if has_context_trigger:
                stations = [new_station, last_dst]

    # No time but context has time — only reuse on follow-ups
    if query_time is None and last_time is not None and has_context_trigger:
        query_time = last_time

    return stations, query_time


def update_context(context, stations, query_time, intent):
    """
    Save current query info into context for next turn.
    Only updates fields that have values (doesn't erase old context).
    """
    if len(stations) >= 1:
        context["last_source"] = stations[0]
    if len(stations) >= 2:
        context["last_dest"] = stations[1]

    if query_time is not None:
        context["last_time"] = query_time

    if intent and intent != "unknown":
        context["last_intent"] = intent
