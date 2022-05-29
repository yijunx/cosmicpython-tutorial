# domain model

# The domain model is the mental map that business owners have of their businesses.
# All business people have these mental maps—​they’re how humans think about complex processes.

# here we are using dataclasses
# dataclasses are great for value objects

from dataclasses import dataclass
from datetime import date
from typing import Optional, Set


@dataclass(frozen=True)  # immutable
class OrderLine:
    """OrderLine is an immutable dataclass with no behavior."""

    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        # self.available_quantity = qty
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

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
