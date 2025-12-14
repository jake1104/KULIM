use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, BufWriter};

// -----------------------------------------------------------------------------
// Scoring Constants
// -----------------------------------------------------------------------------
const COST_LONG_WORD: f64 = -40.0;
const COST_MEDIUM_WORD: f64 = -30.0;
const COST_SHORT_WORD: f64 = -5.0;
const PENALTY_SINGLE_VERB_IC: f64 = 20.0;
const COST_OOV: f64 = 50.0;
const BONUS_NOUN_2PLUS: f64 = 5.0;
const BONUS_ADVERB_2PLUS: f64 = 10.0;

const BONUS_NOUN_JOSA: f64 = 20.0;
const BONUS_VERB_EOMI: f64 = 15.0;
const BONUS_EOMI_EOMI: f64 = 10.0;
const BONUS_ADVERB_NOUN: f64 = 15.0;
const BONUS_ADVERB_VERB: f64 = 10.0;
const BONUS_DETERMINER_NOUN: f64 = 10.0;

const COST_CONJUGATION_BASE: f64 = -25.0;
const BONUS_CONJ_CONTEXT: f64 = 10.0;

// -----------------------------------------------------------------------------
// Data Structures
// -----------------------------------------------------------------------------
#[derive(Serialize, Deserialize, Debug, Clone)]
struct TriePattern {
    pos: String,
    lemma: String,
}

// Inner data struct that is Pure Rust and Serializable
#[derive(Serialize, Deserialize, Default)]
struct TrieData {
    dict: HashMap<String, Vec<TriePattern>>,
}

// PyO3 Wrapper
#[pyclass]
struct RustTrie {
    data: TrieData,
}

// -----------------------------------------------------------------------------
// Constraint Validator
// -----------------------------------------------------------------------------
fn is_valid_transition(prev_pos: &str, curr_pos: &str) -> bool {
    // Ported from constraints.py
    match (prev_pos, curr_pos) {
        ("JKS", "JKS") => false,
        ("JKO", "JKO") => false,
        ("EF", "JKS") => false,
        ("EF", "JKO") => false,
        ("EF", "EF") => false,
        ("SF", "JKS") => false,
        _ => true,
    }
}

#[pymethods]
impl RustTrie {
    #[new]
    fn new() -> Self {
        RustTrie {
            data: TrieData::default(),
        }
    }

    fn insert(&mut self, word: String, pos: String, lemma: String) {
        let entry = self.data.dict.entry(word).or_insert_with(Vec::new);
        if !entry.iter().any(|p| p.pos == pos && p.lemma == lemma) {
            entry.push(TriePattern { pos, lemma });
        }
    }

    fn exists(&self, word: String) -> bool {
        self.data.dict.contains_key(&word)
    }

    fn search(&self, word: String) -> Vec<(String, String)> {
        match self.data.dict.get(&word) {
            Some(patterns) => patterns.iter()
                .map(|p| (p.pos.clone(), p.lemma.clone()))
                .collect(),
            None => Vec::new(),
        }
    }
    
    fn search_batch(&self, words: Vec<String>) -> Vec<Vec<(String, String)>> {
         words.into_iter().map(|w| self.search(w)).collect()
    }

    fn get_stats(&self) -> (usize, usize) {
        let nodes = self.data.dict.len();
        let patterns = self.data.dict.values().map(|v| v.len()).sum();
        (nodes, patterns)
    }

    fn search_all_patterns(&self, text: String) -> Vec<(usize, usize, Vec<(String, String)>)> {
        let chars: Vec<char> = text.chars().collect();
        let n = chars.len();
        let mut results = Vec::new();

        for i in 0..n {
            for len in 1..=16 {
                if i + len > n {
                    break;
                }
                let sub: String = chars[i..i+len].iter().collect();
                if let Some(patterns) = self.data.dict.get(&sub) {
                    let pat_vec: Vec<(String, String)> = patterns.iter()
                        .map(|p| (p.pos.clone(), p.lemma.clone()))
                        .collect();
                    results.push((i, len, pat_vec));
                }
            }
        }
        results
    }

    fn analyze(&self, text: String) -> PyResult<Vec<(String, String, String)>> {
        let chars: Vec<char> = text.chars().collect();
        let n = chars.len();
        
        let mut dp = vec![f64::INFINITY; n + 1];
        let mut path: Vec<Option<(String, String, String, usize)>> = vec![None; n + 1];
        let mut prev_pos_table: Vec<Option<String>> = vec![None; n + 1];

        dp[0] = 0.0;

        for i in 0..n {
            if dp[i] == f64::INFINITY {
                continue;
            }
            
            let prev_pos = prev_pos_table[i].clone();
            let prev_pos_deref = prev_pos.as_deref();

            // 1. Dictionary Search
            for len in 1..=16 {
                if i + len > n {
                    break;
                }
                
                let j = i + len;
                let surface: String = chars[i..j].iter().collect();
                
                if let Some(patterns) = self.data.dict.get(&surface) {
                    for pat in patterns {
                        if let Some(pp) = prev_pos_deref {
                            if !is_valid_transition(pp, &pat.pos) {
                                continue;
                            }
                        }

                        let mut cost = match len {
                            l if l >= 3 => COST_LONG_WORD,
                            2 => COST_MEDIUM_WORD,
                            _ => COST_SHORT_WORD,
                        };

                        if len == 1 && (pat.pos.starts_with('V') || pat.pos == "IC") {
                            cost += PENALTY_SINGLE_VERB_IC;
                        }
                        if pat.pos.starts_with('N') && len >= 2 {
                            cost -= BONUS_NOUN_2PLUS;
                        }
                        if pat.pos == "MAG" && len >= 2 {
                            cost -= BONUS_ADVERB_2PLUS;
                        }

                        if let Some(pp) = prev_pos_deref {
                            if pp.starts_with('N') && pat.pos.starts_with('J') {
                                cost -= BONUS_NOUN_JOSA;
                            } else if pp.starts_with('V') && pat.pos.starts_with('E') {
                                cost -= BONUS_VERB_EOMI;
                            } else if pp.starts_with('E') && pat.pos.starts_with('E') {
                                cost -= BONUS_EOMI_EOMI;
                            } else if pp == "MAG" && pat.pos.starts_with('N') {
                                cost -= BONUS_ADVERB_NOUN;
                            } else if pp == "MAG" && pat.pos.starts_with('V') {
                                cost -= BONUS_ADVERB_VERB;
                            } else if pp == "MM" && pat.pos.starts_with('N') {
                                cost -= BONUS_DETERMINER_NOUN;
                            }
                        }

                        let total_cost = dp[i] + cost;
                        if total_cost < dp[j] {
                            dp[j] = total_cost;
                            path[j] = Some((surface.clone(), pat.pos.clone(), pat.lemma.clone(), i));
                            prev_pos_table[j] = Some(pat.pos.clone());
                        }
                    }
                }
                
                // 2. Simple Conjugation Heuristic
                // 2. Simple Conjugation Heuristic
                // (Removed: Standard Viterbi handles regular decomposition naturally)

            }

            // 3. OOV
            for len in 1..=1 {
                if i + len > n { break; }
                let j = i + len;
                let surface: String = chars[i..j].iter().collect();
                let cost = COST_OOV + (len as f64 * 10.0);
                
                let total_cost = dp[i] + cost;
                
                if total_cost < dp[j] {
                    dp[j] = total_cost;
                    path[j] = Some((surface, "NNG".to_string(), "UNKNOWN".to_string(), i));
                    prev_pos_table[j] = Some("NNG".to_string());
                }
            }
        }

        if dp[n] == f64::INFINITY {
            return Ok(Vec::new());
        }

        let mut results = Vec::new();
        let mut curr = n;
        while curr > 0 {
            if let Some((surf, pos, lemma, prev)) = &path[curr] {
                results.push((surf.clone(), pos.clone(), lemma.clone()));
                curr = *prev;
            } else {
                break;
            }
        }
        results.reverse();
        Ok(results)
    }
}

// -----------------------------------------------------------------------------
// Serialization Wrappers
// -----------------------------------------------------------------------------

#[pyfunction]
fn save_trie(trie: &RustTrie, path: String) -> PyResult<()> {
    let file = File::create(path).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let writer = BufWriter::new(file);
    // Serialize inner data
    bincode::serialize_into(writer, &trie.data).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(())
}

#[pyfunction]
fn load_trie(path: String) -> PyResult<RustTrie> {
    let file = File::open(path).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let reader = BufReader::new(file);
    let data: TrieData = bincode::deserialize_from(reader).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(RustTrie { data })
}

// -----------------------------------------------------------------------------
// Module Definition
// -----------------------------------------------------------------------------
#[pymodule]
fn kulim_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustTrie>()?;
    m.add_function(wrap_pyfunction!(save_trie, m)?)?;
    m.add_function(wrap_pyfunction!(load_trie, m)?)?;
    Ok(())
}
