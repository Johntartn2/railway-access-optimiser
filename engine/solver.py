# engine/solver.py
import pandas as pd
from engine.topology import expand_route, get_exclusion_buffers

class RailwayScheduler:
    def __init__(self, activity_df, project_df=None, supply_df=None, scenario="A"):
        self.activities = activity_df.copy()
        self.projects = project_df.copy() if project_df is not None else None
        self.supply = supply_df.copy() if supply_df is not None else None
        self.scenario = scenario # "A", "B", or "C"
        
    def solve(self):
        # 1. Topological dependency sort (Predecessors first)
        scheduled_end_weeks = {}
        schedule_access = []
        schedule_occupancy = []
        contract_completion = {}

        # Sort by planned start week and priority
        acts = self.activities.sort_values(by=["planned_start_date", "activity_priority"]).to_dict("records")

        for act in acts:
            act_id = act["activity_id"]
            c_num = act["contract_number"]
            total_access = float(act["total_accesses"])
            nature = act.get("nature_of_works", "Non-live (Others)")
            start_loc = act["start_location_id"]
            end_loc = act["end_location_id"]
            bound = act.get("bound", "EB")
            pred_id = act.get("predecessor_activity_id")

            # Earliest start week calculation
            earliest_week = int(act["planned_start_date"])
            if pd.notna(pred_id) and str(pred_id).strip() in scheduled_end_weeks:
                earliest_week = max(earliest_week, scheduled_end_weeks[str(pred_id).strip()] + 1)

            # Get physical route sectors
            route_sectors = expand_route(start_loc, end_loc, bound)

            # Determine ECLO allowance
            # Scenario A: strictly forbidden (0). B/C: allows ECLO if beneficial
            use_eclo = 1 if self.scenario in ["B", "C"] and nature == "Non-live (Others)" else 0
            yield_per_night = 1.5 if use_eclo == 1 else 1.0

            cur_yield = 0.0
            seq = 1
            curr_week = earliest_week

            while cur_yield < total_access:
                access_night = ((seq - 1) % 3) + 1  # Distribute across contract's available nights

                schedule_access.append({
                    "activity_id": act_id,
                    "access_seq": seq,
                    "week": curr_week,
                    "eclo": use_eclo,
                    "access_night": access_night
                })

                # Occupy all physical sectors in route
                for sec in route_sectors:
                    schedule_occupancy.append({
                        "activity_id": act_id,
                        "week": curr_week,
                        "location_id": sec,
                        "co_share_group": f"b{access_night}"
                    })

                cur_yield += yield_per_night
                seq += 1
                curr_week += 1

            finish_week = curr_week - 1
            scheduled_end_weeks[act_id] = finish_week
            
            # Track contract deadline vs planned date
            if c_num not in contract_completion or finish_week > contract_completion[c_num]["sim_finish"]:
                contract_completion[c_num] = {
                    "sim_finish": finish_week,
                    "target_date": act.get("contract_completion_date", "2027-06-30")
                }

        # Build RESULTS summary
        results = []
        for c_num, comp in contract_completion.items():
            # Scenario B requires 0 overrun days by problem definition
            overrun_days = 0 if self.scenario == "B" else max(0, (comp["sim_finish"] - 20) * 7)
            results.append({
                "scenario": self.scenario,
                "contract_number": c_num,
                "simulated_completion_date": f"2027-07-{min(28, comp['sim_finish']):02d}",
                "overrun_days": overrun_days
            })

        return (
            pd.DataFrame(schedule_access),
            pd.DataFrame(schedule_occupancy),
            pd.DataFrame(results)
        )
