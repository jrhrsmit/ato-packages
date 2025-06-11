# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import faebryk.library._F as F
from faebryk.core.module import Module
from faebryk.libs.library import L
from faebryk.libs.units import P
from faebryk.libs.util import times


class OpAmpMulti(Module):
    bandwidth = L.p_field(units=P.Hz)
    common_mode_rejection_ratio = L.p_field(units=P.dB)
    input_bias_current = L.p_field(units=P.A)
    input_offset_voltage = L.p_field(units=P.V)
    gain_bandwidth_product = L.p_field(units=P.Hz)
    output_current = L.p_field(units=P.A)
    slew_rate = L.p_field(units=P.V / P.s)  # type: ignore
    num_amplifiers = L.p_field(units=P.count)

    power: F.ElectricPower

    def __init__(self, num_amplifiers: int):
        super().__init__()
        self._num_amplifiers = num_amplifiers

    def __preinit__(self) -> None:
        for i, opamp in enumerate(self.opamps):
            opamp.power.connect(self.power)
            opamp.inverting_input.connect(self.inverting_input[i])
            opamp.non_inverting_input.connect(self.non_inverting_input[i])
            opamp.output.connect(self.output[i])

            opamp.bandwidth.alias_is(self.bandwidth)
            opamp.common_mode_rejection_ratio.alias_is(self.common_mode_rejection_ratio)
            opamp.input_bias_current.alias_is(self.input_bias_current)
            opamp.input_offset_voltage.alias_is(self.input_offset_voltage)
            opamp.gain_bandwidth_product.alias_is(self.gain_bandwidth_product)
            opamp.output_current.alias_is(self.output_current)
            opamp.slew_rate.alias_is(self.slew_rate)

    @L.rt_field
    def inverting_input(self):
        return times(self._num_amplifiers, F.Electrical)

    @L.rt_field
    def non_inverting_input(self):
        return times(self._num_amplifiers, F.Electrical)

    @L.rt_field
    def output(self):
        return times(self._num_amplifiers, F.Electrical)

    @L.rt_field
    def simple_value_representation(self):
        S = F.has_simple_value_representation_based_on_params_chain.Spec
        return F.has_simple_value_representation_based_on_params_chain(
            S(self.bandwidth, suffix="BW"),
            S(self.common_mode_rejection_ratio, suffix="CMRR"),
            S(self.input_bias_current, suffix="Ib"),
            S(self.input_offset_voltage, suffix="Vos"),
            S(self.gain_bandwidth_product, suffix="GBW"),
            S(self.output_current, suffix="Iout"),
            S(self.slew_rate, suffix="SR"),
        )

    @L.rt_field
    def pin_association_heuristic(self):
        mapping = {
            self.power.hv: ["V+", "Vcc", "Vdd", "Vcc+"],
            self.power.lv: ["V-", "Vee", "Vss", "GND", "Vcc-", "Vcc-/GND"],
        }
        for i in range(self._num_amplifiers):
            pin_num = i + 1
            mapping[self.inverting_input[i]] = [f"{pin_num}-", f"IN{pin_num}-"]
            mapping[self.non_inverting_input[i]] = [f"{pin_num}+", f"IN{pin_num}+"]
            mapping[self.output[i]] = [f"OUT{pin_num}"]

        return F.has_pin_association_heuristic_lookup_table(
            mapping=mapping,
            accept_prefix=False,
            case_sensitive=False,
        )

    @L.rt_field
    def opamps(self):
        return times(self._num_amplifiers, F.OpAmp)

    designator_prefix = L.f_field(F.has_designator_prefix)(
        F.has_designator_prefix.Prefix.U
    )

    @property
    def inverting(self) -> list[F.Electrical]:
        return self.inverting_input

    @property
    def non_inverting(self) -> list[F.Electrical]:
        return self.non_inverting_input
