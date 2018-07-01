# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
import os
from pprint import pprint
from unittest import TestCase

from os.path import join

import pytest

from conda.base.context import context, reset_context, Context
from conda.common.io import env_var, env_vars, stderr_log_level
from conda.core.prefix_data import PrefixData
from conda.core.solve import DepsModifier, Solver, UpdateModifier
from conda.exceptions import UnsatisfiableError, PackagesNotFoundError
from conda.history import History
from conda.models.channel import Channel
from conda.models.records import PrefixRecord
from conda.core.solve import SpecsGroup
from conda.resolve import MatchSpec
from ..helpers import get_index_r_1, get_index_r_2, get_index_r_4, get_index_r_5
from conda.common.compat import iteritems

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

TEST_PREFIX = '/a/test/c/prefix'


@contextmanager
def get_solver(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    PrefixData._cache_.clear()
    pd = PrefixData(TEST_PREFIX)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    specs_group = SpecsGroup(history_specs)
    get_index_r_1()
    with patch.object(History, 'get_requested_specs', return_value=specs_group):
        solver = Solver(TEST_PREFIX, (Channel('channel-1'),), (context.subdir,),
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        yield solver


@contextmanager
def get_solver_2(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    PrefixData._cache_.clear()
    pd = PrefixData(TEST_PREFIX)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    specs_group = SpecsGroup(history_specs)
    get_index_r_2()
    with patch.object(History, 'get_requested_specs', return_value=specs_group):
        solver = Solver(TEST_PREFIX, (Channel('channel-2'),), (context.subdir,),
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        yield solver


@contextmanager
def get_solver_4(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    PrefixData._cache_.clear()
    pd = PrefixData(TEST_PREFIX)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    specs_group = SpecsGroup(history_specs)
    get_index_r_4()
    with patch.object(History, 'get_requested_specs', return_value=specs_group):
        solver = Solver(TEST_PREFIX, (Channel('channel-4'),), (context.subdir,),
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        yield solver


@contextmanager
def get_solver_5(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    PrefixData._cache_.clear()
    pd = PrefixData(TEST_PREFIX)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    specs_group = SpecsGroup(history_specs)
    get_index_r_5()
    with patch.object(History, 'get_requested_specs', return_value=specs_group):
        solver = Solver(TEST_PREFIX, (Channel('channel-5'),), (context.subdir,),
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        yield solver


@contextmanager
def get_solver_aggregate_1(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    PrefixData._cache_.clear()
    pd = PrefixData(TEST_PREFIX)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    specs_group = SpecsGroup(history_specs)
    get_index_r_2()
    get_index_r_4()
    with patch.object(History, 'get_requested_specs', return_value=specs_group):
        solver = Solver(TEST_PREFIX, (Channel('channel-2'), Channel('channel-4'), ),
                        (context.subdir,), specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        yield solver


def convert_to_dist_str(solution):
    return tuple(prec.dist_str() for prec in solution)

def convert_to_record_id(solution):
    return tuple(prec.record_id() for prec in solution)


def test_solve_1():
    specs = MatchSpec("numpy"),
    with get_solver(specs) as solver:
        final_state = solver.solve_final_state()
        # print(convert_to_dist_str(final_state))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-3.3.2-0',
            'channel-1::numpy-1.7.1-py33_0',
        )
        assert convert_to_dist_str(final_state) == order

    specs_to_add = MatchSpec("python=2"),
    with get_solver(specs_to_add=specs_to_add,
                    prefix_records=final_state, history_specs=specs) as solver:
        final_state = solver.solve_final_state()
        # print(convert_to_dist_str(final_state))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numpy-1.7.1-py27_0',
        )
        assert convert_to_dist_str(final_state) == order


def test_packages_not_found_error():
    specs = MatchSpec("numpie"),
    with get_solver(specs) as solver:
        with pytest.raises(PackagesNotFoundError) as exc:
            solver.solve_final_state()
    print(repr(exc.value))
    assert "Current channel urls with subdirs" in str(exc.value)


def test_prune_1():
    specs = MatchSpec("numpy=1.6"), MatchSpec("python=2.7.3"), MatchSpec("accelerate"),

    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::libnvvm-1.0-p0',
            'channel-1::mkl-rt-11.0-p0',
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.7.3-7',
            'channel-1::bitarray-0.8.1-py27_0',
            'channel-1::llvmpy-0.11.2-py27_0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::mkl-service-1.0.0-py27_p0',
            'channel-1::numpy-1.6.2-py27_p4',
            'channel-1::numba-0.8.1-np16py27_0',
            'channel-1::numexpr-2.1-np16py27_p0',
            'channel-1::scipy-0.12.0-np16py27_p0',
            'channel-1::numbapro-0.11.0-np16py27_p0',
            'channel-1::scikit-learn-0.13.1-np16py27_p0',
            'channel-1::mkl-11.0-np16py27_p0',
            'channel-1::accelerate-1.1.0-np16py27_p0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_remove = MatchSpec("numbapro"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        unlink_precs, link_precs = solver.solve_for_diff(prune=False)
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(unlink_precs))
        pprint(convert_to_dist_str(link_precs))
        unlink_order = (
            'channel-1::accelerate-1.1.0-np16py27_p0',
            'channel-1::numbapro-0.11.0-np16py27_p0',
        )
        assert convert_to_dist_str(unlink_precs) == unlink_order

        link_order = ()
        assert convert_to_dist_str(link_precs) == link_order

    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        unlink_precs, link_precs = solver.solve_for_diff(prune=True)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(unlink_precs))
        unlink_order = (
            'channel-1::accelerate-1.1.0-np16py27_p0',
            'channel-1::mkl-11.0-np16py27_p0',
            'channel-1::scikit-learn-0.13.1-np16py27_p0',
            'channel-1::numbapro-0.11.0-np16py27_p0',
            'channel-1::scipy-0.12.0-np16py27_p0',
            'channel-1::numexpr-2.1-np16py27_p0',
            'channel-1::numba-0.8.1-np16py27_0',
            'channel-1::numpy-1.6.2-py27_p4',
            'channel-1::mkl-service-1.0.0-py27_p0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::llvmpy-0.11.2-py27_0',
            'channel-1::bitarray-0.8.1-py27_0',
            'channel-1::llvm-3.2-0',
            'channel-1::mkl-rt-11.0-p0',
            'channel-1::libnvvm-1.0-p0',
        )
        assert convert_to_dist_str(unlink_precs) == unlink_order

        print(convert_to_dist_str(link_precs))
        link_order = (
            'channel-1::numpy-1.6.2-py27_4',
        )
        assert convert_to_dist_str(link_precs) == link_order


def test_force_remove_1():
    specs = MatchSpec("numpy[build=*py27*]"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numpy-1.7.1-py27_0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_remove = MatchSpec("python"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_remove = MatchSpec("python"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(force_remove=True)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::numpy-1.7.1-py27_0',
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
        )
        assert convert_to_dist_str(final_state_2) == order

    with get_solver(prefix_records=final_state_2) as solver:
        final_state_3 = solver.solve_final_state(prune=True)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_3))
        order = ()
        assert convert_to_dist_str(final_state_3) == order


def test_no_deps_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = MatchSpec("numba"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.7.5-0',
            'channel-1::llvmpy-0.11.2-py27_0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::numpy-1.7.1-py27_0',
            'channel-1::numba-0.8.1-np17py27_0'
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_add = MatchSpec("numba"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier='NO_DEPS')
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numba-0.8.1-np17py27_0',
        )
        assert convert_to_dist_str(final_state_2) == order


def test_only_deps_1():
    specs = MatchSpec("numba[build=*py27*]"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.7.5-0',
            'channel-1::llvmpy-0.11.2-py27_0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::numpy-1.7.1-py27_0',
        )
        assert convert_to_dist_str(final_state_1) == order


def test_only_deps_2():
    specs = MatchSpec("numpy=1.5"), MatchSpec("python=2.7.3"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.3-7',
            'channel-1::numpy-1.5.1-py27_4',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = MatchSpec("numba=0.5"),
    with get_solver(specs_to_add) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.7.5-0',
            'channel-1::llvmpy-0.10.0-py27_0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::nose-1.3.0-py27_0',
            'channel-1::numpy-1.7.1-py27_0',
            # 'channel-1::numba-0.5.0-np17py27_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_add = MatchSpec("numba=0.5"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.7.3-7',
            'channel-1::llvmpy-0.10.0-py27_0',
            'channel-1::meta-0.4.2.dev-py27_0',
            'channel-1::nose-1.3.0-py27_0',
            'channel-1::numpy-1.7.1-py27_0',
            # 'channel-1::numba-0.5.0-np17py27_0',
        )
        assert convert_to_dist_str(final_state_2) == order


def test_update_all_1():
    specs = MatchSpec("numpy=1.5"), MatchSpec("python=2.6"), MatchSpec("system[build_number=0]")
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-0',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.6.8-6',
            'channel-1::numpy-1.5.1-py26_4',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = MatchSpec("numba=0.6"), MatchSpec("numpy")
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-0',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.6.8-6',
            'channel-1::llvmpy-0.10.2-py26_0',
            'channel-1::nose-1.3.0-py26_0',
            'channel-1::numpy-1.7.1-py26_0',
            'channel-1::numba-0.6.0-np17py26_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_add = MatchSpec("numba=0.6"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(update_modifier=UpdateModifier.UPDATE_ALL)
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::llvm-3.2-0',
            'channel-1::python-2.6.8-6',  # stick with python=2.6 even though UPDATE_ALL
            'channel-1::llvmpy-0.10.2-py26_0',
            'channel-1::nose-1.3.0-py26_0',
            'channel-1::numpy-1.7.1-py26_0',
            'channel-1::numba-0.6.0-np17py26_0',
        )
        assert convert_to_dist_str(final_state_2) == order


def test_broken_install():
    specs = MatchSpec("pandas"), MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(final_state_1))
        order_original = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numpy-1.6.2-py27_4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::scipy-0.12.0-np16py27_0',
            'channel-1::pandas-0.11.0-np16py27_1',
        )
        assert convert_to_dist_str(final_state_1) == order_original
        assert solver._r.environment_is_consistent(final_state_1)

    # Add an incompatible numpy; installation should be untouched
    final_state_1_modified = list(final_state_1)
    numpy_matcher = MatchSpec("channel-1::numpy==1.7.1=py33_p0")
    numpy_prec = next(prec for prec in solver._index if numpy_matcher.match(prec))
    final_state_1_modified[7] = numpy_prec
    assert not solver._r.environment_is_consistent(final_state_1_modified)

    specs_to_add = MatchSpec("flask"),
    with get_solver(specs_to_add, prefix_records=final_state_1_modified, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            "channel-1::numpy-1.7.1-py33_p0",
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::jinja2-2.6-py27_0',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::scipy-0.12.0-np16py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::werkzeug-0.8.3-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::flask-0.9-py27_0',
            'channel-1::pandas-0.11.0-np16py27_1'
        )
        assert convert_to_dist_str(final_state_2) == order
        assert not solver._r.environment_is_consistent(final_state_2)

    # adding numpy spec again snaps the packages back to a consistent state
    specs_to_add = MatchSpec("flask"), MatchSpec("numpy 1.6.*"),
    with get_solver(specs_to_add, prefix_records=final_state_1_modified, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::jinja2-2.6-py27_0',
            'channel-1::numpy-1.6.2-py27_4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::werkzeug-0.8.3-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::flask-0.9-py27_0',
            'channel-1::scipy-0.12.0-np16py27_0',
            'channel-1::pandas-0.11.0-np16py27_1',
        )
        assert convert_to_dist_str(final_state_2) == order
        assert solver._r.environment_is_consistent(final_state_2)

    # Add an incompatible pandas; installation should be untouched, then fixed
    final_state_2_mod = list(final_state_1)
    pandas_matcher = MatchSpec('channel-1::pandas==0.11.0=np17py27_1')
    pandas_prec = next(prec for prec in solver._index if pandas_matcher.match(prec))
    final_state_2_mod[12] = pandas_prec
    assert not solver._r.environment_is_consistent(final_state_2_mod)

    specs_to_add = MatchSpec("flask"),
    with get_solver(specs_to_add, prefix_records=final_state_2_mod, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::jinja2-2.6-py27_0',
            'channel-1::numpy-1.6.2-py27_4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::werkzeug-0.8.3-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::flask-0.9-py27_0',
            'channel-1::scipy-0.12.0-np16py27_0',
            'channel-1::pandas-0.11.0-np17py27_1',
        )
        assert convert_to_dist_str(final_state_2) == order
        assert not solver._r.environment_is_consistent(final_state_2)

    # adding pandas spec again snaps the packages back to a consistent state
    specs_to_add = MatchSpec("flask"), MatchSpec("pandas"),
    with get_solver(specs_to_add, prefix_records=final_state_2_mod, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::jinja2-2.6-py27_0',
            'channel-1::numpy-1.6.2-py27_4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::werkzeug-0.8.3-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::flask-0.9-py27_0',
            'channel-1::scipy-0.12.0-np16py27_0',
            'channel-1::pandas-0.11.0-np16py27_1',
        )
        assert convert_to_dist_str(final_state_2) == order
        assert solver._r.environment_is_consistent(final_state_2)

    # Actually I think this part might be wrong behavior:
    #    # Removing pandas should fix numpy, since pandas depends on it
    # I think removing pandas should probably leave the broken numpy. That seems more consistent.

    # order_3 = list(order_original)
    # order_1[7] = 'channel-1::numpy-1.7.1-py33_p0'
    # order_3[12] = 'channel-1::pandas-0.11.0-np17py27_1'
    # order_3_records = [index[Dist(d)] for d in order_3]
    # assert not r.environment_is_consistent(order_3)
    #
    # PrefixData._cache_ = {}
    # pd = PrefixData(prefix)
    # pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec)
    #                                   for rec in order_3_records}
    # spec_map = {
    #     "pandas": MatchSpec("pandas"),
    #     "python": MatchSpec("python=2.7"),
    #     "numpy": MatchSpec("numpy 1.6.*"),
    # }
    # with patch.object(History, 'get_requested_specs_map', return_value=spec_map):
    #     solver = Solver(prefix, (Channel('defaults'),), context.subdirs,
    #                     specs_to_remove=(MatchSpec("pandas"),))
    #     solver.index = index
    #     solver.r = r
    #     solver._prepared = True
    #
    #     final_state_2 = solver.solve_final_state()
    #
    #     # PrefixDag(final_state_2, specs).open_url()
    #     print([Dist(rec).full_name for rec in final_state_2])
    #
    #     order = [
    #         'channel-1::openssl-1.0.1c-0',
    #         'channel-1::readline-6.2-0',
    #         'channel-1::sqlite-3.7.13-0',
    #         'channel-1::system-5.8-1',
    #         'channel-1::tk-8.5.13-0',
    #         'channel-1::zlib-1.2.7-0',
    #         'channel-1::python-2.7.5-0',
    #         'channel-1::jinja2-2.6-py27_0',
    #         'channel-1::numpy-1.6.2-py27_4',
    #         'channel-1::pytz-2013b-py27_0',
    #         'channel-1::six-1.3.0-py27_0',
    #         'channel-1::werkzeug-0.8.3-py27_0',
    #         'channel-1::dateutil-2.1-py27_1',
    #         'channel-1::flask-0.9-py27_0',
    #         'channel-1::scipy-0.12.0-np16py27_0',
    #     ]
    #     assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
    #     assert r.environment_is_consistent(order)


def test_install_uninstall_features_1():
    specs = MatchSpec("pandas"), MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with env_var("CONDA_TRACK_FEATURES", 'mkl', reset_context):
        with get_solver(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-1::mkl-rt-11.0-p0',
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-2.7.5-0',
                'channel-1::numpy-1.6.2-py27_p4',
                'channel-1::pytz-2013b-py27_0',
                'channel-1::six-1.3.0-py27_0',
                'channel-1::dateutil-2.1-py27_1',
                'channel-1::scipy-0.12.0-np16py27_p0',
                'channel-1::pandas-0.11.0-np16py27_1',
            )
            assert convert_to_dist_str(final_state_1) == order

    # no more track_features in configuration
    # just remove the pandas package, but the mkl feature "stays in the environment"
    # that is, the current mkl packages aren't switched out
    specs_to_remove = MatchSpec("pandas"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::mkl-rt-11.0-p0',
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numpy-1.6.2-py27_p4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            'channel-1::scipy-0.12.0-np16py27_p0',
        )
        assert convert_to_dist_str(final_state_2) == order

    # now remove the mkl feature
    specs_to_remove = MatchSpec(track_features="mkl"),
    history_specs = MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_2,
                    history_specs=history_specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::numpy-1.6.2-py27_4',
            'channel-1::pytz-2013b-py27_0',
            'channel-1::six-1.3.0-py27_0',
            'channel-1::dateutil-2.1-py27_1',
            # 'channel-1::scipy-0.12.0-np16py27_p0', scipy is out here because it wasn't a requested spec
        )
        assert convert_to_dist_str(final_state_2) == order


def test_install_uninstall_features_2():
    specs = MatchSpec("pandas"), MatchSpec("python=2.7"), MatchSpec("numpy 1.13.*")
    with env_var("CONDA_TRACK_FEATURES", 'nomkl', reset_context):
        with get_solver_4(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-4::ca-certificates-2018.03.07-0',
                'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
                'channel-4::libgfortran-ng-7.2.0-hdf63c60_3',
                'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
                'channel-4::libffi-3.2.1-hd88cf55_4',
                'channel-4::libopenblas-0.2.20-h9ac9557_7',
                'channel-4::ncurses-6.1-hf484d3e_0',
                'channel-4::openssl-1.0.2o-h20670df_0',
                'channel-4::tk-8.6.7-hc745277_3',
                'channel-4::zlib-1.2.11-ha838bed_2',
                'channel-4::libedit-3.1.20170329-h6b74fdf_2',
                'channel-4::readline-7.0-ha6073c6_4',
                'channel-4::sqlite-3.24.0-h84994c4_0',
                'channel-4::python-2.7.15-h1571d57_0',
                'channel-4::numpy-1.13.3-py27_nomklh2b20989_4',  # nomkl
                'channel-4::pytz-2018.4-py27_0',
                'channel-4::six-1.11.0-py27h5f960f1_1',
                'channel-4::python-dateutil-2.7.3-py27_0',
                'channel-4::pandas-0.23.1-py27h637b7d7_0',
            )
            assert convert_to_dist_str(final_state_1) == order

    # no more track_features in configuration
    # just remove the pandas package, but the nomkl feature "stays in the environment"
    # that is, the current nomkl packages aren't switched out
    specs_to_remove = MatchSpec("pandas"),
    with get_solver_4(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                      history_specs=specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()
        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (
            'channel-4::pandas-0.23.1-py27h637b7d7_0',
            # no removal of numpy with nomkl
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order
        link_order = ()
        assert convert_to_dist_str(link_dists) == link_order

    # now remove the nomkl feature
    specs_to_remove = MatchSpec(track_features="nomkl"),
    history_specs = MatchSpec("python=2.7"), MatchSpec("numpy 1.13.*")
    with get_solver_4(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                      history_specs=history_specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()

        pprint(convert_to_dist_str(unlink_dists))
        unlink_order = (
            'channel-4::pandas-0.23.1-py27h637b7d7_0',
            'channel-4::numpy-1.13.3-py27_nomklh2b20989_4',
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        pprint(convert_to_dist_str(link_dists))
        link_order = (
            'channel-4::intel-openmp-2018.0.3-0',
            'channel-4::mkl-2018.0.3-1',
            'channel-4::mkl_fft-1.0.1-py27h3010b51_0',
            'channel-4::mkl_random-1.0.1-py27h629b387_0',
            'channel-4::numpy-1.13.3-py27hdbf6ddf_4',  # numpy with mkl
        )
        assert convert_to_dist_str(link_dists) == link_order


def test_auto_update_conda():
    specs = MatchSpec("conda=1.3"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::yaml-0.1.4-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::pyyaml-3.10-py27_0',
            'channel-1::conda-1.3.5-py27_0',
        )
        assert convert_to_dist_str(final_state_1) == order

    with env_vars({"CONDA_AUTO_UPDATE_CONDA": "yes"}, reset_context):
        specs_to_add = MatchSpec("pytz"),
        with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state()
            # PrefixDag(final_state_2, specs).open_url()
            print(convert_to_dist_str(final_state_2))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::yaml-0.1.4-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-2.7.5-0',
                'channel-1::pytz-2013b-py27_0',
                'channel-1::pyyaml-3.10-py27_0',
                'channel-1::conda-1.3.5-py27_0',
            )
            assert convert_to_dist_str(final_state_2) == order

    with env_vars({"CONDA_AUTO_UPDATE_CONDA": "yes", "CONDA_ROOT_PREFIX": TEST_PREFIX}, reset_context):
        specs_to_add = MatchSpec("pytz"),
        with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state()
            # PrefixDag(final_state_2, specs).open_url()
            print(convert_to_dist_str(final_state_2))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::yaml-0.1.4-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-2.7.5-0',
                'channel-1::pytz-2013b-py27_0',
                'channel-1::pyyaml-3.10-py27_0',
                'channel-1::conda-1.5.2-py27_0',
            )
            assert convert_to_dist_str(final_state_2) == order

    with env_vars({"CONDA_AUTO_UPDATE_CONDA": "no", "CONDA_ROOT_PREFIX": TEST_PREFIX}, reset_context):
        specs_to_add = MatchSpec("pytz"),
        with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state()
            # PrefixDag(final_state_2, specs).open_url()
            print(convert_to_dist_str(final_state_2))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::yaml-0.1.4-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-2.7.5-0',
                'channel-1::pytz-2013b-py27_0',
                'channel-1::pyyaml-3.10-py27_0',
                'channel-1::conda-1.3.5-py27_0',
            )
            assert convert_to_dist_str(final_state_2) == order


def test_aggressive_update_packages():
    def solve(prev_state, specs_to_add, order):
        final_state_1, specs = prev_state
        specs_to_add = tuple(MatchSpec(spec_str) for spec_str in specs_to_add)
        with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state()
            print(convert_to_dist_str(final_state_2))
            assert convert_to_dist_str(final_state_2) == order
        concat_specs = specs + specs_to_add
        return final_state_2, concat_specs
    # test with "libpng", "cmake": both have multiple versions and no requirements in "channel-1"

    empty_state = ((), ())
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": ""}, reset_context):
        base_state = solve(
            empty_state, ["libpng=1.2"],
            (
                'channel-1::libpng-1.2.50-0',
            ))

    # # ~~has "libpng" restricted to "=1.2" by history_specs~~ NOPE!
    # In conda 4.6 making aggressive_update *more* aggressive, making it override history specs.
    state_1 = base_state
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": "libpng"}, reset_context):
        solve(
            state_1, ["cmake=2.8.9"],
            (
                'channel-1::cmake-2.8.9-0',
                'channel-1::libpng-1.5.13-1',
            ))
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": ""}, reset_context):
        state_1_2 = solve(
            state_1, ["cmake=2.8.9"],
            (
                'channel-1::cmake-2.8.9-0',
                'channel-1::libpng-1.2.50-0',
            ))
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": "libpng"}, reset_context):
        solve(
            state_1_2, ["cmake>2.8.9"],
            (
                'channel-1::cmake-2.8.10.2-0',
                'channel-1::libpng-1.5.13-1',
            ))

    # use new history_specs to remove "libpng" version restriction
    state_2 = (base_state[0], (MatchSpec("libpng"),))
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": "libpng"}, reset_context):
        solve(
            state_2, ["cmake=2.8.9"],
            (
                'channel-1::cmake-2.8.9-0',
                'channel-1::libpng-1.5.13-1',
            ))
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": ""}, reset_context):
        state_2_2 = solve(
            state_2, ["cmake=2.8.9"],
            (
                'channel-1::cmake-2.8.9-0',
                'channel-1::libpng-1.2.50-0',
            ))
    with env_vars({"CONDA_AGGRESSIVE_UPDATE_PACKAGES": "libpng"}, reset_context):
        solve(
            state_2_2, ["cmake>2.8.9"],
            (
                'channel-1::cmake-2.8.10.2-0',
                'channel-1::libpng-1.5.13-1',
            ))


def test_update_deps_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        # print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs2 = MatchSpec("numpy=1.7.0"), MatchSpec("python=2.7.3")
    with get_solver(specs2, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.3-7',
            'channel-1::nose-1.3.0-py27_0',
            'channel-1::numpy-1.7.0-py27_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs2) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()
        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (

        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        link_order = (
            'channel-1::unixodbc-2.3.1-0',
            'channel-1::iopro-1.5.0-np17py27_p0',
        )
        assert convert_to_dist_str(link_dists) == link_order

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs2) as solver:
        unlink_dists, link_dists = solver.solve_for_diff(update_modifier=UpdateModifier.UPDATE_DEPS)
        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (
            'channel-1::numpy-1.7.0-py27_0',
            'channel-1::python-2.7.3-7',
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        link_order = (
            'channel-1::unixodbc-2.3.1-0',
            'channel-1::python-2.7.5-0',  # with update_deps, python should switch from 2.7.3 to 2.7.5
            'channel-1::numpy-1.7.1-py27_0',  # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            'channel-1::iopro-1.5.0-np17py27_p0',
        )
        assert convert_to_dist_str(link_dists) == link_order

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs2) as solver:
        unlink_dists, link_dists = solver.solve_for_diff(update_modifier=UpdateModifier.UPDATE_DEPS,
                                                         deps_modifier=DepsModifier.ONLY_DEPS)
        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (
            'channel-1::numpy-1.7.0-py27_0',
            'channel-1::python-2.7.3-7',
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        link_order = (
            'channel-1::unixodbc-2.3.1-0',
            'channel-1::python-2.7.5-0',  # with update_deps, python should switch from 2.7.3 to 2.7.5
            'channel-1::numpy-1.7.1-py27_0',  # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            # 'channel-1::iopro-1.5.0-np17py27_p0', isn't installed because of ONLY_DEPS
        )
        assert convert_to_dist_str(link_dists) == link_order


def test_fast_update_with_update_modifier_not_set():
    specs = MatchSpec("python=2"), MatchSpec("openssl==1.0.2l"), MatchSpec("sqlite=3.21"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(final_state_1))
        order1 = (
            'channel-4::ca-certificates-2018.03.07-0',
            'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4::libffi-3.2.1-hd88cf55_4',
            'channel-4::ncurses-6.0-h9df7e31_2',
            'channel-4::openssl-1.0.2l-h077ae2c_5',
            'channel-4::tk-8.6.7-hc745277_3',
            'channel-4::zlib-1.2.11-ha838bed_2',
            'channel-4::libedit-3.1-heed3624_0',
            'channel-4::readline-7.0-ha6073c6_4',
            'channel-4::sqlite-3.21.0-h1bed415_2',
            'channel-4::python-2.7.14-h89e7a4a_22',
        )
        assert convert_to_dist_str(final_state_1) == order1

    specs_to_add = MatchSpec("python"),
    with get_solver_4(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()

        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (
            'channel-4::python-2.7.14-h89e7a4a_22',
            'channel-4::openssl-1.0.2l-h077ae2c_5',
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        link_order = (
            'channel-4::openssl-1.0.2o-h20670df_0',  # openssl is aggressively updated
            'channel-4::xz-5.2.4-h14c3975_4',
            'channel-4::python-3.6.4-hc3d631a_1',  # python is upgraded
        )
        assert convert_to_dist_str(link_dists) == link_order

    specs_to_add = MatchSpec("sqlite=3.22"),
    with get_solver_4(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()

        pprint(convert_to_dist_str(unlink_dists))
        pprint(convert_to_dist_str(link_dists))
        unlink_order = (
            'channel-4::sqlite-3.21.0-h1bed415_2',
            'channel-4::openssl-1.0.2l-h077ae2c_5',
        )
        assert convert_to_dist_str(unlink_dists) == unlink_order

        link_order = (
            'channel-4::openssl-1.0.2o-h20670df_0',  # openssl is aggressively updated
            'channel-4::sqlite-3.22.0-h1bed415_0',  # sqlite is upgraded
            # python is not upgraded
        )
        assert convert_to_dist_str(link_dists) == link_order

    specs_to_add = MatchSpec("sqlite"), MatchSpec("python"),
    with get_solver_4(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(update_modifier=UpdateModifier.SPECS_SATISFIED_SKIP_SOLVE)
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        assert convert_to_dist_str(final_state_2) == order1


def test_pinned_1():
    specs = MatchSpec("numpy"),
    with get_solver(specs) as solver:
        final_state_0 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(final_state_0))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-3.3.2-0',
            'channel-1::numpy-1.7.1-py33_0',
        )
        assert convert_to_dist_str(final_state_0) == order

    with env_var("CONDA_PINNED_PACKAGES", "python=2.6&iopro<=1.4.2", reset_context):
        specs = MatchSpec("system=5.8=0"),
        with get_solver(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-1::system-5.8-0',
                # pinned packages are optional, so they don't come into this solution
            )
            assert convert_to_dist_str(final_state_1) == order

        # solve with ignore_pinned=True
        specs_to_add = MatchSpec("python"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_1,
                        history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state(ignore_pinned=True)
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_2))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-0',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-3.3.2-0',
            )
            assert convert_to_dist_str(final_state_2) == order

        # solve with ignore_pinned=False
        specs_to_add = MatchSpec("python"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_1,
                        history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state(ignore_pinned=False)
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_2))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-0',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::python-2.6.8-6',
            )
            assert convert_to_dist_str(final_state_2) == order

        specs_to_add = MatchSpec("numba"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_2,
                        history_specs=history_specs) as solver:
            final_state_3 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_3))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-0',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::llvm-3.2-0',
                'channel-1::python-2.6.8-6',
                'channel-1::argparse-1.2.1-py26_0',
                'channel-1::llvmpy-0.11.2-py26_0',
                'channel-1::numpy-1.7.1-py26_0',
                'channel-1::numba-0.8.1-np17py26_0',
            )
            assert convert_to_dist_str(final_state_3) == order

        specs_to_add = MatchSpec("python"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_3,
                        history_specs=history_specs) as solver:
            final_state_4 = solver.solve_final_state(update_modifier=UpdateModifier.UPDATE_DEPS)
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_4))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::llvm-3.2-0',
                'channel-1::python-2.6.8-6',
                'channel-1::argparse-1.2.1-py26_0',
                'channel-1::llvmpy-0.11.2-py26_0',
                'channel-1::numpy-1.7.1-py26_0',
                'channel-1::numba-0.8.1-np17py26_0',
            )
            assert convert_to_dist_str(final_state_4) == order

        specs_to_add = MatchSpec("python"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_4,
                        history_specs=history_specs) as solver:
            final_state_5 = solver.solve_final_state(update_modifier=UpdateModifier.UPDATE_ALL)
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_5))
            order = (
                'channel-1::openssl-1.0.1c-0',
                'channel-1::readline-6.2-0',
                'channel-1::sqlite-3.7.13-0',
                'channel-1::system-5.8-1',
                'channel-1::tk-8.5.13-0',
                'channel-1::zlib-1.2.7-0',
                'channel-1::llvm-3.2-0',
                'channel-1::python-2.6.8-6',
                'channel-1::argparse-1.2.1-py26_0',
                'channel-1::llvmpy-0.11.2-py26_0',
                'channel-1::numpy-1.7.1-py26_0',
                'channel-1::numba-0.8.1-np17py26_0',
            )
            assert convert_to_dist_str(final_state_5) == order

    # # TODO: re-enable when UPDATE_ALL gets prune behavior again, following completion of https://github.com/conda/constructor/issues/138
    # # now update without pinning
    # specs_to_add = MatchSpec("python"),
    # history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
    # with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_4,
    #                 history_specs=history_specs) as solver:
    #     final_state_5 = solver.solve_final_state(update_modifier=UpdateModifier.UPDATE_ALL)
    #     # PrefixDag(final_state_1, specs).open_url()
    #     print([Dist(rec).full_name for rec in final_state_5])
    #     order = (
    #         'channel-1::openssl-1.0.1c-0',
    #         'channel-1::readline-6.2-0',
    #         'channel-1::sqlite-3.7.13-0',
    #         'channel-1::system-5.8-1',
    #         'channel-1::tk-8.5.13-0',
    #         'channel-1::zlib-1.2.7-0',
    #         'channel-1::llvm-3.2-0',
    #         'channel-1::python-3.3.2-0',
    #         'channel-1::llvmpy-0.11.2-py33_0',
    #         'channel-1::numpy-1.7.1-py33_0',
    #         'channel-1::numba-0.8.1-np17py33_0',
    #     )
    #     assert tuple(final_state_5) == tuple(solver._index[Dist(d)] for d in order)


def test_no_update_deps_1():  # i.e. FREEZE_DEPS
    # NOTE: So far, NOT actually testing the FREEZE_DEPS flag.  I'm unable to contrive a
    # situation where it's actually needed.

    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = MatchSpec("zope.interface"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
            'channel-1::nose-1.3.0-py27_0',
            'channel-1::zope.interface-4.0.5-py27_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    specs_to_add = MatchSpec("zope.interface>4.1"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-3.3.2-0',
            'channel-1::nose-1.3.0-py33_0',
            'channel-1::zope.interface-4.1.1.1-py33_0',
        )
        assert convert_to_dist_str(final_state_2) == order


def test_force_reinstall_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = specs
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()
        assert not unlink_dists
        assert not link_dists

        unlink_dists, link_dists = solver.solve_for_diff(force_reinstall=True)
        assert len(unlink_dists) == len(link_dists) == 1
        assert unlink_dists[0] == link_dists[0]

        unlink_dists, link_dists = solver.solve_for_diff()
        assert not unlink_dists
        assert not link_dists


def test_force_reinstall_2():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff(force_reinstall=True)
        assert not unlink_dists
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(link_dists))
        order = (
            'channel-1::openssl-1.0.1c-0',
            'channel-1::readline-6.2-0',
            'channel-1::sqlite-3.7.13-0',
            'channel-1::system-5.8-1',
            'channel-1::tk-8.5.13-0',
            'channel-1::zlib-1.2.7-0',
            'channel-1::python-2.7.5-0',
        )
        assert convert_to_dist_str(link_dists) == order


def test_timestamps_1():
    specs = MatchSpec("python=3.6.2"),
    with get_solver_4(specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff(force_reinstall=True)
        assert not unlink_dists
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(link_dists))
        order = (
            'channel-4::ca-certificates-2018.03.07-0',
            'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4::libffi-3.2.1-hd88cf55_4',
            'channel-4::ncurses-6.0-h9df7e31_2',
            'channel-4::openssl-1.0.2o-h20670df_0',
            'channel-4::tk-8.6.7-hc745277_3',
            'channel-4::xz-5.2.4-h14c3975_4',
            'channel-4::zlib-1.2.11-ha838bed_2',
            'channel-4::libedit-3.1-heed3624_0',
            'channel-4::readline-7.0-ha6073c6_4',
            'channel-4::sqlite-3.23.1-he433501_0',
            'channel-4::python-3.6.2-hca45abc_19',  # this package has a later timestamp but lower hash value
                                                    # than the alternate 'channel-4::python-3.6.2-hda45abc_19'
        )
        assert convert_to_dist_str(link_dists) == order


def test_remove_with_constrained_dependencies():
    # This is a regression test for #6904. Up through conda 4.4.10, removal isn't working
    # correctly with constrained dependencies.
    specs = MatchSpec("conda"), MatchSpec("conda-build"),
    with get_solver_4(specs) as solver:
        unlink_dists_1, link_dists_1 = solver.solve_for_diff()
        assert not unlink_dists_1
        # PrefixDag(final_state_1, specs).open_url()
        pprint(convert_to_dist_str(link_dists_1))
        assert not unlink_dists_1
        order = (
            'channel-4::ca-certificates-2018.03.07-0',
            'channel-4::conda-env-2.6.0-h36134e3_1',
            'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4::libffi-3.2.1-hd88cf55_4',
            'channel-4::ncurses-6.1-hf484d3e_0',
            'channel-4::openssl-1.0.2o-h20670df_0',
            'channel-4::patchelf-0.9-hf79760b_2',
            'channel-4::tk-8.6.7-hc745277_3',
            'channel-4::xz-5.2.4-h14c3975_4',
            'channel-4::yaml-0.1.7-had09818_2',
            'channel-4::zlib-1.2.11-ha838bed_2',
            'channel-4::libedit-3.1.20170329-h6b74fdf_2',
            'channel-4::readline-7.0-ha6073c6_4',
            'channel-4::sqlite-3.24.0-h84994c4_0',
            'channel-4::python-3.6.6-hc3d631a_0',
            'channel-4::asn1crypto-0.24.0-py36_0',
            'channel-4::beautifulsoup4-4.6.0-py36h49b8c8c_1',
            'channel-4::certifi-2018.4.16-py36_0',
            'channel-4::chardet-3.0.4-py36h0f667ec_1',
            'channel-4::filelock-3.0.4-py36_0',
            'channel-4::glob2-0.6-py36he249c77_0',
            'channel-4::idna-2.7-py36_0',
            'channel-4::markupsafe-1.0-py36hd9260cd_1',
            'channel-4::pkginfo-1.4.2-py36_1',
            'channel-4::psutil-5.4.6-py36h14c3975_0',
            'channel-4::pycosat-0.6.3-py36h0a5515d_0',
            'channel-4::pycparser-2.18-py36hf9f622e_1',
            'channel-4::pysocks-1.6.8-py36_0',
            'channel-4::pyyaml-3.12-py36hafb9ca4_1',
            'channel-4::ruamel_yaml-0.15.40-py36h14c3975_2',
            'channel-4::six-1.11.0-py36h372c433_1',
            'channel-4::cffi-1.11.5-py36h9745a5d_0',
            'channel-4::conda-verify-2.0.0-py36h98955d8_0',
            'channel-4::setuptools-39.2.0-py36_0',
            'channel-4::cryptography-2.2.2-py36h14c3975_0',
            'channel-4::jinja2-2.10-py36ha16c418_0',
            'channel-4::pyopenssl-18.0.0-py36_0',
            'channel-4::urllib3-1.23-py36_0',
            'channel-4::requests-2.19.1-py36_0',
            'channel-4::conda-4.5.4-py36_0',
            'channel-4::conda-build-3.10.9-py36_0'
        )
        assert convert_to_dist_str(link_dists_1) == order

    specs_to_remove = MatchSpec("pycosat"),
    with get_solver_4(specs_to_remove=specs_to_remove, prefix_records=link_dists_1, history_specs=specs) as solver:
        unlink_dists_2, link_dists_2 = solver.solve_for_diff()
        assert not link_dists_2
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(unlink_dists_2))
        order = (
            'channel-4::conda-build-3.10.9-py36_0',
            'channel-4::conda-4.5.4-py36_0',
            'channel-4::pycosat-0.6.3-py36h0a5515d_0',
        )
        assert convert_to_dist_str(unlink_dists_2) == order


def test_priority_1():
    specs = (MatchSpec("pandas"), MatchSpec("python=2.7"))
    with env_var("CONDA_CHANNEL_PRIORITY", "True", reset_context):
        with get_solver_aggregate_1(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-2::mkl-2017.0.1-0',
                'channel-2::openssl-1.0.2l-0',
                'channel-2::readline-6.2-2',
                'channel-2::sqlite-3.13.0-0',
                'channel-2::tk-8.5.18-0',
                'channel-2::zlib-1.2.8-3',
                'channel-2::python-2.7.13-0',
                'channel-2::numpy-1.13.0-py27_0',
                'channel-2::pytz-2017.2-py27_0',
                'channel-2::six-1.10.0-py27_0',
                'channel-2::python-dateutil-2.6.0-py27_0',
                'channel-2::pandas-0.20.2-np113py27_0',
            )
            assert convert_to_dist_str(final_state_1) == order

    with env_var("CONDA_CHANNEL_PRIORITY", "False", reset_context):
        with get_solver_aggregate_1(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-4::blas-1.0-mkl',
                'channel-4::ca-certificates-2018.03.07-0',
                'channel-4::intel-openmp-2018.0.3-0',
                'channel-2::libffi-3.2.1-1',
                'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
                'channel-4::libgfortran-ng-7.2.0-hdf63c60_3',
                'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
                'channel-4::mkl-2018.0.3-1',
                'channel-4::ncurses-6.1-hf484d3e_0',
                'channel-4::openssl-1.0.2o-h20670df_0',
                'channel-4::tk-8.6.7-hc745277_3',
                'channel-4::zlib-1.2.11-ha838bed_2',
                'channel-4::libedit-3.1.20170329-h6b74fdf_2',
                'channel-4::readline-7.0-ha6073c6_4',
                'channel-4::sqlite-3.24.0-h84994c4_0',
                'channel-4::python-2.7.15-h1571d57_0',
                'channel-4::numpy-base-1.14.5-py27hdbf6ddf_0',
                'channel-4::pytz-2018.4-py27_0',
                'channel-4::six-1.11.0-py27h5f960f1_1',
                'channel-4::python-dateutil-2.7.3-py27_0',
                'channel-4::mkl_fft-1.0.1-py27h3010b51_0',
                'channel-4::mkl_random-1.0.1-py27h629b387_0',
                'channel-4::numpy-1.14.5-py27hcd700cb_0',
                'channel-4::pandas-0.23.1-py27h637b7d7_0',
            )
            assert convert_to_dist_str(final_state_1) == order


def test_features_solve_1():
    # in this test, channel-2 is a view of pkgs/free/linux-64
    #   and channel-4 is a view of the newer pkgs/main/linux-64
    # The channel list, equivalent to context.channels is ('channel-2', 'channel-4')
    specs = (MatchSpec("python=2.7"), MatchSpec("numpy"), MatchSpec("nomkl"))
    with env_var("CONDA_CHANNEL_PRIORITY", "True", reset_context):
        with get_solver_aggregate_1(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-2::nomkl-1.0-0',
                'channel-2::libgfortran-3.0.0-1',
                'channel-2::openssl-1.0.2l-0',
                'channel-2::readline-6.2-2',
                'channel-2::sqlite-3.13.0-0',
                'channel-2::tk-8.5.18-0',
                'channel-2::zlib-1.2.8-3',
                'channel-2::openblas-0.2.19-0',
                'channel-2::python-2.7.13-0',
                'channel-2::numpy-1.13.0-py27_nomkl_0',
            )
            assert convert_to_dist_str(final_state_1) == order

    with env_var("CONDA_CHANNEL_PRIORITY", "False", reset_context):
        with get_solver_aggregate_1(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            pprint(convert_to_dist_str(final_state_1))
            order = (
                'channel-4::blas-1.0-openblas',
                'channel-4::ca-certificates-2018.03.07-0',
                'channel-2::libffi-3.2.1-1',  # libffi comes from channel-2
                'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
                'channel-4::libgfortran-ng-7.2.0-hdf63c60_3',
                'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
                'channel-4::libopenblas-0.2.20-h9ac9557_7',
                'channel-4::ncurses-6.1-hf484d3e_0',
                'channel-4::nomkl-3.0-0',
                'channel-4::openssl-1.0.2o-h20670df_0',
                'channel-4::tk-8.6.7-hc745277_3',
                'channel-4::zlib-1.2.11-ha838bed_2',
                'channel-4::libedit-3.1.20170329-h6b74fdf_2',
                'channel-4::readline-7.0-ha6073c6_4',
                'channel-4::sqlite-3.24.0-h84994c4_0',
                'channel-4::python-2.7.15-h1571d57_0',
                'channel-4::numpy-base-1.14.5-py27h2b20989_0',
                'channel-4::numpy-1.14.5-py27h28100ab_0'
            )
            assert convert_to_dist_str(final_state_1) == order


@pytest.mark.integration  # this test is slower, so we'll lump it into integration
def test_freeze_deps_1():
    specs = MatchSpec("six=1.7"),
    with get_solver_2(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print(convert_to_dist_str(final_state_1))
        order = (
            'channel-2::openssl-1.0.2l-0',
            'channel-2::readline-6.2-2',
            'channel-2::sqlite-3.13.0-0',
            'channel-2::tk-8.5.18-0',
            'channel-2::xz-5.2.2-1',
            'channel-2::zlib-1.2.8-3',
            'channel-2::python-3.4.5-0',
            'channel-2::six-1.7.3-py34_0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs_to_add = MatchSpec("bokeh"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        pprint(convert_to_dist_str(final_state_2))
        order = (
            'channel-2::mkl-2017.0.1-0',
            'channel-2::openssl-1.0.2l-0',
            'channel-2::readline-6.2-2',
            'channel-2::sqlite-3.13.0-0',
            'channel-2::tk-8.5.18-0',
            'channel-2::xz-5.2.2-1',
            'channel-2::yaml-0.1.6-0',
            'channel-2::zlib-1.2.8-3',
            'channel-2::python-3.4.5-0',
            'channel-2::backports_abc-0.5-py34_0',
            'channel-2::markupsafe-0.23-py34_2',
            'channel-2::numpy-1.13.0-py34_0',
            'channel-2::pyyaml-3.12-py34_0',
            'channel-2::requests-2.14.2-py34_0',
            'channel-2::setuptools-27.2.0-py34_0',
            'channel-2::six-1.7.3-py34_0',
            'channel-2::python-dateutil-2.6.0-py34_0',
            'channel-2::jinja2-2.9.6-py34_0',
            'channel-2::tornado-4.4.2-py34_0',
            'channel-2::bokeh-0.12.4-py34_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    # now we can't install the latest bokeh 0.12.5, but instead we get bokeh 0.12.4
    specs_to_add = MatchSpec("bokeh"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-2::mkl-2017.0.1-0',
            'channel-2::openssl-1.0.2l-0',
            'channel-2::readline-6.2-2',
            'channel-2::sqlite-3.13.0-0',
            'channel-2::tk-8.5.18-0',
            'channel-2::xz-5.2.2-1',
            'channel-2::yaml-0.1.6-0',
            'channel-2::zlib-1.2.8-3',
            'channel-2::python-3.4.5-0',
            'channel-2::backports_abc-0.5-py34_0',
            'channel-2::markupsafe-0.23-py34_2',
            'channel-2::numpy-1.13.0-py34_0',
            'channel-2::pyyaml-3.12-py34_0',
            'channel-2::requests-2.14.2-py34_0',
            'channel-2::setuptools-27.2.0-py34_0',
            'channel-2::six-1.7.3-py34_0',
            'channel-2::python-dateutil-2.6.0-py34_0',
            'channel-2::jinja2-2.9.6-py34_0',
            'channel-2::tornado-4.4.2-py34_0',
            'channel-2::bokeh-0.12.4-py34_0',
        )
        assert convert_to_dist_str(final_state_2) == order

    # here, the python=3.4 spec can't be satisfied, so it's dropped, and we go back to py27
    specs_to_add = MatchSpec("bokeh=0.12.5"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print(convert_to_dist_str(final_state_2))
        order = (
            'channel-2::xz-5.2.2-1',
            'channel-2::mkl-2017.0.1-0',
            'channel-2::openssl-1.0.2l-0',
            'channel-2::readline-6.2-2',
            'channel-2::sqlite-3.13.0-0',
            'channel-2::tk-8.5.18-0',
            'channel-2::yaml-0.1.6-0',
            'channel-2::zlib-1.2.8-3',
            'channel-2::python-2.7.13-0',
            'channel-2::backports-1.0-py27_0',
            'channel-2::backports_abc-0.5-py27_0',
            'channel-2::futures-3.1.1-py27_0',
            'channel-2::markupsafe-0.23-py27_2',
            'channel-2::numpy-1.13.0-py27_0',
            'channel-2::pyyaml-3.12-py27_0',
            'channel-2::requests-2.14.2-py27_0',
            'channel-2::setuptools-27.2.0-py27_0',
            'channel-2::six-1.7.3-py27_0',
            'channel-2::python-dateutil-2.6.0-py27_0',
            'channel-2::jinja2-2.9.6-py27_0',
            'channel-2::singledispatch-3.4.0.3-py27_0',
            'channel-2::ssl_match_hostname-3.4.0.2-py27_1',
            'channel-2::tornado-4.5.1-py27_0',
            'channel-2::bokeh-0.12.5-py27_1',
        )
        assert convert_to_dist_str(final_state_2) == order

    # here, the python=3.4 spec can't be satisfied, so it's dropped, and we go back to py27
    specs_to_add = MatchSpec("bokeh=0.12.5"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        with pytest.raises(UnsatisfiableError):
            solver.solve_final_state(update_modifier=UpdateModifier.FREEZE_INSTALLED)


def test_namespace_package_rename_1():
    specs = MatchSpec("python-dateutil"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_dist_str(final_state_1))
        order = (
            'channel-4::ca-certificates-2018.03.07-0',
            'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4::libffi-3.2.1-hd88cf55_4',
            'channel-4::ncurses-6.1-hf484d3e_0',
            'channel-4::openssl-1.0.2o-h20670df_0',
            'channel-4::tk-8.6.7-hc745277_3',
            'channel-4::xz-5.2.4-h14c3975_4',
            'channel-4::zlib-1.2.11-ha838bed_2',
            'channel-4::libedit-3.1.20170329-h6b74fdf_2',
            'channel-4::readline-7.0-ha6073c6_4',
            'channel-4::sqlite-3.24.0-h84994c4_0',
            'channel-4::python-3.6.6-hc3d631a_0',
            'channel-4::six-1.11.0-py36h372c433_1',
            'channel-4::python-dateutil-2.7.3-py36_0',
        )
        assert convert_to_dist_str(final_state_1) == order

    specs = MatchSpec("python:dateutil"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_dist_str(final_state_1))
        assert convert_to_dist_str(final_state_1) == order

    specs = MatchSpec("dateutil"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_dist_str(final_state_1))
        assert convert_to_dist_str(final_state_1) == order


def test_namespace_create_ambiguous_namespace():
    # solution should contain global:graphviz only
    specs = MatchSpec("global:graphviz"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz only
    specs = MatchSpec("graphviz"),
    with get_solver_4(specs) as solver:
        final_state_2 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_2))
        assert final_state_2 == final_state_1

    # solution should contain global:graphviz and python:graphviz
    specs = MatchSpec("python:graphviz"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz and python:graphviz
    specs = MatchSpec("ibis-framework"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:blas-1.0-mkl',
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:intel-openmp-2018.0.3-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libgfortran-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:mkl-2018.0.3-1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:krb5-1.16.1-hc83ff2d_6',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:libpq-10.3-h1ad7b7a_0',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:python:bitarray-0.8.2-py36h14c3975_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:python:certifi-2018.4.16-py36_0',
            'channel-4:python:multipledispatch-0.5.0-py36_0',
            'channel-4:python:numpy-base-1.14.5-py36hdbf6ddf_0',
            'channel-4:python:ply-3.11-py36_0',
            'channel-4:python:psycopg2-2.7.5-py36hb7f436b_0',
            'channel-4:python:pytz-2018.4-py36_0',
            'channel-4:python:six-1.11.0-py36h372c433_1',
            'channel-4:python:sqlalchemy-1.2.8-py36h14c3975_0',
            'channel-4:python:toolz-0.9.0-py36_0',
            'channel-4:python:dateutil-2.7.3-py36_0',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:python:setuptools-39.2.0-py36_0',
            'channel-4:python:thrift-0.11.0-py36hf484d3e_0',
            'channel-4:python:thriftpy-0.3.9-py36h14c3975_1',
            'channel-4:python:impyla-0.14.1-py36_0',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
            'channel-4:python:mkl_fft-1.0.1-py36h3010b51_0',
            'channel-4:python:mkl_random-1.0.1-py36h629b387_0',
            'channel-4:python:numpy-1.14.5-py36hcd700cb_0',
            'channel-4:python:pandas-0.23.1-py36h637b7d7_0',
            'channel-4:python:ibis-framework-0.12.0-py36h5db9e08_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz and python:graphviz
    specs = MatchSpec("graphviz"), MatchSpec("itsdangerous"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:python:itsdangerous-0.24-py36h93cc618_1',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain python:digest, r:digest
    specs = MatchSpec("digest"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:_r-mutex-1.0.0-mro_2',
            'channel-4:global:binutils_impl_linux-64-2.28.1-had2808c_3',
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libgfortran-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:binutils_linux-64-7.2.0-had2808c_27',
            'channel-4:global:fribidi-1.0.4-h14c3975_0',
            'channel-4:global:gcc_impl_linux-64-7.2.0-habb00fd_3',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libuuid-1.0.3-h1bed415_2',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:gcc_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gfortran_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:gxx_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libssh2-1.8.0-h9cfc8f7_4',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:freetype-2.9.1-h8a8886c_0',
            'channel-4:global:gfortran_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gxx_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:libcurl-7.60.0-h1ad7b7a_0',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:curl-7.60.0-h84994c4_0',
            'channel-4:global:fontconfig-2.13.0-h9420a91_0',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:python:asn1crypto-0.24.0-py36_0',
            'channel-4:global:cairo-1.14.12-h8948797_3',
            'channel-4:python:idna-2.7-py36_0',
            'channel-4:python:pycparser-2.18-py36hf9f622e_1',
            'channel-4:python:six-1.11.0-py36h372c433_1',
            'channel-4:python:cffi-1.11.5-py36h9745a5d_0',
            'channel-4:global:harfbuzz-1.7.6-hec2c2bc_3',
            'channel-4:python:cryptography-2.1.4-py36hd09be54_0',
            'channel-4:global:pango-1.42.1-h8589676_0',
            'channel-4:python:digest-1.1.1-py3_0',
            'channel-4:global:mro-base-3.4.3-h1c2f66e_1',
            'channel-4:r:digest-0.6.13-mro343h086d26f_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz, python:graphviz, r:graphviz, python:digest, r:digest
    specs = MatchSpec("graphviz"), MatchSpec("digest"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:_r-mutex-1.0.0-mro_2',
            'channel-4:global:binutils_impl_linux-64-2.28.1-had2808c_3',
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libgfortran-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:binutils_linux-64-7.2.0-had2808c_27',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:gcc_impl_linux-64-7.2.0-habb00fd_3',
            'channel-4:global:gmp-6.1.2-h6c8ec71_1',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:gcc_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gfortran_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:gxx_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:isl-0.12.2-0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libssh2-1.8.0-h9cfc8f7_4',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:mpfr-3.1.5-h11a74b3_2',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:cloog-0.18.0-0',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:gfortran_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gxx_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:libcurl-7.60.0-h1ad7b7a_0',
            'channel-4:global:mpc-1.0.3-hec55b23_5',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:curl-7.60.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:gcc-4.8.5-7',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:python:asn1crypto-0.24.0-py36_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:python:idna-2.7-py36_0',
            'channel-4:python:pycparser-2.18-py36hf9f622e_1',
            'channel-4:python:six-1.11.0-py36h372c433_1',
            'channel-4:python:cffi-1.11.5-py36h9745a5d_0',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:python:cryptography-2.1.4-py36hd09be54_0',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:python:digest-1.1.1-py3_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:global:mro-base-3.4.3-h1c2f66e_1',
            'channel-4:global:r-3.1.2-2',
            'channel-4:r:digest-0.6.13-mro343h086d26f_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
            'channel-4:r:graphviz-8.9.10-r_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz, python:graphviz, python:digest
    specs = MatchSpec("graphviz"), MatchSpec("digest"), MatchSpec("itsdangerous"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:python:asn1crypto-0.24.0-py36_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:python:idna-2.7-py36_0',
            'channel-4:python:itsdangerous-0.24-py36h93cc618_1',
            'channel-4:python:pycparser-2.18-py36hf9f622e_1',
            'channel-4:python:six-1.11.0-py36h372c433_1',
            'channel-4:python:cffi-1.11.5-py36h9745a5d_0',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:python:cryptography-2.1.4-py36hd09be54_0',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:python:digest-1.1.1-py3_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
        )
        assert convert_to_record_id(final_state_1) == order

    # solution should contain global:graphviz, python:graphviz, python:digest, r:graphviz, r:digest, r:mime
    specs = MatchSpec("graphviz"), MatchSpec("digest"), MatchSpec("itsdangerous"), MatchSpec("mime"),
    with get_solver_4(specs) as solver:
        final_state_1 = solver.solve_final_state()
        pprint(convert_to_record_id(final_state_1))
        order = (
            'channel-4:global:_r-mutex-1.0.0-mro_2',
            'channel-4:global:binutils_impl_linux-64-2.28.1-had2808c_3',
            'channel-4:global:ca-certificates-2018.03.07-0',
            'channel-4:global:libgcc-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libgfortran-ng-7.2.0-hdf63c60_3',
            'channel-4:global:libstdcxx-ng-7.2.0-hdf63c60_3',
            'channel-4:global:binutils_linux-64-7.2.0-had2808c_27',
            'channel-4:global:expat-2.2.5-he0dffb1_0',
            'channel-4:global:gcc_impl_linux-64-7.2.0-habb00fd_3',
            'channel-4:global:gmp-6.1.2-h6c8ec71_1',
            'channel-4:global:graphite2-1.3.11-h16798f4_2',
            'channel-4:global:icu-58.2-h9c2bf20_1',
            'channel-4:global:jpeg-9b-h024ee3a_2',
            'channel-4:global:libffi-3.2.1-hd88cf55_4',
            'channel-4:global:libtool-2.4.6-h544aabb_3',
            'channel-4:global:libxcb-1.13-h1bed415_1',
            'channel-4:global:ncurses-6.1-hf484d3e_0',
            'channel-4:global:openssl-1.0.2o-h20670df_0',
            'channel-4:global:pcre-8.42-h439df22_0',
            'channel-4:global:pixman-0.34.0-hceecf20_3',
            'channel-4:global:tk-8.6.7-hc745277_3',
            'channel-4:global:xz-5.2.4-h14c3975_4',
            'channel-4:global:zlib-1.2.11-ha838bed_2',
            'channel-4:global:gcc_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gfortran_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:glib-2.56.1-h000015b_0',
            'channel-4:global:gxx_impl_linux-64-7.2.0-hdf63c60_3',
            'channel-4:global:isl-0.12.2-0',
            'channel-4:global:libedit-3.1.20170329-h6b74fdf_2',
            'channel-4:global:libpng-1.6.34-hb9fc6fc_0',
            'channel-4:global:libssh2-1.8.0-h9cfc8f7_4',
            'channel-4:global:libtiff-4.0.9-he85c1e1_1',
            'channel-4:global:libxml2-2.9.8-h26e45fe_1',
            'channel-4:global:mpfr-3.1.5-h11a74b3_2',
            'channel-4:global:readline-7.0-ha6073c6_4',
            'channel-4:global:cloog-0.18.0-0',
            'channel-4:global:freetype-2.8-hab7d2ae_1',
            'channel-4:global:gfortran_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:gxx_linux-64-7.2.0-h550dcbe_27',
            'channel-4:global:libcurl-7.60.0-h1ad7b7a_0',
            'channel-4:global:mpc-1.0.3-hec55b23_5',
            'channel-4:global:sqlite-3.24.0-h84994c4_0',
            'channel-4:global:curl-7.60.0-h84994c4_0',
            'channel-4:global:fontconfig-2.12.6-h49f89f6_0',
            'channel-4:global:gcc-4.8.5-7',
            'channel-4:global:python-3.6.6-hc3d631a_0',
            'channel-4:python:asn1crypto-0.24.0-py36_0',
            'channel-4:global:cairo-1.14.12-h7636065_2',
            'channel-4:python:idna-2.7-py36_0',
            'channel-4:python:itsdangerous-0.24-py36h93cc618_1',
            'channel-4:python:pycparser-2.18-py36hf9f622e_1',
            'channel-4:python:six-1.11.0-py36h372c433_1',
            'channel-4:python:cffi-1.11.5-py36h9745a5d_0',
            'channel-4:global:harfbuzz-1.7.6-h5f0a787_1',
            'channel-4:python:cryptography-2.1.4-py36hd09be54_0',
            'channel-4:global:pango-1.41.0-hd475d92_0',
            'channel-4:python:digest-1.1.1-py3_0',
            'channel-4:global:graphviz-2.40.1-h25d223c_0',
            'channel-4:global:mro-base-3.4.3-h1c2f66e_1',
            'channel-4:global:r-3.1.2-2',
            'channel-4:r:digest-0.6.13-mro343h086d26f_0',
            'channel-4:r:mime-0.5-mro343h086d26f_0',
            'channel-4:python:graphviz-0.8.3-py36_0',
            'channel-4:r:graphviz-8.9.10-r_0',
        )
        assert convert_to_record_id(final_state_1) == order


# def test_namespace_1():
#     specs = MatchSpec("python"), MatchSpec("perl"),
#     with get_solver_4(specs) as solver:
#         final_state_1 = solver.solve_final_state()
#         pprint(convert_to_dist_str(final_state_1))
#         order = (
#             'channel-4::ca-certificates-2018.03.07-0',
#             'channel-4::libgcc-ng-7.2.0-hdf63c60_3',
#             'channel-4::libstdcxx-ng-7.2.0-hdf63c60_3',
#             'channel-4::libffi-3.2.1-hd88cf55_4',
#             'channel-4::ncurses-6.1-hf484d3e_0',
#             'channel-4::openssl-1.0.2o-h20670df_0',
#             'channel-4::perl-5.26.2-h14c3975_0',
#             'channel-4::tk-8.6.7-hc745277_3',
#             'channel-4::xz-5.2.4-h14c3975_4',
#             'channel-4::zlib-1.2.11-ha838bed_2',
#             'channel-4::libedit-3.1.20170329-h6b74fdf_2',
#             'channel-4::readline-7.0-ha6073c6_4',
#             'channel-4::sqlite-3.24.0-h84994c4_0',
#             'channel-4::python-3.6.5-hc3d631a_2'
#         )
#         assert convert_to_dist_str(final_state_1) == order
#
#     specs_to_add = MatchSpec("graphviz"), MatchSpec("python-graphviz"), MatchSpec("perl-graphviz")
#     with get_solver_4(specs_to_add=specs_to_add, prefix_records=final_state_1,
#                       history_specs=specs) as solver:
#         unlink_dists, link_dists = solver.solve_for_diff()
#
#         pprint(convert_to_dist_str(unlink_dists))
#         unlink_order = (
#
#         )
#         assert convert_to_dist_str(unlink_dists) == unlink_order
#
#         pprint(convert_to_dist_str(link_dists))
#         link_order = (
#             'channel-4::perl-threaded-5.22.0-10',
#             'channel-4::tidyp-1.04-1',
#             'channel-4::expat-2.2.5-he0dffb1_0',
#             'channel-4::graphite2-1.3.11-h16798f4_2',
#             'channel-4::icu-58.2-h9c2bf20_1',
#             'channel-4::jpeg-9b-h024ee3a_2',
#             'channel-4::libgcc-7.2.0-h69d50b8_2',
#             'channel-4::libtool-2.4.6-h544aabb_3',
#             'channel-4::libxcb-1.13-h1bed415_1',
#             'channel-4::pcre-8.42-h439df22_0',
#             'channel-4::perl-digest-hmac-1.03-0',
#             'channel-4::perl-file-which-1.20-0',
#             'channel-4::perl-font-afm-1.20-0',
#             'channel-4::perl-html-entities-numbered-0.04-0',
#             'channel-4::perl-html-tagset-3.20-0',
#             'channel-4::perl-html-tidy-1.56-1',
#             'channel-4::perl-http-date-6.02-0',
#             'channel-4::perl-io-html-1.001-0',
#             'channel-4::perl-io-tty-1.12-0',
#             'channel-4::perl-lwp-mediatypes-6.02-0',
#             'channel-4::perl-parse-recdescent-1.967013-0',
#             'channel-4::perl-test-pod-1.51-0',
#             'channel-4::perl-tie-ixhash-1.23-0',
#             'channel-4::perl-uri-1.71-0',
#             'channel-4::perl-xml-xpathengine-0.14-0',
#             'channel-4::pixman-0.34.0-hceecf20_3',
#             'channel-4::glib-2.56.1-h000015b_0',
#             'channel-4::libpng-1.6.34-hb9fc6fc_0',
#             'channel-4::libtiff-4.0.9-he85c1e1_1',
#             'channel-4::libxml2-2.9.8-h26e45fe_1',
#             'channel-4::perl-encode-locale-1.05-3',
#             'channel-4::perl-file-listing-6.04-0',
#             'channel-4::perl-html-parser-3.72-0',
#             'channel-4::perl-ipc-run-0.94-0',
#             'channel-4::perl-net-ssleay-1.74-0',
#             'channel-4::perl-ntlm-1.09-1',
#             'channel-4::perl-www-robotrules-6.02-0',
#             'channel-4::freetype-2.8-hab7d2ae_1',
#             'channel-4::perl-http-message-6.11-0',
#             'channel-4::perl-io-socket-ssl-2.024-0',
#             'channel-4::fontconfig-2.12.6-h49f89f6_0',
#             'channel-4::perl-http-cookies-6.01-0',
#             'channel-4::perl-http-daemon-6.01-0',
#             'channel-4::perl-http-negotiate-6.01-0',
#             'channel-4::perl-net-http-6.09-0',
#             'channel-4::cairo-1.14.12-h7636065_2',
#             'channel-4::perl-libwww-perl-6.15-0',
#             'channel-4::harfbuzz-1.7.6-h5f0a787_1',
#             'channel-4::perl-html-tree-5.03-0',
#             'channel-4::perl-xml-parser-2.44-4',
#             'channel-4::pango-1.41.0-hd475d92_0',
#             'channel-4::perl-html-formatter-2.14-0',
#             'channel-4::perl-xml-xpath-1.33-0',
#             'channel-4::graphviz-2.40.1-h25d223c_0',
#             'channel-4::perl-xml-twig-3.49-0',
#             'channel-4::perl-graphviz-2.20-1',
#             'channel-4::python-graphviz-0.8.3-py36_0',
#         )
#         assert convert_to_dist_str(link_dists) == link_order
#
#         python_graphviz_rec = link_dists[-1]
#         assert python_graphviz_rec.name == "python-graphviz"
#         assert python_graphviz_rec.name_aliases == ("graphviz",)
#
#     specs_to_add = MatchSpec("graphviz"),
#     with get_solver_4(specs_to_add=specs_to_add, prefix_records=final_state_1,
#                       history_specs=specs) as solver:
#         unlink_dists, link_dists = solver.solve_for_diff()
#
#         pprint(convert_to_dist_str(unlink_dists))
#         unlink_order = (
#
#         )
#         assert convert_to_dist_str(unlink_dists) == unlink_order
#
#         pprint(convert_to_dist_str(link_dists))
#         link_order = (
#             'channel-4::perl-threaded-5.22.0-10',
#             'channel-4::tidyp-1.04-1',
#             'channel-4::expat-2.2.5-he0dffb1_0',
#             'channel-4::graphite2-1.3.11-h16798f4_2',
#             'channel-4::icu-58.2-h9c2bf20_1',
#             'channel-4::jpeg-9b-h024ee3a_2',
#             'channel-4::libgcc-7.2.0-h69d50b8_2',
#             'channel-4::libtool-2.4.6-h544aabb_3',
#             'channel-4::libxcb-1.13-h1bed415_1',
#             'channel-4::pcre-8.42-h439df22_0',
#             'channel-4::perl-digest-hmac-1.03-0',
#             'channel-4::perl-file-which-1.20-0',
#             'channel-4::perl-font-afm-1.20-0',
#             'channel-4::perl-html-entities-numbered-0.04-0',
#             'channel-4::perl-html-tagset-3.20-0',
#             'channel-4::perl-html-tidy-1.56-1',
#             'channel-4::perl-http-date-6.02-0',
#             'channel-4::perl-io-html-1.001-0',
#             'channel-4::perl-io-tty-1.12-0',
#             'channel-4::perl-lwp-mediatypes-6.02-0',
#             'channel-4::perl-parse-recdescent-1.967013-0',
#             'channel-4::perl-test-pod-1.51-0',
#             'channel-4::perl-tie-ixhash-1.23-0',
#             'channel-4::perl-uri-1.71-0',
#             'channel-4::perl-xml-xpathengine-0.14-0',
#             'channel-4::pixman-0.34.0-hceecf20_3',
#             'channel-4::glib-2.56.1-h000015b_0',
#             'channel-4::libpng-1.6.34-hb9fc6fc_0',
#             'channel-4::libtiff-4.0.9-he85c1e1_1',
#             'channel-4::libxml2-2.9.8-h26e45fe_1',
#             'channel-4::perl-encode-locale-1.05-3',
#             'channel-4::perl-file-listing-6.04-0',
#             'channel-4::perl-html-parser-3.72-0',
#             'channel-4::perl-ipc-run-0.94-0',
#             'channel-4::perl-net-ssleay-1.74-0',
#             'channel-4::perl-ntlm-1.09-1',
#             'channel-4::perl-www-robotrules-6.02-0',
#             'channel-4::freetype-2.8-hab7d2ae_1',
#             'channel-4::perl-http-message-6.11-0',
#             'channel-4::perl-io-socket-ssl-2.024-0',
#             'channel-4::fontconfig-2.12.6-h49f89f6_0',
#             'channel-4::perl-http-cookies-6.01-0',
#             'channel-4::perl-http-daemon-6.01-0',
#             'channel-4::perl-http-negotiate-6.01-0',
#             'channel-4::perl-net-http-6.09-0',
#             'channel-4::cairo-1.14.12-h7636065_2',
#             'channel-4::perl-libwww-perl-6.15-0',
#             'channel-4::harfbuzz-1.7.6-h5f0a787_1',
#             'channel-4::perl-html-tree-5.03-0',
#             'channel-4::perl-xml-parser-2.44-4',
#             'channel-4::pango-1.41.0-hd475d92_0',
#             'channel-4::perl-html-formatter-2.14-0',
#             'channel-4::perl-xml-xpath-1.33-0',
#             'channel-4::graphviz-2.40.1-h25d223c_0',
#             'channel-4::perl-xml-twig-3.49-0',
#             'channel-4::perl-graphviz-2.20-1',
#             'channel-4::python-graphviz-0.8.3-py36_0',
#         )
#         assert convert_to_dist_str(link_dists) == link_order


class PrivateEnvTests(TestCase):

    def setUp(self):
        self.prefix = '/a/test/c/prefix'

        self.preferred_env = "_spiffy-test-app_"
        self.preferred_env_prefix = join(self.prefix, 'envs', self.preferred_env)

        # self.save_path_conflict = os.environ.get('CONDA_PATH_CONFLICT')
        self.saved_values = {}
        self.saved_values['CONDA_ROOT_PREFIX'] = os.environ.get('CONDA_ROOT_PREFIX')
        self.saved_values['CONDA_ENABLE_PRIVATE_ENVS'] = os.environ.get('CONDA_ENABLE_PRIVATE_ENVS')

        # os.environ['CONDA_PATH_CONFLICT'] = 'prevent'
        os.environ['CONDA_ROOT_PREFIX'] = self.prefix
        os.environ['CONDA_ENABLE_PRIVATE_ENVS'] = 'true'

        reset_context()

    def tearDown(self):
        for key, value in iteritems(self.saved_values):
            if value is not None:
                os.environ[key] = value
            else:
                del os.environ[key]

        reset_context()

    # @patch.object(Context, 'prefix_specified')
    # def test_simple_install_uninstall(self, prefix_specified):
    #     prefix_specified.__get__ = Mock(return_value=False)
    #
    #     specs = MatchSpec("spiffy-test-app"),
    #     with get_solver_3(specs) as solver:
    #         final_state_1 = solver.solve_final_state()
    #         # PrefixDag(final_state_1, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_1])
    #         order = (
    #             'channel-1::openssl-1.0.2l-0',
    #             'channel-1::readline-6.2-2',
    #             'channel-1::sqlite-3.13.0-0',
    #             'channel-1::tk-8.5.18-0',
    #             'channel-1::zlib-1.2.8-3',
    #             'channel-1::python-2.7.13-0',
    #             'channel-1::spiffy-test-app-2.0-py27hf99fac9_0',
    #         )
    #         assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)
    #
    #     specs_to_add = MatchSpec("uses-spiffy-test-app"),
    #     with get_solver_3(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
    #         final_state_2 = solver.solve_final_state()
    #         # PrefixDag(final_state_2, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_2])
    #         order = (
    #
    #         )
    #         assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
    #
    #     specs = specs + specs_to_add
    #     specs_to_remove = MatchSpec("uses-spiffy-test-app"),
    #     with get_solver_3(specs_to_remove=specs_to_remove, prefix_records=final_state_2,
    #                       history_specs=specs) as solver:
    #         final_state_3 = solver.solve_final_state()
    #         # PrefixDag(final_state_2, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_3])
    #         order = (
    #
    #         )
    #         assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)
