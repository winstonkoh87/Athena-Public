"""
schema_ssot.py — Single-Source-of-Truth (SSOT) Relational Schema & Invariant Compiler (TD-078)
================================================================================================
Universal engine for academic and consulting deliverables requiring relational data models,
functional dependencies, BCNF validation, data dictionaries, ERDs, and cross-table invariant checks.

Resolves TD-078: Eliminates silent drift between text tables, relational models, and diagram runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FunctionalDependency:
    """Represents a functional dependency X -> Y."""
    lhs: list[str]
    rhs: list[str]

    def __post_init__(self) -> None:
        self.lhs = sorted(set(self.lhs))
        self.rhs = sorted(set(self.rhs))


@dataclass
class RelationSchema:
    """Represents a relational schema R(A1, A2, ..., An) with keys and constraints."""
    name: str
    attributes: list[str]
    primary_key: list[str]
    fds: list[FunctionalDependency] = field(default_factory=list)
    foreign_keys: dict[str, tuple[str, str]] = field(default_factory=dict)  # col -> (TargetTable, TargetCol)
    types: dict[str, str] = field(default_factory=dict)
    nullable: dict[str, bool] = field(default_factory=dict)
    descriptions: dict[str, str] = field(default_factory=dict)

    def compute_closure(self, attributes_subset: set[str]) -> set[str]:
        """Compute the attribute closure X+ under the declared functional dependencies."""
        closure = set(attributes_subset)
        changed = True
        while changed:
            changed = False
            for fd in self.fds:
                lhs_set = set(fd.lhs)
                rhs_set = set(fd.rhs)
                if lhs_set.issubset(closure) and not rhs_set.issubset(closure):
                    closure.update(rhs_set)
                    changed = True
        return closure

    def is_superkey(self, attributes_subset: set[str]) -> bool:
        """Return True if attributes_subset functionally determines all attributes in the relation."""
        return self.compute_closure(attributes_subset) == set(self.attributes)

    def check_bcnf_violations(self) -> list[FunctionalDependency]:
        """
        Identify BCNF violations.
        A relation is in BCNF if for every non-trivial FD X -> Y, X is a superkey.
        """
        violations: list[FunctionalDependency] = []
        for fd in self.fds:
            lhs_set = set(fd.lhs)
            rhs_set = set(fd.rhs)
            # Trivial FD check: if Y is a subset of X, it is trivial
            if rhs_set.issubset(lhs_set):
                continue
            # BCNF condition: LHS must be a superkey
            if not self.is_superkey(lhs_set):
                violations.append(fd)
        return violations


class SchemaSSOTCompiler:
    """Master SSOT compiler that validates and renders all downstream deliverable artifacts."""

    def __init__(self) -> None:
        self.relations: dict[str, RelationSchema] = {}

    def add_relation(self, relation: RelationSchema) -> None:
        self.relations[relation.name] = relation

    def render_markdown_dictionary(self, relation_name: str) -> str:
        """Render publication-grade markdown data dictionary table for a relation."""
        rel = self.relations.get(relation_name)
        if not rel:
            raise KeyError(f"Relation '{relation_name}' not defined in SSOT schema.")

        lines = [
            f"### Data Dictionary: `{rel.name}`",
            "",
            "| Attribute | Type | Nullable | Key | Description |",
            "|:----------|:-----|:---------|:----|:------------|",
        ]
        pk_set = set(rel.primary_key)
        for attr in rel.attributes:
            attr_type = rel.types.get(attr, "VARCHAR(255)")
            is_nullable = rel.nullable.get(attr, True)
            null_str = "YES" if is_nullable else "NO"

            key_tags = []
            if attr in pk_set:
                key_tags.append("PK")
            if attr in rel.foreign_keys:
                key_tags.append("FK")
            key_cell = "/".join(key_tags)

            desc = rel.descriptions.get(attr, "")
            lines.append(f"| {attr} | {attr_type} | {null_str} | {key_cell} | {desc} |".replace("|  |", "| |"))

        return "\n".join(lines)

    def render_mermaid_erd(self) -> str:
        """Render Mermaid ERD diagram representing all relations and foreign key relationships."""
        lines = ["erDiagram"]

        # 1. Relationships
        for rel_name, rel in self.relations.items():
            for col, (target_table, target_col) in rel.foreign_keys.items():
                lines.append(f"    {target_table} ||--o{{ {rel_name} : places")

        # 2. Entity definitions
        for rel_name, rel in self.relations.items():
            lines.append(f"    {rel_name} {{")
            pk_set = set(rel.primary_key)
            for attr in rel.attributes:
                col_type = rel.types.get(attr, "string")
                tag = "PK" if attr in pk_set else ("FK" if attr in rel.foreign_keys else "")
                lines.append(f"        {col_type} {attr} {tag}".strip())
            lines.append("    }")

        return "\n".join(lines)

    def render_sql_ddl(self, relation_name: str) -> str:
        """Render standard ANSI SQL DDL CREATE TABLE statement with PK and FK constraints."""
        rel = self.relations.get(relation_name)
        if not rel:
            raise KeyError(f"Relation '{relation_name}' not defined in SSOT schema.")

        col_defs = []
        pk_set = set(rel.primary_key)
        for attr in rel.attributes:
            attr_type = rel.types.get(attr, "VARCHAR(255)")
            not_null = " NOT NULL" if (not rel.nullable.get(attr, True) or attr in pk_set) else ""
            col_defs.append(f"    {attr} {attr_type}{not_null}")

        if rel.primary_key:
            pk_cols = ", ".join(rel.primary_key)
            col_defs.append(f"    PRIMARY KEY ({pk_cols})")

        for col, (target_table, target_col) in rel.foreign_keys.items():
            col_defs.append(f"    FOREIGN KEY ({col}) REFERENCES {target_table}({target_col})")

        inner_body = ",\n".join(col_defs)
        return f"CREATE TABLE {rel.name} (\n{inner_body}\n);"

    def verify_markdown_table_parity(self, relation_name: str, markdown_table: str) -> dict[str, Any]:
        """
        Verify that a rendered markdown table does not deviate from the SSOT relation schema.
        Detects missing columns and rogue/unexpected attributes.
        """
        rel = self.relations.get(relation_name)
        if not rel:
            raise KeyError(f"Relation '{relation_name}' not defined in SSOT schema.")

        expected_attrs = set(rel.attributes)
        found_attrs: set[str] = set()
        header_skipped = False

        for line in markdown_table.strip().splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Skip separator rows like |:---|---|
            if re.match(r"^\|(?:\s*:?-+:?\s*\|)+\Z", line):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not cells:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            found_attrs.add(cells[0])

        missing = sorted(expected_attrs - found_attrs)
        unexpected = sorted(found_attrs - expected_attrs)

        return {
            "is_valid": len(missing) == 0 and len(unexpected) == 0,
            "missing_attributes": missing,
            "unexpected_attributes": unexpected,
            "expected_count": len(expected_attrs),
            "found_count": len(found_attrs),
        }
