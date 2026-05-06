from __future__ import annotations

from dataclasses import dataclass

from models.vm import VM


@dataclass(frozen=True)
class VMTemplate:
    name: str
    mips: float
    ram_mb: int
    bandwidth_mbps: int
    pes: int = 1


@dataclass(frozen=True)
class Datacenter:
    name: str
    templates: list[VMTemplate]

    def build_vms(self) -> list[VM]:
        vms: list[VM] = []
        for index, template in enumerate(self.templates, start=1):
            vms.append(
                VM(
                    id=f"VM{index:02d}",
                    name=template.name,
                    mips=template.mips,
                    ram_mb=template.ram_mb,
                    bandwidth_mbps=template.bandwidth_mbps,
                    pes=template.pes,
                )
            )
        return vms
