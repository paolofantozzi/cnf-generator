# -*- coding: utf-8 -*-

"""CNF related classes."""

from dataclasses import dataclass
from itertools import chain
from string import ascii_letters
from string import digits
from typing import FrozenSet
from typing import Iterator
from typing import Set
from typing import Union

from .exceptions import SymbolNotAllowed

CONJUCTION_SYMBOL = '&'
DISJUCTION_SYMBOL = '|'
NEGATED_SYMBOL = '!'
NOT_ALLOWED_SYMBOLS = frozenset((CONJUCTION_SYMBOL, DISJUCTION_SYMBOL, NEGATED_SYMBOL))
STD_SYMBOLS = frozenset(ascii_letters + digits)


@dataclass(frozen=True)
class Literal:
    """Represent a literal in a cnf formula."""

    symbol: str
    is_negated: bool = False

    def __post_init__(self):
        """Raise an exception if the symbol is not allowed."""
        if self.symbol.startswith(NEGATED_SYMBOL):
            object.__setattr__(self, 'symbol', self.symbol.replace(NEGATED_SYMBOL, ''))  # noqa: WPS609
            object.__setattr__(self, 'is_negated', True)  # noqa: WPS425,WPS609
        if (not self.symbol) or (self.symbol in NOT_ALLOWED_SYMBOLS):
            raise SymbolNotAllowed(f'Symbol {self.symbol} not allowed for literal.')

    def __str__(self) -> str:
        """Return the str representation of the literal."""
        negated = ''
        if self.is_negated:
            negated = NEGATED_SYMBOL
        return f'{negated}{self.symbol}'

    def __hash__(self):
        """Hash of the attributes."""
        return hash(self.symbol) ^ hash(self.is_negated)


@dataclass(frozen=True)
class Clause:
    """Represent a clause in a cnf formula."""

    literals: FrozenSet[Literal]

    def __init__(self, literals: Set[Literal]):
        """Save the frozenset."""
        object.__setattr__(self, 'literals', frozenset(literals))  # noqa: WPS609

    def __str__(self) -> str:
        """Return the str representation of the clause."""
        return DISJUCTION_SYMBOL.join(str(literal) for literal in self.literals)

    @property
    def symbols(self):
        """Return all the symbols in clause."""
        yield from (literal.symbol for literal in self.literals)

    def __hash__(self):
        """Return directly the hash of the frozenset."""
        return hash(self.literals)


@dataclass(frozen=True)
class CNF:
    """Represent a cnf formula."""

    clauses: FrozenSet[Clause]

    def __init__(self, clauses: Union[Set[Clause], FrozenSet[Clause]]):
        """Save the frozenset."""
        object.__setattr__(self, 'clauses', frozenset(clauses))  # noqa: WPS609

    @property
    def literals(self):
        """Iterate through literals over all the clauses."""
        yield from chain.from_iterable(clause.literals for clause in self.clauses)

    def filtered_clauses_by_literals(self, included: Set[Literal], excluded: Set[Literal]) -> Iterator[Clause]:
        """Iterate through clauses filtering by literals."""
        included_set = set(included)
        excluded_set = set(excluded)
        for clause in self.clauses:
            if not (clause.literals & included_set):
                continue
            if clause.literals & excluded_set:
                continue
            yield clause

    def filtered_clauses_by_symbols(self, included: Set[str], excluded: Set[str]) -> Iterator[Clause]:
        """Iterate through clauses filtering by symbols."""
        included_set = set(included)
        excluded_set = set(excluded)
        for clause in self.clauses:
            if not (set(clause.symbols) & included_set):
                continue
            if set(clause.symbols) & excluded_set:
                continue
            yield clause

    def __str__(self) -> str:
        """Return the str representation of the formula."""
        return CONJUCTION_SYMBOL.join(str(clause) for clause in self.clauses)

    def __hash__(self):
        """Return directly the hash of the frozenset."""
        return hash(self.clauses)
