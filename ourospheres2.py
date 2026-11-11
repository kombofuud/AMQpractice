import itertools
import time

# --- GAME CONFIGURATION ---
BASE_SCORES = {
    'B': 5,    # 0 purples nearby
    'T': 15,   # 1 purple nearby
    'G': 30,   # 2 purples nearby
    'Y': 50,   # 3 purples nearby
    'O': 85,   # 4 purples nearby
    'R': 145,  # Auto-revealed 4th purple (Red bonus)
    'P': 5     # Standard purple tile score
}

COLOR_MAP = {0: 'B', 1: 'T', 2: 'G', 3: 'Y', 4: 'O'}

def get_neighbors(r, c):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                neighbors.append(nr * 5 + nc)
    return neighbors

NEIGHBORS = [get_neighbors(r, c) for r in range(5) for c in range(5)]

def precompute_boards():
    """Precomputes all 12,650 valid board configurations."""
    boards = []
    for purples in itertools.combinations(range(25), 4):
        p_set = set(purples)
        grid = [
            'P' if idx in p_set else COLOR_MAP[sum(1 for n in NEIGHBORS[idx] if n in p_set)]
            for idx in range(25)
        ]
        boards.append((frozenset(purples), tuple(grid)))
    return tuple(boards)

ALL_BOARDS = precompute_boards()

# Unique opening squares for a pristine 5x5 grid
UNIQUE_OPENING_SQUARES = {
    0: "Corner (0,0)",
    1: "Edge-1 (0,1)",
    2: "Edge-Center (0,2)",
    6: "Inner-Corner (1,1)",
    7: "Inner-Edge (1,2)",
    12: "Center (2,2)"
}


# --- BACKWARD INDUCTION SOLVER ---
class BackwardInductionSolver:
    def __init__(self, purple_score=5):
        self.scores = dict(BASE_SCORES)
        self.scores['P'] = purple_score
        
        # Transposition Tables: state_key -> exact max EV
        self.memo_phase2 = {} # For 2-purple states
        self.memo_phase1 = {} # For 1-purple states

    def _get_consistent_indices(self, history):
        history_items = tuple(sorted(history.items()))
        return tuple(
            idx for idx, (_, grid) in enumerate(ALL_BOARDS)
            if all(grid[c] == col for c, col in history_items)
        )

    def _state_key(self, history, remaining_clicks):
        return (frozenset(history.items()), remaining_clicks)

    # --- TERMINAL EVALUATION ---
    def _evaluate_terminal_or_cascade(self, board_indices, remaining_clicks, history, purples_found):
        """
        Handles guaranteed purple pre-pass, Red cascade auto-triggers,
        and greedy deterministic score computation.
        """
        if remaining_clicks <= 0:
            return 0.0

        curr_history = dict(history)
        curr_revealed = set(curr_history.keys())
        unrevealed = [c for c in range(25) if c not in curr_revealed]
        accumulated_score = 0.0
        curr_purples = purples_found

        # Deterministic Pre-Pass: Take free guaranteed purples
        while True:
            guaranteed_purple = None
            for cell in unrevealed:
                if all(ALL_BOARDS[idx][1][cell] == 'P' for idx in board_indices):
                    guaranteed_purple = cell
                    break

            if guaranteed_purple is not None:
                accumulated_score += self.scores['P']
                curr_purples += 1
                curr_revealed.add(guaranteed_purple)
                unrevealed.remove(guaranteed_purple)

                if curr_purples == 3:
                    sample_p_set = ALL_BOARDS[board_indices[0]][0]
                    fourth_purple = list(sample_p_set - curr_revealed)[0]
                    accumulated_score += self.scores['R']
                    curr_purples = 4
                    curr_revealed.add(fourth_purple)
                    if fourth_purple in unrevealed:
                        unrevealed.remove(fourth_purple)
                    break
            else:
                break

        # If 4 purples found or 1 board remains, solve greedily
        if curr_purples == 4 or len(board_indices) == 1:
            sample_grid = ALL_BOARDS[board_indices[0]][1]
            cell_vals = sorted([self.scores[sample_grid[c]] for c in unrevealed], reverse=True)
            return accumulated_score + sum(cell_vals[:remaining_clicks])

        return None # Not fully resolved deterministically

    # --- PHASE 1: SOLVE STATES WITH 2 PURPLES FOUND ---
    def solve_state_2_purples(self, board_indices, remaining_clicks, history):
        key = self._state_key(history, remaining_clicks)
        if key in self.memo_phase2:
            return self.memo_phase2[key]

        # Check deterministic resolution
        det_val = self._evaluate_terminal_or_cascade(board_indices, remaining_clicks, history, purples_found=2)
        if det_val is not None:
            self.memo_phase2[key] = det_val
            return det_val

        unrevealed = [c for c in range(25) if c not in history]
        num_boards = len(board_indices)
        best_action_ev = -float('inf')

        for action in unrevealed:
            # Group outcomes by color
            outcomes = {}
            for idx in board_indices:
                color = ALL_BOARDS[idx][1][action]
                outcomes.setdefault(color, []).append(idx)

            action_ev = 0.0
            for color, matching_indices in outcomes.items():
                prob = len(matching_indices) / num_boards
                next_history = dict(history)
                next_history[action] = color

                if color == 'P':
                    # 3rd purple hit -> Red cascade auto-trigger!
                    sample_p_set = ALL_BOARDS[matching_indices[0]][0]
                    found_p = {c for c, col in next_history.items() if col == 'P'}
                    fourth_p = list(sample_p_set - found_p)[0]
                    next_history[fourth_p] = 'R'

                    # Pure deterministic score remainder
                    sample_grid = ALL_BOARDS[matching_indices[0]][1]
                    unrev_cells = [c for c in range(25) if c not in next_history]
                    top_vals = sorted([self.scores[sample_grid[c]] for c in unrev_cells], reverse=True)
                    
                    outcome_ev = self.scores['P'] + self.scores['R'] + sum(top_vals[:remaining_clicks])
                else:
                    outcome_ev = self.scores[color] + self.solve_state_2_purples(
                        tuple(matching_indices), remaining_clicks - 1, next_history
                    )

                action_ev += prob * outcome_ev

            if action_ev > best_action_ev:
                best_action_ev = action_ev

        self.memo_phase2[key] = best_action_ev
        return best_action_ev

    # --- PHASE 2: SOLVE STATES WITH 1 PURPLE FOUND ---
    def solve_state_1_purple(self, board_indices, remaining_clicks, history):
        key = self._state_key(history, remaining_clicks)
        if key in self.memo_phase1:
            return self.memo_phase1[key]

        det_val = self._evaluate_terminal_or_cascade(board_indices, remaining_clicks, history, purples_found=1)
        if det_val is not None:
            self.memo_phase1[key] = det_val
            return det_val

        unrevealed = [c for c in range(25) if c not in history]
        num_boards = len(board_indices)
        best_action_ev = -float('inf')

        for action in unrevealed:
            outcomes = {}
            for idx in board_indices:
                color = ALL_BOARDS[idx][1][action]
                outcomes.setdefault(color, []).append(idx)

            action_ev = 0.0
            for color, matching_indices in outcomes.items():
                prob = len(matching_indices) / num_boards
                next_history = dict(history)
                next_history[action] = color

                if color == 'P':
                    # HALT BRANCH: Transits to Phase 1 (2 purples found)!
                    outcome_ev = self.scores['P'] + self.solve_state_2_purples(
                        tuple(matching_indices), remaining_clicks, next_history
                    )
                else:
                    outcome_ev = self.scores[color] + self.solve_state_1_purple(
                        tuple(matching_indices), remaining_clicks - 1, next_history
                    )

                action_ev += prob * outcome_ev

            if action_ev > best_action_ev:
                best_action_ev = action_ev

        self.memo_phase1[key] = best_action_ev
        return best_action_ev

    # --- PHASE 3: SOLVE 0 PURPLES (OPENING MOVE EVALUATION) ---
    def solve_opening_moves(self, total_clicks=7):
        print(f"\n--- BACKWARD INDUCTION OPENING EVALUATION (Clicks = {total_clicks}) ---")
        print(f"{'Cell Index':<12} | {'Position Type':<18} | {'Exact Mathematical EV':<22} | {'Prob of Purple':<15}")
        print("-" * 75)

        total_boards = len(ALL_BOARDS)
        results = []

        for cell, label in UNIQUE_OPENING_SQUARES.items():
            outcomes = {}
            for idx, (_, grid) in enumerate(ALL_BOARDS):
                color = grid[cell]
                outcomes.setdefault(color, []).append(idx)

            exact_ev = 0.0
            prob_purple = len(outcomes.get('P', [])) / total_boards

            for color, matching_indices in outcomes.items():
                prob = len(matching_indices) / total_boards
                history = {cell: color}

                if color == 'P':
                    # Transits directly to Phase 2 (1 purple found)
                    branch_ev = self.scores['P'] + self.solve_state_1_purple(
                        tuple(matching_indices), total_clicks, history
                    )
                else:
                    # Transits to 0-purple sub-tree
                    branch_ev = self.scores[color] + self.solve_state_0_purples(
                        tuple(matching_indices), total_clicks - 1, history
                    )

                exact_ev += prob * branch_ev

            results.append((exact_ev, cell, label, prob_purple))

        results.sort(reverse=True, key=lambda x: x[0])

        for ev, cell, label, p_purple in results:
            print(f"{cell:<12} | {label:<18} | {ev:<22.4f} | {p_purple*100:<14.1f}%")

        best_cell = results[0][1]
        r, c = divmod(best_cell, 5)
        print(f"\nDefinitive Mathematical Optimal Opening Move: Cell {best_cell} ({r}, {c})")
        return results

    def solve_state_0_purples(self, board_indices, remaining_clicks, history):
        det_val = self._evaluate_terminal_or_cascade(board_indices, remaining_clicks, history, purples_found=0)
        if det_val is not None:
            return det_val

        unrevealed = [c for c in range(25) if c not in history]
        num_boards = len(board_indices)
        best_action_ev = -float('inf')

        for action in unrevealed:
            outcomes = {}
            for idx in board_indices:
                color = ALL_BOARDS[idx][1][action]
                outcomes.setdefault(color, []).append(idx)

            action_ev = 0.0
            for color, matching_indices in outcomes.items():
                prob = len(matching_indices) / num_boards
                next_history = dict(history)
                next_history[action] = color

                if color == 'P':
                    # Transits to Phase 2 (1 purple found)!
                    outcome_ev = self.scores['P'] + self.solve_state_1_purple(
                        tuple(matching_indices), remaining_clicks, next_history
                    )
                else:
                    outcome_ev = self.scores[color] + self.solve_state_0_purples(
                        tuple(matching_indices), remaining_clicks - 1, next_history
                    )

                action_ev += prob * outcome_ev

            if action_ev > best_action_ev:
                best_action_ev = action_ev

        return best_action_ev


# --- EXECUTION ---
if __name__ == "__main__":
    start_time = time.time()
    solver = BackwardInductionSolver(purple_score=5)
    solver.solve_opening_moves(total_clicks=7)
    print(f"\nExecution Time: {time.time() - start_time:.2f} seconds")