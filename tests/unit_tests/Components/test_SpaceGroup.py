__author__ = 'github.com/wardsimon'
__version__ = '0.1.0'

#  SPDX-FileCopyrightText: 2022 easyCrystallography contributors  <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2024 Contributors to the easyscience project <https://github.com/easyScience/easyCrystallography>

import pytest
import itertools
import numpy as np

from easyscience.Objects.ObjectClasses import Descriptor, Parameter
from easyCrystallography.Components.SpaceGroup import SpaceGroup, SG_DETAILS as _SG_DETAILS
from easyCrystallography.Symmetry.groups import SpaceGroup as SG

SG_DETAILS = _SG_DETAILS.copy()
del SG_DETAILS['symmetry_ops']

known_conversions = {
    "A e m 2":  'A b m 2',
    "B m e 2":  'B m a 2',
    "B 2 e m":  'B 2 c m',
    "C 2 m e":  'C 2 m b',
    "C m 2 e":  'C m 2 a',
    "A e 2 m":  'A c 2 m',
    "A e a 2":  'A b a 2',
    "B b e 2":  'B b a 2',
    "B 2 e b":  'B 2 c b',
    "C 2 c e":  'C 2 c b',
    "C c 2 e":  'C c 2 a',
    "A e 2 a":  'A c 2 a',
    "C m c e":  'C m c a',
    "C c m e":  'C c m b',
    "A e m a":  'A b m a',
    "A e a m":  'A c a m',
    "B b e m":  'B b c m',
    "B m e b":  'B m a b',
    "C m m e":  'C m m a',
    "A e m m":  'A b m m',
    "B m e m":  'B m c m',
    "C c c e":  'C c c a',
    "A e a a":  'A b a a',
    "B b e b":  'B b c b',
    'B 1 21 1': 'B 1 1 2',

}

SYM = [value for value in SG.SYMM_OPS
       if '(' not in value['hermann_mauguin_fmt']
       or '(' not in value['hermann_mauguin']
       or '(' not in value['universal_h_m']]


def test_SpaceGroup_fromDescriptor():
    sg_items = ['space_group_HM_name', 'P 1']

    d = Descriptor(*sg_items)
    sg = SpaceGroup(d)
    assert sg.space_group_HM_name.raw_value == 'P 1'

    with pytest.raises(ValueError):
        p = Parameter('space_group_HM_name', 1)
        sg = SpaceGroup(p)


def test_SpaceGroup_default():
    sg = SpaceGroup()
    assert sg.setting is None

    for selector in SG_DETAILS.keys():
        f = getattr(sg, selector)
        if f is None:
            continue
        for item in SG_DETAILS[selector].keys():
            g_item = item
            if item == 'value':
                g_item = 'raw_value'
            assert getattr(f, g_item) == SG_DETAILS[selector][item]

    assert isinstance(sg.space_group_HM_name, Descriptor)


@pytest.mark.parametrize('sg_in', [sg['hermann_mauguin_fmt'] for sg in SYM])
def test_SpaceGroup_fromPars_HM_Full(sg_in):
    if sg_in in ['C 2 e b', 'R 1 2/c 1 ("rhombohedral" setting)', 'B 1 21/m 1']:
        return  # This is a known issue

    sg_p = SpaceGroup(sg_in)

    for selector in SG_DETAILS.keys():
        f = getattr(sg_p, selector)
        if f is None:
            continue
        for item in SG_DETAILS[selector].keys():
            g_item = item
            f_value = SG_DETAILS[selector][item]
            if item == 'value':
                g_item = 'raw_value'
                f_value = sg_in.split(':')
            if f_value[0] in known_conversions.keys():
                f_value[0] = known_conversions[f_value[0]]
            assert getattr(f, g_item) in f_value


@pytest.mark.parametrize('sg_in', SYM, ids=[sg['hermann_mauguin'] for sg in SYM])
def test_SpaceGroup_fromPars_HM_noSpace(sg_in):
    if sg_in['hermann_mauguin'] in ['C2eb', 'R12/c1("rhombohedral"setting)', 'B1211', 'B121/m1', 'P4bm',
                                    'C1c1', 'Pmc21', 'Cmm2', 'P121/c1', 'Pmma', 'P12/c1', 'Pmmm', 'P1211', 'Pnma']:
        return  # This is a known issue

    sg_p = SpaceGroup(sg_in['hermann_mauguin'])

    for selector in SG_DETAILS.keys():
        f = getattr(sg_p, selector)
        if f is None:
            continue
        for item in SG_DETAILS[selector].keys():
            g_item = item
            f_value = SG_DETAILS[selector][item]
            if item == 'value':
                g_item = 'raw_value'
                f_value = sg_in['hermann_mauguin_fmt'].split(':')
            if f_value[0] in known_conversions.keys():
                f_value[0] = known_conversions[f_value[0]]
            assert getattr(f, g_item) in f_value


@pytest.mark.parametrize('sg_in', SYM, ids=[sg['universal_h_m'] for sg in SYM])
def test_SpaceGroup_fromPars_HM_noSpace(sg_in):
    if sg_in['hermann_mauguin'] in ['C2eb', 'R12/c1("rhombohedral"setting)', 'B1211', 'B121/m1', 'P4bm',
                                    'C1c1', 'Pmc21', 'Cmm2', 'P121/c1', 'Pmma', 'P12/c1', 'Pmmm', 'P1211', 'Pnma']:
        return  # This is a known issue

    sg_p = SpaceGroup(sg_in['universal_h_m'])

    for selector in SG_DETAILS.keys():
        f = getattr(sg_p, selector)
        if f is None:
            continue
        for item in SG_DETAILS[selector].keys():
            g_item = item
            f_value = SG_DETAILS[selector][item]
            if item == 'value':
                g_item = 'raw_value'
                f_value = sg_in['hermann_mauguin_fmt'].split(':')
            if f_value[0] in known_conversions.keys():
                f_value[0] = known_conversions[f_value[0]]
            assert getattr(f, g_item) in f_value


@pytest.mark.parametrize('sg_int', range(1, 231), ids=[f'spacegroup_int_{s_id}' for s_id in range(1, 231)])
def test_SpaceGroup_fromIntNumber(sg_int: int):
    sg_p = SpaceGroup.from_int_number(sg_int)

    for selector in SG_DETAILS.keys():
        f = getattr(sg_p, selector)
        if f is None:
            continue
        for item in SG_DETAILS[selector].keys():
            g_item = item
            f_value = SG_DETAILS[selector][item]
            if item == 'value':
                g_item = 'raw_value'
                for opt in SG.SYMM_OPS:
                    if opt['number'] == sg_int:
                        f_value = opt['hermann_mauguin_fmt'].split(':')
                        break
            if f_value[0] in known_conversions.keys():
                f_value[0] = known_conversions[f_value[0]]
            assert getattr(f, g_item) in f_value


@pytest.mark.parametrize('sg_int,setting', itertools.product([146, 148, 155, 160, 161, 166, 167], [True, False]))
def test_SpaceGroup_fromIntNumber_HexTest(sg_int: int, setting: bool):
    sg_p = SpaceGroup.from_int_number(sg_int, setting)

    for selector in SG_DETAILS.keys():
        f = getattr(sg_p, selector)
        for item in SG_DETAILS[selector].keys():
            g_item = item
            f_value = SG_DETAILS[selector][item]
            if item == 'value':
                g_item = 'raw_value'
                for opt in SG.SYMM_OPS:
                    if opt['number'] == sg_int:
                        f_value: str = opt['hermann_mauguin_fmt']
                        if f_value.endswith(':H') and setting or f_value.endswith(':R') and not setting:
                            break
                assert getattr(f, g_item) in f_value.split(':')
                return
        assert getattr(f, g_item) in f_value


def test_SpaceGroup_as_dict():
    sg_p = SpaceGroup.from_int_number(146)
    assert sg_p.as_data_dict() == {'name':                'SpaceGroup',
                                   'symmetry_ops':        None,
                                   'setting':             {
                                       'units':        'dimensionless',
                                       'enabled':      True,
                                       'name':         'coordinate-code',
                                       'display_name': 'coordinate-code',
                                       'url':
                                           'https://www.iucr.org/__data/iucr/cifdic_html/2/cif_sym.dic/Ispace_group'
                                           '.IT_coordinate_system_code.html',
                                       'description':  'A qualifier taken from the enumeration list identifying which '
                                                       'setting in International Tables for Crystallography Volume A '
                                                       '(2002) (IT) is used.',
                                       'value':        'H'
                                   },
                                   'interface':           None,
                                   'space_group_HM_name': {
                                       'units':        'dimensionless',
                                       'enabled':      True,
                                       'name':         'hermann_mauguin',
                                       'display_name': 'hermann_mauguin',
                                       'url':          'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic'
                                                       '/Ispace_group_name_H-M_alt.html',
                                       'description':  'Hermann-Mauguin symbols given in Table 4.3.2.1 of '
                                                       'International Tables for Crystallography Vol. A (2002) or a '
                                                       'Hermann-Mauguin symbol for a conventional or unconventional '
                                                       'setting.',
                                       'value':        'R 3'}}


def test_SpaceGroup_change_setting():
    sg_p = SpaceGroup('P b a n')
    assert sg_p.setting_str == '1'
    old_ops = sg_p.symmetry_ops
    sg_p.setting = '2'
    assert sg_p.setting.raw_value == '2'
    assert not np.all(sg_p.symmetry_ops == old_ops)


def test_SpaceGroup_from_dict():
    sg_p = SpaceGroup.from_int_number(146)
    d = sg_p.as_dict()
    sg_2 = SpaceGroup.from_dict(d)
    assert sg_2.as_data_dict() == sg_p.as_data_dict()


# def test_SpaceGroup_to_cif_str():
#     sg_p = SpaceGroup.from_int_number(15)
#     s = sg_p.to_cif_str()
#     assert s == '_space_group_name_H-M_ref C 1 2/c 1\n'


# def test_SpaceGroup_to_cif_str_with_setting():
#     sg_p = SpaceGroup.from_int_number(146)
#     s = sg_p.to_cif_str()
#     assert s == '_space_group_name_H-M_ref R 3\n_space_group_IT_coordinate_system_code H\n'


def testSpaceGroup_from_SymOps():
    from easyCrystallography.Symmetry.SymOp import SymmOp
    ops_str = 'x, y, z;-x, y, -z+1/2;-x, -y, -z;x, -y, z+1/2;x+1/2, y+1/2, z;-x+1/2, y+1/2, -z+1/2;-x+1/2, -y+1/2, ' \
              '-z;x+1/2, -y+1/2, z+1/2'
    ops_str_list = ops_str.split(';')
    ops = [SymmOp.from_xyz_string(op) for op in ops_str_list]
    spg = SpaceGroup.from_symOps(ops)
    assert spg.int_number == 15


def testSpaceGroup_from_xyz_string():
    ops_str = 'x, y, z;-x, y, -z+1/2;-x, -y, -z;x, -y, z+1/2;x+1/2, y+1/2, z;-x+1/2, y+1/2, -z+1/2;-x+1/2, -y+1/2, ' \
              '-z;x+1/2, -y+1/2, z+1/2'
    ops_str_list = ops_str.split(';')

    spg = SpaceGroup.from_xyz_string(ops_str)
    assert spg.int_number == 15
    spg = SpaceGroup.from_xyz_string(ops_str_list)
    assert spg.int_number == 15


def testSpaceGroup_from_SymOps():
    from easyCrystallography.Symmetry.SymOp import SymmOp
    ops_str = 'x, y, z;-x, y, -z+1/2;-x, -y, -z;x, -y, z+1/2;x+1/2, y+1/2, z;-x+1/2, y+1/2, -z+1/2;-x+1/2, -y+1/2, ' \
              '-z;x+1/2, -y+1/2, z+1/2'
    ops_str_list = ops_str.split(';')
    ops = [SymmOp.from_xyz_string(op) for op in ops_str_list]
    sym_mat_rot = [op.rotation_matrix for op in ops]
    sym_mat_trans = [op.translation_vector for op in ops]
    spg = SpaceGroup.from_symMatrices(sym_mat_rot, sym_mat_trans)
    assert spg.int_number == 15


def testSpaceGroup_from_gemmi_ops():
    from gemmi import Op, GroupOps
    ops_str = 'x, y, z;-x, y, -z+1/2;-x, -y, -z;x, -y, z+1/2;x+1/2, y+1/2, z;-x+1/2, y+1/2, -z+1/2;-x+1/2, -y+1/2, ' \
              '-z;x+1/2, -y+1/2, z+1/2'
    ops_str_list = ops_str.split(';')
    ops = [Op(op) for op in ops_str_list]

    spg = SpaceGroup.from_gemmi_operations(ops)
    assert spg.int_number == 15

    spg = SpaceGroup.from_gemmi_operations(GroupOps(ops))
    assert spg.int_number == 15