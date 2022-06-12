# domain model

# The domain model is the mental map that business owners have of their businesses.
# All business people have these mental maps—​they’re how humans think about complex processes.

# here we are using dataclasses
# dataclasses are great for value objects

from dataclasses import dataclass
from datetime import date
from typing import Optional, Set, List


@dataclass(frozen=True)  # immutable
class OrderLine:
    """OrderLine is an immutable dataclass with no behavior."""

    # Whenever we have a business concept that has data but no identity,
    # we often choose to represent it using the Value Object pattern.
    # A value object is any domain object that is
    # uniquely identified by the data it holds;
    # we usually make them immutable:
    # thus frozen = True

    # One of the nice things that dataclasses
    # (or namedtuples) give us is value equality,
    # which is the fancy way of saying,
    # "Two lines with the same orderid, sku, and qty are equal."

    orderid: str
    sku: str
    qty: int


class Batch:

    # We use the term entity to
    # describe a domain object that has long-lived identity.
    # On the previous page, we introduced a Name class as a value object.
    # If we take the name Harry Percival and change one letter,
    # we have the new Name object Barry Percival.

    # Entities, unlike values, have identity equality.
    # We can change their values,
    # and they are still recognizably the same thing.
    # Batches, in our example, are entities.
    # We can allocate lines to a batch,
    # or change the date that we expect it to arrive,
    # and it will still be the same entity.

    # thus we can add __eq__, or __hash__ as below

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        # self.available_quantity = qty
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    @property
    def allocated_quantity(self) -> int:
        return sum(x.qty for x in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
    except StopIteration:
        raise OutOfStock(f"out of stock for sku {line.sku}")
    return batch.reference
