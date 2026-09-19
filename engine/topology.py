# engine/topology.py

ALPHA_ORDER = ["S01", "S02", "S03", "S04", "H01", "H02", "S05", "S06", "S07", "S08"]
BETA_ORDER  = ["S11", "S12", "S13", "S14", "H01", "H02", "S15", "S16", "S17", "S18"]

def get_line_order(station_id):
    if station_id in ALPHA_ORDER:
        return "ALP", ALPHA_ORDER
    elif station_id in BETA_ORDER:
        return "BET", BETA_ORDER
    return None, []

def expand_route(start_loc, end_loc, bound):
    """
    Expands a start and end location into all intermediate PLAT and SEC sectors.
    """
    start_stn = start_loc.split(":")[-1]
    end_stn = end_loc.split(":")[-1]
    
    line, order = get_line_order(start_stn)
    if not line or start_stn not in order or end_stn not in order:
        return [start_loc]
    
    i1 = order.index(start_stn)
    i2 = order.index(end_stn)
    
    step = 1 if i1 <= i2 else -1
    station_seq = [order[i] for i in range(i1, i2 + step, step)]
    
    sectors = []
    for idx, stn in enumerate(station_seq):
        sectors.append(f"PLAT:{line}:{stn}:{bound}")
        if idx < len(station_seq) - 1:
            next_stn = station_seq[idx + 1]
            pair = f"{stn}_{next_stn}" if order.index(stn) < order.index(next_stn) else f"{next_stn}_{stn}"
            sectors.append(f"SEC:{line}:{pair}:{bound}")
            
    return sectors

def get_exclusion_buffers(sector, nature_of_works):
    """
    Calculates safety buffers based on Nature of Works:
    - Live: 2 sectors + opposite bound mirror
    - Non-live (Consist): 1 sector
    - Non-live (Others): 0 sectors
    """
    buffers = [sector]
    parts = sector.split(":")
    if len(parts) < 4:
        return buffers
    
    sec_type, line, ident, bound = parts[0], parts[1], parts[2], parts[3]
    opp_bound = "WB" if bound == "EB" else "EB"
    
    if "LIVE" in nature_of_works.upper():
        # Mirror opposite bound
        buffers.append(f"{sec_type}:{line}:{ident}:{opp_bound}")
        # Crossover coupling at interchange
        if "H01" in ident or "H02" in ident:
            opp_line = "BET" if line == "ALP" else "ALP"
            buffers.append(f"{sec_type}:{opp_line}:{ident}:{bound}")
            buffers.append(f"{sec_type}:{opp_line}:{ident}:{opp_bound}")
            
    return list(set(buffers))
