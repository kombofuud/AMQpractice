#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <iomanip>
#include <cstdint>
#include <unordered_map>
#include <omp.h>

using namespace std;

// --- GAME CONFIGURATION ---
const int GRID_SIZE = 25;
const int RED_BONUS = 170;
const int TOTAL_BOARDS = 12650;

int SCORE_LUT[256] = {0};

void init_score_lut(int purple_score = 25) {
    SCORE_LUT['B'] = 5 + purple_score;   
    SCORE_LUT['T'] = 15 + purple_score;  
    SCORE_LUT['G'] = 30 + purple_score;  
    SCORE_LUT['Y'] = 50 + purple_score;  
    SCORE_LUT['O'] = 85 + purple_score;  
    SCORE_LUT['R'] = 145 + purple_score; 
    SCORE_LUT['P'] = purple_score;       
}

inline int get_score(char col) {
    return SCORE_LUT[(unsigned char)col];
}

const char COLOR_MAP[5] = {'B', 'T', 'G', 'Y', 'O'};

inline int color_to_idx(char c) {
    switch(c) {
        case 'B': return 0;
        case 'T': return 1;
        case 'G': return 2;
        case 'Y': return 3;
        case 'O': return 4;
        case 'P': return 5;
        default: return -1;
    }
}

const char IDX_TO_COLOR[6] = {'B', 'T', 'G', 'Y', 'O', 'P'};

vector<vector<int>> NEIGHBORS(GRID_SIZE);

void precompute_neighbors() {
    for (int r = 0; r < 5; ++r) {
        for (int c = 0; c < 5; ++c) {
            int idx = r * 5 + c;
            for (int dr = -1; dr <= 1; ++dr) {
                for (int dc = -1; dc <= 1; ++dc) {
                    if (dr == 0 && dc == 0) continue;
                    int nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < 5 && nc >= 0 && nc < 5) {
                        NEIGHBORS[idx].push_back(nr * 5 + nc);
                    }
                }
            }
        }
    }
}

struct Board {
    array<int, 4> purples;
    array<char, GRID_SIZE> grid;
};

vector<Board> ALL_BOARDS;

uint8_t CELL_COLOR_INDEX[TOTAL_BOARDS][GRID_SIZE];
uint32_t PURPLE_MASKS[TOTAL_BOARDS];

void precompute_boards() {
    precompute_neighbors();
    vector<bool> v(GRID_SIZE, false);
    fill(v.begin(), v.begin() + 4, true);

    int board_counter = 0;

    do {
        Board b;
        array<bool, GRID_SIZE> p_set{};
        int p_idx = 0;
        uint32_t p_mask = 0;

        for (int i = 0; i < GRID_SIZE; ++i) {
            if (v[i]) {
                b.purples[p_idx++] = i;
                p_set[i] = true;
                p_mask |= (1U << i);
            }
        }

        PURPLE_MASKS[board_counter] = p_mask;

        for (int i = 0; i < GRID_SIZE; ++i) {
            if (p_set[i]) {
                b.grid[i] = 'P';
            } else {
                int count = 0;
                for (int n : NEIGHBORS[i]) {
                    if (p_set[n]) count++;
                }
                b.grid[i] = COLOR_MAP[count];
            }
            CELL_COLOR_INDEX[board_counter][i] = color_to_idx(b.grid[i]);
        }

        ALL_BOARDS.push_back(b);
        board_counter++;
    } while (prev_permutation(v.begin(), v.end()));
}

string format_cell(int cell) {
    int r = cell / 5;
    int c = cell % 5;
    return "Cell " + to_string(cell) + " (" + to_string(r) + "," + to_string(c) + ")";
}

// --- STATE KEY & MEMOIZATION ---
struct StateKey {
    uint64_t board_hash;
    uint32_t packed_state; 

    bool operator==(const StateKey& other) const {
        return packed_state == other.packed_state && board_hash == other.board_hash;
    }
};

struct StateKeyHash {
    size_t operator()(const StateKey& k) const {
        uint64_t h = k.board_hash ^ (static_cast<uint64_t>(k.packed_state) * 0x9e3779b97f4a7c15ULL);
        return static_cast<size_t>(h);
    }
};

inline StateKey make_key(uint64_t board_hash, uint32_t revealed_mask, int remaining_clicks, int purples_found) {
    uint32_t packed = (revealed_mask & 0x1FFFFFFU) 
                    | (static_cast<uint32_t>(remaining_clicks & 0xF) << 25) 
                    | (static_cast<uint32_t>(purples_found & 0x7) << 29);
    return StateKey{board_hash, packed};
}

using MemoTable = unordered_map<StateKey, double, StateKeyHash>;

inline uint64_t compute_board_hash(const vector<int>& active_indices) {
    uint64_t h = 14695981039346656037ULL;
    for (int idx : active_indices) {
        h ^= static_cast<uint64_t>(idx);
        h *= 1099511628211ULL;
    }
    return h;
}

// Forward declaration
double solve_exact_recursive(
    const vector<int>& active_indices, 
    int remaining_clicks, 
    int purples_found, 
    uint32_t revealed_mask, 
    int purple_score,
    MemoTable& memo_table
);

// --- RESOLVE THREE PURPLES ---
double resolve_three_purples(
    const vector<int>& active_indices,
    int remaining_clicks,
    uint32_t current_revealed,
    int purple_score,
    MemoTable& memo_table
) {
    double total_ev = 0.0;
    int num_boards = active_indices.size();

    vector<int> boards_by_fourth[25];

    for (int idx : active_indices) {
        int fourth_p = -1;
        for (int p : ALL_BOARDS[idx].purples) {
            if (!(current_revealed & (1U << p))) {
                fourth_p = p;
                break;
            }
        }
        if (fourth_p != -1) {
            boards_by_fourth[fourth_p].push_back(idx);
        }
    }

    for (int fourth_p = 0; fourth_p < GRID_SIZE; ++fourth_p) {
        if (boards_by_fourth[fourth_p].empty()) continue;

        const auto& sub_indices = boards_by_fourth[fourth_p];
        int sub_count = sub_indices.size();
        uint32_t next_revealed = current_revealed | (1U << fourth_p);

        double group_ev = RED_BONUS + solve_exact_recursive(
            sub_indices, remaining_clicks - 1, 4, next_revealed, purple_score, memo_table
        );

        total_ev += group_ev * ((double)sub_count / num_boards);
    }

    return total_ev;
}

struct OutcomeGroup {
    int color_idx;
    vector<int> indices;
};

inline void get_color_outcomes(
    const vector<int>& active_indices, 
    int action, 
    vector<OutcomeGroup>& outcomes
) {
    outcomes.clear();
    vector<int> color_buckets[6];

    for (int idx : active_indices) {
        uint8_t c_idx = CELL_COLOR_INDEX[idx][action];
        color_buckets[c_idx].push_back(idx);
    }

    for (int c = 0; c < 6; ++c) {
        if (!color_buckets[c].empty()) {
            outcomes.push_back({c, move(color_buckets[c])});
        }
    }
}

// --- RECURSIVE EVALUATOR (THREAD-LOCAL MEMO TABLE) ---
double solve_exact_recursive(
    const vector<int>& active_indices, 
    int remaining_clicks, 
    int purples_found, 
    uint32_t revealed_mask, 
    int purple_score,
    MemoTable& memo_table
) {
    if (remaining_clicks <= 0 && purples_found < 4) return 0.0;

    int num_boards = active_indices.size();
    
    uint64_t b_hash = compute_board_hash(active_indices);
    StateKey key = make_key(b_hash, revealed_mask, remaining_clicks, purples_found);
    
    auto it = memo_table.find(key);
    if (it != memo_table.end()) return it->second;

    double accumulated_score = 0.0;
    int curr_purples = purples_found;
    uint32_t current_revealed = revealed_mask;

    // 1. O(1) Bitmask Guaranteed Purple Pre-Pass
    while (true) {
        int guaranteed_purple = -1;
        uint32_t unrevealed_mask = (~current_revealed) & 0x1FFFFFFU;
        
        for (int cell = 0; cell < GRID_SIZE; ++cell) {
            if (unrevealed_mask & (1U << cell)) {
                bool is_guaranteed = true;
                for (int idx : active_indices) {
                    if (!(PURPLE_MASKS[idx] & (1U << cell))) {
                        is_guaranteed = false;
                        break;
                    }
                }
                if (is_guaranteed) {
                    guaranteed_purple = cell;
                    break;
                }
            }
        }

        if (guaranteed_purple != -1) {
            accumulated_score += get_score('P');
            curr_purples++;
            current_revealed |= (1U << guaranteed_purple);

            if (curr_purples == 3) {
                accumulated_score += resolve_three_purples(
                    active_indices, remaining_clicks, current_revealed, purple_score, memo_table
                );
                memo_table[key] = accumulated_score;
                return accumulated_score;
            }
        } else {
            break;
        }
    }

    // 2. Deterministic Resolution (1 Board Left)
    if (num_boards == 1) {
        const auto& sample_grid = ALL_BOARDS[active_indices[0]].grid;
        vector<int> cell_vals;
        cell_vals.reserve(GRID_SIZE);

        uint32_t unrevealed = (~current_revealed) & 0x1FFFFFFU;
        for (int cell = 0; cell < GRID_SIZE; ++cell) {
            if (unrevealed & (1U << cell)) {
                cell_vals.push_back(get_score(sample_grid[cell]));
            }
        }
        sort(cell_vals.rbegin(), cell_vals.rend());

        int k = min((int)cell_vals.size(), remaining_clicks);
        for (int i = 0; i < k; ++i) accumulated_score += cell_vals[i];

        memo_table[key] = accumulated_score;
        return accumulated_score;
    }

    // 3. Four Purples Found Resolution
    if (curr_purples == 4) {
        double expected_greedy_score = 0.0;
        uint32_t unrevealed = (~current_revealed) & 0x1FFFFFFU;

        for (int idx : active_indices) {
            const auto& grid = ALL_BOARDS[idx].grid;
            vector<int> cell_vals;
            cell_vals.reserve(GRID_SIZE);

            for (int cell = 0; cell < GRID_SIZE; ++cell) {
                if (unrevealed & (1U << cell)) {
                    cell_vals.push_back(get_score(grid[cell]));
                }
            }
            sort(cell_vals.rbegin(), cell_vals.rend());

            int k = min((int)cell_vals.size(), remaining_clicks);
            double board_score = 0.0;
            for (int i = 0; i < k; ++i) board_score += cell_vals[i];
            expected_greedy_score += board_score;
        }

        accumulated_score += (expected_greedy_score / num_boards);
        memo_table[key] = accumulated_score;
        return accumulated_score;
    }

    // 4. Exact Expectimax Evaluation
    double best_action_ev = -1e9;
    vector<int> candidate_actions;
    candidate_actions.reserve(GRID_SIZE);

    int best_det_action = -1;
    double max_det_ev = -1.0;
    double max_nondet_1click_ev = -1.0;

    vector<OutcomeGroup> outcomes;

    for (int action = 0; action < GRID_SIZE; ++action) {
        if (current_revealed & (1U << action)) continue;

        get_color_outcomes(active_indices, action, outcomes);

        if (outcomes.size() == 1 && outcomes[0].color_idx != 5) {
            double score = get_score(IDX_TO_COLOR[outcomes[0].color_idx]);
            if (score > max_det_ev) {
                max_det_ev = score;
                best_det_action = action;
            }
        } else {
            candidate_actions.push_back(action);

            double immediate_ev = 0.0;
            for (const auto& grp : outcomes) {
                double prob = (double)grp.indices.size() / num_boards;
                immediate_ev += prob * get_score(IDX_TO_COLOR[grp.color_idx]);
            }

            if (immediate_ev > max_nondet_1click_ev) {
                max_nondet_1click_ev = immediate_ev;
            }
        }
    }

    if (best_det_action != -1) {
        if (candidate_actions.empty() || max_det_ev > max_nondet_1click_ev) {
            candidate_actions.push_back(best_det_action);
        }
    }

    for (int action : candidate_actions) {
        get_color_outcomes(active_indices, action, outcomes);

        double action_ev = 0.0;

        for (const auto& grp : outcomes) {
            char color = IDX_TO_COLOR[grp.color_idx];
            const auto& matching_indices = grp.indices;

            double prob = (double)matching_indices.size() / num_boards;
            uint32_t next_revealed = current_revealed | (1U << action);

            double outcome_ev = 0.0;

            if (color == 'P') {
                int next_purples = curr_purples + 1;
                
                if (next_purples == 3) {
                    outcome_ev = get_score('P') + resolve_three_purples(
                        matching_indices, remaining_clicks, next_revealed, purple_score, memo_table
                    );
                } else {
                    outcome_ev = get_score('P') + solve_exact_recursive(
                        matching_indices, remaining_clicks, next_purples, next_revealed, purple_score, memo_table
                    );
                }
            } else {
                outcome_ev = get_score(color) + solve_exact_recursive(
                    matching_indices, remaining_clicks - 1, curr_purples, next_revealed, purple_score, memo_table
                );
            }

            action_ev += prob * outcome_ev;
        }

        if (action_ev > best_action_ev) best_action_ev = action_ev;
    }

    double final_ev = accumulated_score + best_action_ev;
    memo_table[key] = final_ev;
    return final_ev;
}

// --- MINIMALIST MAIN CLI RUNNER (TIED MOVES + PURPLE STATUS ANALYSIS) ---
int main(int argc, char* argv[]) {
    if (argc < 1) return 1;

    int purple_score = 25;
    init_score_lut(purple_score);
    precompute_boards();

    int total_clicks = 7;
    uint32_t revealed_mask = 0;

    vector<int> active_indices(TOTAL_BOARDS);
    iota(active_indices.begin(), active_indices.end(), 0);

    int clicks_used = 0;
    int purples_found = 0;
    double base_accumulated_score = 0.0;

    bool evaluate_target_cell_only = ((argc - 1) % 2 != 0);
    int target_cell = -1;

    int parse_until = argc;
    if (evaluate_target_cell_only) {
        target_cell = atoi(argv[argc - 1]);
        parse_until = argc - 1;
    }

    // Process move history
    vector<string> history_tokens;
    for (int i = 1; i < parse_until; i += 2) {
        int cell = atoi(argv[i]);
        char color = argv[i + 1][0];

        revealed_mask |= (1U << cell);
        int cell_score = get_score(color);
        base_accumulated_score += cell_score;

        if (color == 'P') {
            purples_found++;
        } else {
            clicks_used++;
        }

        int c_idx = color_to_idx(color);
        vector<int> next_active;
        for (int idx : active_indices) {
            if (CELL_COLOR_INDEX[idx][cell] == c_idx) {
                next_active.push_back(idx);
            }
        }
        active_indices = move(next_active);
        history_tokens.push_back(to_string(cell) + ":" + color);
    }

    int remaining_clicks = total_clicks - clicks_used;

    if (active_indices.empty()) {
        cout << "[Error] Invalid sequence: 0 candidate boards match this history.\n";
        return 0;
    }

    // --- ANALYZE GUARANTEED & POTENTIAL PURPLES ---
    vector<int> guaranteed_purples;
    vector<int> potential_purples;
    int num_active = active_indices.size();

    for (int cell = 0; cell < GRID_SIZE; ++cell) {
        if (revealed_mask & (1U << cell)) continue; // Skip already revealed cells

        int purple_count = 0;
        for (int idx : active_indices) {
            if (PURPLE_MASKS[idx] & (1U << cell)) {
                purple_count++;
            }
        }

        if (purple_count == num_active) {
            guaranteed_purples.push_back(cell);
        } else if (purple_count > 0) {
            potential_purples.push_back(cell);
        }
    }

    auto start_time = chrono::high_resolution_clock::now();

    // MODE 1: Target Single Specific Cell
    if (evaluate_target_cell_only) {
        if (revealed_mask & (1U << target_cell)) {
            cout << "[Error] Cell " << target_cell << " is already revealed.\n";
            return 1;
        }

        vector<OutcomeGroup> outcomes;
        get_color_outcomes(active_indices, target_cell, outcomes);

        double weighted_ev = 0.0;
        int total_boards = active_indices.size();

        for (const auto& grp : outcomes) {
            char color = IDX_TO_COLOR[grp.color_idx];
            const auto& matching_indices = grp.indices;

            double prob = (double)matching_indices.size() / total_boards;
            uint32_t next_revealed = revealed_mask | (1U << target_cell);

            MemoTable local_memo;
            local_memo.reserve(50000);

            double outcome_ev = 0.0;
            if (color == 'P') {
                int next_purples = purples_found + 1;
                if (next_purples == 3) {
                    outcome_ev = get_score('P') + resolve_three_purples(
                        matching_indices, remaining_clicks, next_revealed, purple_score, local_memo
                    );
                } else {
                    outcome_ev = get_score('P') + solve_exact_recursive(
                        matching_indices, remaining_clicks, next_purples, next_revealed, purple_score, local_memo
                    );
                }
            } else {
                outcome_ev = get_score(color) + solve_exact_recursive(
                    matching_indices, remaining_clicks - 1, purples_found, next_revealed, purple_score, local_memo
                );
            }

            weighted_ev += prob * (base_accumulated_score + outcome_ev);
        }

        auto end_time = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = end_time - start_time;

        cout << "Target Cell : " << target_cell << "\n";
        cout << "Target EV   : " << fixed << setprecision(2) << weighted_ev << "\n";
        cout << "Time        : " << setprecision(3) << elapsed.count() << "s\n";
    } 
    // MODE 2: Search Candidate Next Moves
    else {
        vector<int> unrevealed;
        for (int i = 0; i < GRID_SIZE; ++i) {
            if (!(revealed_mask & (1U << i))) unrevealed.push_back(i);
        }

        int n_candidates = unrevealed.size();
        vector<double> candidate_results(n_candidates, 0.0);

        #pragma omp parallel for schedule(dynamic)
        for (int i = 0; i < n_candidates; ++i) {
            int candidate = unrevealed[i];
            
            MemoTable thread_memo;
            thread_memo.reserve(50000);

            vector<OutcomeGroup> thread_outcomes;
            get_color_outcomes(active_indices, candidate, thread_outcomes);

            double move_ev = 0.0;

            for (const auto& grp : thread_outcomes) {
                char color = IDX_TO_COLOR[grp.color_idx];
                const auto& matching_indices = grp.indices;
                double prob = (double)matching_indices.size() / num_active;

                uint32_t next_revealed = revealed_mask | (1U << candidate);

                double outcome_ev = 0.0;
                if (color == 'P') {
                    int next_purples = purples_found + 1;
                    if (next_purples == 3) {
                        outcome_ev = get_score('P') + resolve_three_purples(
                            matching_indices, remaining_clicks, next_revealed, purple_score, thread_memo
                        );
                    } else {
                        outcome_ev = get_score('P') + solve_exact_recursive(
                            matching_indices, remaining_clicks, next_purples, next_revealed, purple_score, thread_memo
                        );
                    }
                } else {
                    outcome_ev = get_score(color) + solve_exact_recursive(
                        matching_indices, remaining_clicks - 1, purples_found, next_revealed, purple_score, thread_memo
                    );
                }

                move_ev += prob * outcome_ev;
            }

            candidate_results[i] = base_accumulated_score + move_ev;
        }

        // Find highest EV across candidates
        double best_overall_ev = -1e9;
        for (int i = 0; i < n_candidates; ++i) {
            if (candidate_results[i] > best_overall_ev) {
                best_overall_ev = candidate_results[i];
            }
        }

        // Collect all tied optimal moves
        vector<int> best_moves;
        const double EPSILON = 1e-4;
        for (int i = 0; i < n_candidates; ++i) {
            if (abs(candidate_results[i] - best_overall_ev) < EPSILON) {
                best_moves.push_back(unrevealed[i]);
            }
        }

        auto end_time = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = end_time - start_time;

        // --- CLEAN MINIMALIST OUTPUT ---
        cout << "History   : ";
        if (history_tokens.empty()) cout << "[Start]";
        else {
            for (size_t i = 0; i < history_tokens.size(); ++i) {
                cout << history_tokens[i] << (i + 1 < history_tokens.size() ? " " : "");
            }
        }
        cout << "\nBoards    : " << num_active;

        // Guaranteed Purples Output
        cout << "\nGuaranteed: ";
        if (guaranteed_purples.empty()) {
            cout << "None";
        } else {
            for (size_t i = 0; i < guaranteed_purples.size(); ++i) {
                cout << guaranteed_purples[i] << (i + 1 < guaranteed_purples.size() ? ", " : "");
            }
        }

        // Potential Purples Output
        cout << "\nPotential : ";
        if (potential_purples.empty()) {
            cout << "None";
        } else {
            for (size_t i = 0; i < potential_purples.size(); ++i) {
                cout << potential_purples[i] << (i + 1 < potential_purples.size() ? ", " : "");
            }
        }
        
        // Best Move Recommendation
        cout << "\nBest Move : ";
        if (best_moves.size() == 1) {
            cout << "Cell " << best_moves[0];
        } else {
            cout << "Cells ";
            for (size_t i = 0; i < best_moves.size(); ++i) {
                cout << best_moves[i] << (i + 1 < best_moves.size() ? ", " : "");
            }
        }

        cout << "\nMax EV    : " << fixed << setprecision(2) << best_overall_ev;
        cout << "\nTime      : " << setprecision(3) << elapsed.count() << "s\n";
    }
    return 0;
}