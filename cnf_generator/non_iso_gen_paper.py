# -*- coding: utf-8 -*-

"""Implementation of the non isomorphic cnf generation from the paper."""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

from .cnf import CNF
from .cnf import Clause
from .cnf import Literal
from .exceptions import GenerationFailedException
from .exceptions import NoSymbolsOrderException
from .iso_gen import cnf_isomorphic_generator


@dataclass
class LiteralCounter:
    """Represent a counter for both positive and negated literal."""

    pos_counter: int = 0
    neg_counter: int = 0

    @property
    def counter(self):
        """Return the total counter of a literal."""
        return self.pos_counter + self.neg_counter


class CardinalityRepository:
    """Represent all the info about cardinalities of a cnf."""

    def __init__(self, cnf: CNF):
        """Build the cardinalities."""
        self.counters: Dict[str, LiteralCounter] = defaultdict(LiteralCounter)
        for literal in cnf.literals:
            lit_count = self.counters[literal.symbol]
            if literal.is_negated:
                lit_count.neg_counter += 1
            else:
                lit_count.pos_counter += 1
        self.clauses_index = defaultdict(set)
        for clause in cnf.clauses:
            for literal in clause.literals:  # noqa: WPS440
                self.clauses_index[(literal.symbol, literal.is_negated)].add(clause)

    def clauses(self, symbol, negated=None):
        """Return the set of clauses that contains the symbol."""
        if negated is None:
            return self.clauses_index[(symbol, True)] | self.clauses_index[(symbol, False)]
        return self.clauses_index[(symbol, bool(negated))]

    def literal_count(self, literal):
        """Return the cardinality of the literal."""
        if literal.is_negated:
            return self.counters[literal.symbol].neg_counter
        return self.counters[literal.symbol].pos_counter

    def vec_space(self, clauses, literal):
        """Return the list of tuples (sorted by cardinality) of cardinality vector space excluding the literal."""
        space = []
        space_clauses = []
        for clause in clauses:
            all_counts = (self.literal_count(lit) for lit in clause.literals if lit != literal)
            t_lit = tuple(sorted(all_counts))
            space.append(t_lit)
            space_clauses.append(clause)
        return space, space_clauses


def _correct_order_of_symbols(  # noqa: WPS212,WPS231
    a_sym: str,
    b_sym: str,
    a_count: LiteralCounter,
    b_count: LiteralCounter,
) -> Tuple[Literal, Literal]:
    """Return the correct order of a pair of counters, raising an exception if there are no one."""
    ap = a_count.pos_counter
    an = a_count.neg_counter
    bp = b_count.pos_counter
    bn = b_count.neg_counter
    if   (0 < bp < ap) and (an == bn):  # noqa: E271,WPS223
        return Literal(a_sym), Literal(b_sym)
    elif (0 < ap < bp) and (an == bn):
        return Literal(b_sym), Literal(a_sym)
    elif (0 < bn < an) and (ap == bp):
        return Literal(a_sym, is_negated=True), Literal(b_sym, is_negated=True)
    elif (0 < an < bn) and (ap == bp):
        return Literal(b_sym, is_negated=True), Literal(a_sym, is_negated=True)
    elif (0 < bp < an) and (ap == bn):
        return Literal(a_sym, is_negated=True), Literal(b_sym)
    elif (0 < an < bp) and (ap == bn):
        return Literal(b_sym), Literal(a_sym, is_negated=True)
    elif (0 < bn < ap) and (an == bp):
        return Literal(a_sym), Literal(b_sym, is_negated=True)
    elif (0 < ap < bn) and (an == bp):
        return Literal(b_sym, is_negated=True), Literal(a_sym)
    raise NoSymbolsOrderException


def _swappable_pair_of_literals(  # noqa: WPS231
    cnf: CNF,
    repository: CardinalityRepository,
) -> Iterator[Tuple[Literal, Literal, Clause]]:
    """Iterate through the pair of literals that could be swapped."""
    symbols = set(repository.counters.keys())
    for a_sym, b_sym in combinations(symbols, 2):
        a_count = repository.counters[a_sym]
        b_count = repository.counters[b_sym]

        try:
            alpha, beta = _correct_order_of_symbols(a_sym, b_sym, a_count, b_count)
        except NoSymbolsOrderException:
            continue

        c_alpha = set(cnf.filtered_clauses_by_literals(included={alpha}, excluded={beta}))
        c_beta = set(cnf.filtered_clauses_by_literals(included={beta}, excluded={alpha}))
        if (not c_alpha) or (not c_beta):
            continue

        v_alpha, v_clauses_alpha = repository.vec_space(c_alpha, alpha)
        v_beta, _ = repository.vec_space(c_beta, beta)
        v_alpha_non_beta = set(v_alpha) - set(v_beta)
        if not v_alpha_non_beta:
            continue

        v_alpha_non_beta_single = v_alpha_non_beta.pop()
        u_clause_idx = v_alpha.index(v_alpha_non_beta_single)
        u_clause = v_clauses_alpha[u_clause_idx]

        yield alpha, beta, u_clause


def non_trivial_non_isomorphic_cnf_generator(original_cnf: CNF, isomorphic_to_result=True, **kwargs) -> CNF:
    """Return a new cnf generated by using the paper algorithm."""
    cardinalities = CardinalityRepository(original_cnf)
    for alpha, beta, u_clause in _swappable_pair_of_literals(original_cnf, cardinalities):
        alpha_count = cardinalities.literal_count(alpha)
        beta_count = cardinalities.literal_count(beta)
        delta = alpha_count - beta_count

        c_alpha = set(original_cnf.filtered_clauses_by_literals(included={alpha}, excluded={beta}))
        to_change: List[Clause] = list(c_alpha - {u_clause})[:delta]
        changed = set()
        for clause in to_change:
            literals = set(clause.literals)
            literals.remove(alpha)
            literals.add(beta)
            changed.add(Clause(literals))
        cnf = CNF((original_cnf.clauses - set(to_change)) | changed)

        if isomorphic_to_result:
            return cnf_isomorphic_generator(cnf)  # we return an isomorphic cnf to obfuscate the changes
        return cnf
    raise GenerationFailedException
