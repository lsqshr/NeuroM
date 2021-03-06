# Copyright (c) 2015, Ecole Polytechnique Federale de Lausanne, Blue Brain Project
# All rights reserved.
#
# This file is part of NeuroM <https://github.com/BlueBrain/NeuroM>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#     3. Neither the name of the copyright holder nor the names of
#        its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from nose import tools as nt
import numpy as np
import neurom as nm
from neurom.apps import morph_stats as ms
from neurom.exceptions import ConfigError

_path = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_path, '../../../test_data/swc')


REF_CONFIG = {
    'neurite': {
        'section_lengths': ['max', 'total'],
        'section_volumes': ['total'],
        'section_branch_orders': ['max']
    },
    'neurite_type': ['AXON', 'APICAL_DENDRITE', 'BASAL_DENDRITE', 'ALL'],
    'neuron': {
        'soma_radii': ['mean']
    }
}

REF_OUT = {
    'mean_soma_radius': 0.17071067811865476,
    'axon': {
        'total_section_length': 207.87975220908129,
        'max_section_length': 11.018460736176685,
        'max_section_branch_order': 10,
        'total_section_volume': 276.73857657289523
    },
    'all': {
        'total_section_length': 840.68521442251949,
        'max_section_length': 11.758281556059444,
        'max_section_branch_order': 10,
        'total_section_volume': 1104.9077419665782
    },
    'apical_dendrite': {
        'total_section_length': 214.37304577550353,
        'max_section_length': 11.758281556059444,
        'max_section_branch_order': 10,
        'total_section_volume': 271.9412385728449
    },
    'basal_dendrite': {
        'total_section_length': 418.43241643793476,
        'max_section_length': 11.652508126101711,
        'max_section_branch_order': 10,
        'total_section_volume': 556.22792682083821
    }
}


def test_name_correction():
    nt.assert_equal(ms._stat_name('foo', 'raw'), 'foo')
    nt.assert_equal(ms._stat_name('foos', 'raw'), 'foo')
    nt.assert_equal(ms._stat_name('foos', 'bar'), 'bar_foo')
    nt.assert_equal(ms._stat_name('foos', 'total'), 'total_foo')
    nt.assert_equal(ms._stat_name('soma_radii', 'total'), 'total_soma_radius')
    nt.assert_equal(ms._stat_name('soma_radii', 'raw'), 'soma_radius')


def test_eval_stats_raw_returns_list():
    nt.assert_equal(ms.eval_stats(np.array([1,2,3,4]), 'raw'), [1,2,3,4])


def test_eval_stats_empty_input_returns_none():
    nt.assert_true(ms.eval_stats([], 'min') is None)


def test_eval_stats_total_returns_sum():
    nt.assert_equal(ms.eval_stats(np.array([1,2,3,4]), 'total'), 10)


def test_eval_stats_applies_numpy_function():
    modes = ('min', 'max', 'mean', 'median', 'std')

    ref_array = np.array([1,2,3,4,5,6,7,8,9,10])

    for m in modes:
        nt.eq_(ms.eval_stats(ref_array, m),
               getattr(np, m)(ref_array))


def test_extract_stats_single_neuron():

    nrn = nm.load_neuron(os.path.join(DATA_PATH, 'Neuron.swc'))
    res = ms.extract_stats(nrn, REF_CONFIG)
    nt.eq_(res.keys(), REF_OUT.keys())
    nt.assert_almost_equal(res['mean_soma_radius'], REF_OUT['mean_soma_radius'])

    for k in ('all', 'axon', 'basal_dendrite', 'apical_dendrite'):
        nt.eq_(res[k].keys(), REF_OUT[k].keys())
        for kk in res[k].keys():
            nt.assert_almost_equal(res[k][kk], REF_OUT[k][kk])


def test_get_header():
    fake_results = {'fake_name0': REF_OUT,
                    'fake_name1': REF_OUT,
                    'fake_name2': REF_OUT,
                    }
    header = ms.get_header(fake_results)
    nt.eq_(1 + 1 + 4 * 4, len(header))  # name + everything in REF_OUT
    nt.ok_('name' in header)
    nt.ok_('mean_soma_radius' in header)


def test_generate_flattened_dict():
    fake_results = {'fake_name0': REF_OUT,
                    'fake_name1': REF_OUT,
                    'fake_name2': REF_OUT,
                    }
    header = ms.get_header(fake_results)
    rows = list(ms.generate_flattened_dict(header, fake_results))
    nt.eq_(3, len(rows))  # one for fake_name[0-2]
    nt.eq_(1 + 1 + 4 * 4, len(rows[0]))  # name + everything in REF_OUT


def test_sanitize_config():
    nt.assert_raises(ConfigError, ms.sanitize_config, {'neurite': []})

    new_config = ms.sanitize_config({}) #empty
    nt.eq_(2, len(new_config)) #neurite & neuron created

    full_config = {
        'neurite': {
            'section_lengths': ['max', 'total'],
            'section_volumes': ['total'],
            'section_branch_orders': ['max']
        },
        'neurite_type': ['AXON', 'APICAL_DENDRITE', 'BASAL_DENDRITE', 'ALL'],
        'neuron': {
            'soma_radii': ['mean']
        }
    }
    new_config = ms.sanitize_config(full_config)
    nt.eq_(3, len(new_config)) #neurite, neurite_type & neuron

