# -*- coding: utf-8 -*-

"""Implementation of the isomorphic cnf generation."""

from random import randint
from random import shuffle
from typing import Dict
from typing import List

from .cnf import CNF
from .cnf import STD_SYMBOLS
from .cnf import Clause
from .cnf import Literal


def _map_literal(old_literal: Literal, symbols_mapping: Dict[str, str], inversion_mapping: Dict[str, bool]):
    """Return a new literal using mappings."""
    return Literal(
        symbol=symbols_mapping.get(old_literal.symbol, old_literal.symbol),
        is_negated=inversion_mapping.get(old_literal.symbol, False) ^ old_literal.is_negated,
    )


def cnf_isomorphic_generator(original_cnf: CNF, new_symbols: List[str] = None, monotone: bool = False, **kwargs) -> CNF:
    """Return a new cnf isomorph to the original."""
    old_symbols_set = {literal.symbol for literal in original_cnf.literals}
    old_symbols = list(old_symbols_set)

    new_symbols = new_symbols or list(STD_SYMBOLS)
    new_symbols = new_symbols[:]
    shuffle(new_symbols)

    mapping = {old_s: new_s for old_s, new_s in zip(old_symbols, new_symbols)}
    inverted = {}
    if not monotone:
        inverted = {old_s: bool(randint(0, 1)) for old_s in mapping}

    clauses = set()
    for old_clause in original_cnf.clauses:
        this_clause_literals = {_map_literal(old_literal, mapping, inverted) for old_literal in old_clause.literals}
        clauses.add(Clause(this_clause_literals))

    return CNF(clauses)
