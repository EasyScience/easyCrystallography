from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

from typing import List, NoReturn, TYPE_CHECKING, ClassVar, Tuple, Dict

from .template import CIF_Template, gemmi
from easyCrystallography.Components.Site import Site as _Site, Atoms as _Atoms
from easyCrystallography.Components.AtomicDisplacement import AtomicDisplacement as _AtomicDisplacement
from easyCrystallography.Components.Susceptibility import MagneticSusceptibility as _MagneticSusceptibility

if TYPE_CHECKING:
    from easyCore.Utils.typing import B


class AtomicDisplacement(CIF_Template):

    _CIF_SECTION_NAME: ClassVar[str] = "_atom_site"

    _CIF_ADP_ISO_CONVERSIONS = [
        ("label", "_label"),
        ("adp_type", "_adp_type"),
        ("Biso", "_B_iso_or_equiv"),
        ("Uiso", "_U_iso_or_equiv"),
    ]
    _CIF_ADP_ANISO_CONVERSIONS = [
        ("label", "_aniso_label"),
        ("adp_type", "_adp_type"),
        ("B_11", "_aniso_B_11"),
        ("B_12", "_aniso_B_12"),
        ("B_13", "_aniso_B_13"),
        ("B_22", "_aniso_B_22"),
        ("B_23", "_aniso_B_23"),
        ("B_33", "_aniso_B_33"),
        ("U_11", "_aniso_U_11"),
        ("U_12", "_aniso_U_12"),
        ("U_13", "_aniso_U_13"),
        ("U_22", "_aniso_U_22"),
        ("U_23", "_aniso_U_23"),
        ("U_33", "_aniso_U_33"),
    ]

    def __init__(self, reference_class=_AtomicDisplacement):
        super().__init__()
        self._CIF_CLASS = reference_class

    def from_cif_block(self, block: gemmi.cif.Block) -> Dict[str, B]:

        atom_dict = {}
        # ADP CHECKER
        keys = [
            self._CIF_SECTION_NAME + name[1] if 'label' in name[1] else '?' + self._CIF_SECTION_NAME + name[1]
            for name in self._CIF_ADP_ISO_CONVERSIONS]
        table = block.find(keys)
        for row in table:
            kwargs = {}
            errors = {}
            is_fixed = {}
            if not row.has(0):
                continue
            if row.has(1):
                kwargs['adp_type'] = row[1]
            else:
                if row.has(2):
                    kwargs['adp_type'] = 'Biso'
                elif row.has(3):
                    kwargs['adp_type'] = 'Uiso'
                else:
                    continue

            for i in range(2, 4):
                if row.has(i):
                    V, E, F = self.string_to_variable(row[i])
                    kwargs[kwargs['adp_type']] = V
                    if E:
                        errors[kwargs['adp_type']] = E
                    if F is not None and not F:
                        is_fixed[kwargs['adp_type']] = F
            obj = _AtomicDisplacement(**kwargs)
            for error in errors.keys():
                setattr(getattr(obj, error), 'error', errors[error])
            for atr in is_fixed.keys():
                setattr(getattr(obj, atr), 'fixed', is_fixed[atr])
            atom_dict[row[0]] = {'adp': obj}

        keys = [
            self._CIF_SECTION_NAME + name[1] if 'label' in name[1] else '?' + self._CIF_SECTION_NAME + name[1]
            for name in self._CIF_ADP_ANISO_CONVERSIONS]
        table = block.find(keys)
        for row in table:
            kwargs = {}
            errors = {}
            is_fixed = {}
            if not row.has(0):
                continue
            if row.has(2):
                kwargs['adp_type'] = 'Bani'
                idx = 2
            elif row.has(8):
                idx = 8
                kwargs['adp_type'] = 'Uani'
            else:
                continue
            for i in range(idx, idx + 6):
                l = self._CIF_ADP_ANISO_CONVERSIONS[i][0]
                if row.has(i):
                    V, E, F = self.string_to_variable(row[i])
                    kwargs[l] = V
                    if E:
                        errors[l] = E
                    if F is not None and not F:
                        is_fixed[l] = F
            obj = _AtomicDisplacement(**kwargs)
            for error in errors.keys():
                setattr(getattr(obj, error), 'error', errors[error])
            for atr in is_fixed.keys():
                setattr(getattr(obj, atr), 'fixed', is_fixed[atr])
            atom_dict[row[0]] = {'adp': obj}
        return atom_dict

    def add_to_cif_block(self, obj: B, block: gemmi.cif.Block):
        labels = []
        objs = []

        # Assume that all atoms have the same adp type
        if len(obj) == 0:
            return labels, objs
        adp0 = getattr(obj[0], 'adp', None)
        if adp0 is None:
            return labels, objs
        adp_type = adp0.adp_type.raw_value
        if adp_type[-3:] == 'iso':
            labels = self._CIF_ADP_ISO_CONVERSIONS.copy()
            if adp_type[0].lower() == 'u':
                del labels[2]
            else:
                del labels[3]
            objs = [[getattr(_obj, 'adp')] for _obj in obj]
            del labels[0]
            return [[labels]] * len(objs), objs
        elif adp_type[-3:] == 'ani':
            labels = self._CIF_ADP_ANISO_CONVERSIONS.copy()
            if adp_type[0].lower() == 'u':
                idx = 7
                idy = 1
            else:
                idx = 1
                idy = 7
            rows = []
            # for _obj in obj:
                # row = [self.variable_to_string(getattr(_obj, self._CIF_ADP_ANISO_CONVERSIONS[0][0]))]
                #if not hasattr(_obj.adp, self._CIF_ADP_ANISO_CONVERSIONS[idx][0]):
                #    continue
                # for i in range(idx, idx + 6):
                    # row.append(self.variable_to_string(getattr(_obj.adp, self._CIF_ADP_ANISO_CONVERSIONS[i][0])))
                    # row.append(getattr(_obj.adp, self._CIF_ADP_ANISO_CONVERSIONS[i][0]))
                # rows.append(getattr(_obj, 'adp'))
                # rows.append(row)
            objs = [[getattr(_obj, 'adp')] for _obj in obj if hasattr(_obj.adp, self._CIF_ADP_ANISO_CONVERSIONS[idx][0])]
            del labels[idy: idy + 6]
            del labels[0]
            # loop = block.init_loop(self._CIF_SECTION_NAME, [label[1] for label in labels])
            #for row in rows:
            #    loop.add_row(row)
        return [[labels]]*len(objs), objs

    def from_cif_string(self, cif_string: str) -> List[Dict[str, B]]:
        if "data_" not in cif_string:
            cif_string = "data_temp\n" + cif_string
        cif_blocks = gemmi.cif.read_string(cif_string)
        objs = []
        for block in cif_blocks:
            objs.append(self.from_cif_block(block))
        return objs


class MagneticSusceptibility(CIF_Template):

    _CIF_SECTION_NAME: ClassVar[str] = "_atom_site"
    _CIF_MSP_ANISO_CONVERSIONS = [
        ("label", "_susceptibility_label"),
        ("msp_type", "_susceptibility_chi_type"),
        ("chi_11", "_susceptibility_chi_11"),
        ("chi_12", "_susceptibility_chi_12"),
        ("chi_13", "_susceptibility_chi_13"),
        ("chi_22", "_susceptibility_chi_22"),
        ("chi_23", "_susceptibility_chi_23"),
        ("chi_33", "_susceptibility_chi_33"),
    ]

    def __init__(self, reference_class=_MagneticSusceptibility):
        super().__init__()
        self._CIF_CLASS = reference_class

    def from_cif_block(self, block: gemmi.cif.Block) -> Dict[str, B]:

        atom_dict = {}
        keys = [
            self._CIF_SECTION_NAME + name[1] if 'label' in name[1] else '?' + self._CIF_SECTION_NAME + name[1]
            for name in self._CIF_MSP_ANISO_CONVERSIONS]
        table = block.find(keys)
        for row in table:
            kwargs = {}
            errors = {}
            is_fixed = {}
            if not row.has(0):
                continue
            if row.has(1):
                kwargs['msp_type'] = row[1]
            else:
                continue
            idx = 2
            for i in range(idx, idx + 6):
                l = self._CIF_MSP_ANISO_CONVERSIONS[i][0]
                if row.has(i):
                    V, E, F = self.string_to_variable(row[i])
                    kwargs[l] = V
                    if E:
                        errors[l] = E
                    if F is not None and not F:
                        is_fixed[l] = F
            obj = _MagneticSusceptibility(**kwargs)
            for error in errors.keys():
                setattr(getattr(obj, error), 'error', errors[error])
            for atr in is_fixed.keys():
                setattr(getattr(obj, atr), 'fixed', is_fixed[atr])
            atom_dict[row[0]] = {'msp': obj}
        return atom_dict

    def add_to_cif_block(self, obj: B, block: gemmi.cif.Block) -> NoReturn:
        # Then add the additional loops
        lines = []
        for atom in obj:
            if not hasattr(atom, 'msp'):
                continue
            line = [self.variable_to_string(atom.__getattribute__(self._CIF_MSP_ANISO_CONVERSIONS[0][0]))]
            for keys in self._CIF_MSP_ANISO_CONVERSIONS[1:]:
                key, cif_key = keys
                s = self.variable_to_string(atom.msp.__getattribute__(key))
                line.append(s)
            lines.append(line)
        _, names = zip(*self._CIF_MSP_ANISO_CONVERSIONS)
        loop = block.init_loop(self._CIF_SECTION_NAME, names)
        for line in lines:
            loop.add_row(line)

    def from_cif_string(self, cif_string: str) -> List[B]:
        if "data_" not in cif_string:
            cif_string = "data_temp\n" + cif_string
        cif_blocks = gemmi.cif.read_string(cif_string)
        objs = []
        for block in cif_blocks:
            objs.append(self.from_cif_block(block))
        return objs


class Atoms(CIF_Template):

    _CIF_SECTION_NAME: ClassVar[str] = "_atom_site"
    _CIF_CONVERSIONS: ClassVar[List[Tuple[str, str]]] = [
        ("label", "_label"),
        ("specie", "_type_symbol"),
        ("fract_x", "_fract_x"),
        ("fract_y", "_fract_y"),
        ("fract_z", "_fract_z"),
        ("occupancy", "_occupancy"),
    ]

    def __init__(self, reference_class=_Atoms):
        super().__init__()
        self._CIF_CLASS = reference_class

    def _site_runner(self, block):
        keys = [
            self._CIF_SECTION_NAME + name[1] if 'occupancy' not in name[1] else '?' + self._CIF_SECTION_NAME + name[1]
            for name in self._CIF_CONVERSIONS]
        table = block.find(keys)
        atom_dict = {}
        error_dict = {}
        fixed_dict = {}
        for row in table:
            kwargs = {}
            errors = {}
            is_fixed = {}
            for idx, item in enumerate(self._CIF_CONVERSIONS):
                ec_name, cif_name = item
                if row.has(idx):
                    V, E, F = self.string_to_variable(row[idx])
                    kwargs[ec_name] = V
                    if E:
                        errors[ec_name] = E
                    if F is not None and not F:
                        is_fixed[ec_name] = F
            atom_dict[kwargs['label']] = kwargs
            error_dict[kwargs['label']] = errors
            fixed_dict[kwargs['label']] = is_fixed

        # ADP CHECKER
        ADP_RUNNER = AtomicDisplacement()
        adp_dict = ADP_RUNNER.from_cif_block(block)
        for label, adp in adp_dict.items():
            if label in atom_dict:
                atom_dict[label].update(adp)

        # MSP Checker
        MSP_RUNNER = MagneticSusceptibility()
        msp_dict = MSP_RUNNER.from_cif_block(block)
        for label, msp in msp_dict.items():
            if label in atom_dict:
                atom_dict[label].update(msp)

        atoms = []
        for a in atom_dict.values():
            obj = self._CIF_CLASS._SITE_CLASS(**a)
            if obj.label in error_dict.keys():
                for atr in error_dict[obj.label].keys():
                    setattr(getattr(obj, atr), 'error', error_dict[obj.label][atr])
            if obj.label in fixed_dict.keys():
                for atr in fixed_dict[obj.label].keys():
                    setattr(getattr(obj, atr), 'fixed', fixed_dict[obj.label][atr])
            atoms.append(obj)
        return atoms

    def from_cif_block(self, block: gemmi.cif.Block) -> B:
        atoms = self._site_runner(block)
        return self._CIF_CLASS('from_cif', *atoms)

    def add_to_cif_block(self, obj: B, block: gemmi.cif.Block) -> NoReturn:
        additional_keys = []
        additional_objs = []
        if len(obj) > 0:
            if getattr(obj[0], 'adp', False):
                ADP_WRITER = AtomicDisplacement()
                additional_keys, additional_objs = ADP_WRITER.add_to_cif_block(obj, block)
        MSP_WRITER = MagneticSusceptibility()
        MSP_WRITER.add_to_cif_block(obj, block)
        self._add_to_cif_block(obj, block, additional_keys, additional_objs)

    def _add_to_cif_block(self, obj: B, block: gemmi.cif.Block, additional_keys, additional_objs) -> NoReturn:
        # First add the main loop
        items = list(self._CIF_CONVERSIONS)
        names = [item[1] for item in items]
        lines = []
        for idx1, atom in enumerate(obj):
            line = []
            for idx2, item in enumerate(items):
                if item[0] == 'specie':
                    s = str(atom.specie)
                else:
                    s = self.variable_to_string(atom.__getattribute__(item[0]))
                line.append(s)
            lines.append(line)

        for keys, objs, line in zip(additional_keys, additional_objs, lines):
            for idx, _obj in enumerate(objs):
                for key in keys[idx]:
                    s = self.variable_to_string(_obj.__getattribute__(key[0]))
                    line.append(s)
                    if key[1] not in names:
                        names.append(key[1])
        loop = block.init_loop(self._CIF_SECTION_NAME, names)
        for line in lines:
            loop.add_row(line)

    def from_cif_string(self, cif_string: str) -> List[B]:
        if "data_" not in cif_string:
            cif_string = "data_temp\n" + cif_string
        cif_blocks = gemmi.cif.read_string(cif_string)
        objs = []
        for block in cif_blocks:
            objs.append(self.from_cif_block(block))
        return objs


