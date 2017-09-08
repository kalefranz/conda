# (c) 2012-2016 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
#
# conda is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import defaultdict
from logging import getLogger
import os
from os import listdir, lstat, walk
from os.path import getsize, isdir, join
import sys

from ..base.constants import CONDA_TARBALL_EXTENSION
from ..base.context import context

log = getLogger(__name__)


def find_tarballs():
    from ..core.package_cache import PackageCache

    pkgs_dirs = {}
    totalsize = 0
    for package_cache in PackageCache.writable_caches(context.pkgs_dirs):
        tarball_pcrecs = package_cache.pcrecs_with_tarballs
        totalsize += sum(pcrec.size for pcrec in tarball_pcrecs)

        pkgs_dir_path_len = len(package_cache.pkgs_dir) + 1
        tarball_paths = tuple(pcrec.package_tarball_full_path[pkgs_dir_path_len:]
                              for pcrec in tarball_pcrecs)
        pkgs_dirs[package_cache.pkgs_dir] = tarball_paths

    return pkgs_dirs, totalsize


def rm_tarballs(args, pkgs_dirs, totalsize, verbose=True):
    from .common import confirm_yn
    from ..gateways.disk.delete import rm_rf
    from ..utils import human_bytes

    if verbose:
        for pkgs_dir in pkgs_dirs:
            print('Cache location: %s' % pkgs_dir)

    if not any(pkgs_dirs[i] for i in pkgs_dirs):
        if verbose:
            print("There are no tarballs to remove")
        return

    if verbose:
        print("Will remove the following tarballs:")
        print()

        for pkgs_dir in pkgs_dirs:
            print(pkgs_dir)
            print('-'*len(pkgs_dir))
            fmt = "%-40s %10s"
            for fn in pkgs_dirs[pkgs_dir]:
                size = getsize(join(pkgs_dir, fn))
                print(fmt % (fn, human_bytes(size)))
            print()
        print('-' * 51)  # From 40 + 1 + 10 in fmt
        print(fmt % ('Total:', human_bytes(totalsize)))
        print()

    if not context.json or not context.always_yes:
        confirm_yn()
    if context.json and args.dry_run:
        return

    for pkgs_dir in pkgs_dirs:
        for fn in pkgs_dirs[pkgs_dir]:
            try:
                if rm_rf(os.path.join(pkgs_dir, fn)):
                    if verbose:
                        print("Removed %s" % fn)
                else:
                    if verbose:
                        print("WARNING: cannot remove, file permissions: %s" % fn)
            except (IOError, OSError) as e:
                if verbose:
                    print("WARNING: cannot remove, file permissions: %s\n%r" % (fn, e))
                else:
                    log.info("%r", e)
    from ..core.package_cache import PackageCache
    PackageCache._cache_ = {}


def find_pkgs():
    warnings = []

    from ..core.package_cache import PackageCache
    from ..gateways.disk.read import read_paths_json

    pkgs_dirs = {}
    pkgsizes = {}
    totalsize = 0
    for package_cache in PackageCache.writable_caches(context.pkgs_dirs):
        unused_pcrecs = package_cache.pcrecs_not_linked()

        pkgsizes_this_pkgs_dir = []
        for pcrec in unused_pcrecs:
            paths_data = read_paths_json(pcrec.extracted_package_dir)
            this_size = sum(getattr(pd, 'size_in_bytes', 0) for pd in paths_data.paths)
            pkgsizes_this_pkgs_dir.append(this_size)
            totalsize += this_size

        pkgs_dir_path_len = len(package_cache.pkgs_dir) + 1
        extracted_package_dirs = tuple(pcrec.extracted_package_dir[pkgs_dir_path_len:]
                                       for pcrec in unused_pcrecs)
        pkgs_dirs[package_cache.pkgs_dir] = extracted_package_dirs
        pkgsizes[package_cache.pkgs_dir] = pkgsizes_this_pkgs_dir

    return pkgs_dirs, warnings, totalsize, pkgsizes


def rm_pkgs(args, pkgs_dirs, warnings, totalsize, pkgsizes, verbose=True):
    from .common import confirm_yn
    from ..gateways.disk.delete import rm_rf
    from ..utils import human_bytes
    if verbose:
        for pkgs_dir in pkgs_dirs:
            print('Cache location: %s' % pkgs_dir)
            for fn, exception in warnings:
                print(exception)

    if not any(pkgs_dirs[i] for i in pkgs_dirs):
        if verbose:
            print("There are no unused packages to remove")
        return

    if verbose:
        print("Will remove the following packages:")
        for pkgs_dir in pkgs_dirs:
            print(pkgs_dir)
            print('-' * len(pkgs_dir))
            print()
            fmt = "%-40s %10s"
            for pkg, pkgsize in zip(pkgs_dirs[pkgs_dir], pkgsizes[pkgs_dir]):
                print(fmt % (pkg, human_bytes(pkgsize)))
            print()
        print('-' * 51)  # 40 + 1 + 10 in fmt
        print(fmt % ('Total:', human_bytes(totalsize)))
        print()

    if not context.json or not context.always_yes:
        confirm_yn()
    if context.json and args.dry_run:
        return

    for pkgs_dir in pkgs_dirs:
        for pkg in pkgs_dirs[pkgs_dir]:
            if verbose:
                print("removing %s" % pkg)
            rm_rf(join(pkgs_dir, pkg))

    from ..core.package_cache import PackageCache
    PackageCache._cache_ = {}


def rm_index_cache():
    from ..gateways.disk.delete import rm_rf
    from ..core.package_cache import PackageCache
    for package_cache in PackageCache.writable_caches():
        rm_rf(join(package_cache.pkgs_dir, 'cache'))


def find_source_cache():
    cache_dirs = {
        'source cache': context.src_cache,
        'git cache': context.git_cache,
        'hg cache': context.hg_cache,
        'svn cache': context.svn_cache,
    }

    sizes = {}
    totalsize = 0
    for cache_type, cache_dir in cache_dirs.items():
        dirsize = 0
        for root, d, files in walk(cache_dir):
            for fn in files:
                size = lstat(join(root, fn)).st_size
                totalsize += size
                dirsize += size
        sizes[cache_type] = dirsize

    return {
        'warnings': [],
        'cache_dirs': cache_dirs,
        'cache_sizes': sizes,
        'total_size': totalsize,
    }


def rm_source_cache(args, cache_dirs, warnings, cache_sizes, total_size):
    from .common import confirm_yn
    from ..gateways.disk.delete import rm_rf
    from ..utils import human_bytes

    verbose = not (context.json or context.quiet)
    if warnings:
        if verbose:
            for warning in warnings:
                print(warning, file=sys.stderr)
        return

    if verbose:
        for cache_type in cache_dirs:
            print("%s (%s)" % (cache_type, cache_dirs[cache_type]))
            print("%-40s %10s" % ("Size:", human_bytes(cache_sizes[cache_type])))
            print()

        print("%-40s %10s" % ("Total:", human_bytes(total_size)))

    if not context.json or not context.always_yes:
        confirm_yn()
    if context.json and args.dry_run:
        return

    for dir in cache_dirs.values():
        if verbose:
            print("Removing %s" % dir)
        rm_rf(dir)


def execute(args, parser):
    from .common import stdout_json
    json_result = {
        'success': True
    }

    if args.tarballs or args.all:
        pkgs_dirs, totalsize = find_tarballs()
        first = sorted(pkgs_dirs)[0] if pkgs_dirs else ''
        json_result['tarballs'] = {
            'pkgs_dir': first,  # Backwards compabitility
            'pkgs_dirs': dict(pkgs_dirs),
            'files': pkgs_dirs[first],  # Backwards compatibility
            'total_size': totalsize
        }
        rm_tarballs(args, pkgs_dirs, totalsize, verbose=not (context.json or context.quiet))

    if args.index_cache or args.all:
        json_result['index_cache'] = {
            'files': [join(context.pkgs_dirs[0], 'cache')]
        }
        rm_index_cache()

    if args.packages or args.all:
        pkgs_dirs, warnings, totalsize, pkgsizes = find_pkgs()
        first = sorted(pkgs_dirs)[0] if pkgs_dirs else ''
        json_result['packages'] = {
            'pkgs_dir': first,  # Backwards compatibility
            'pkgs_dirs': dict(pkgs_dirs),
            'files': pkgs_dirs[first],  # Backwards compatibility
            'total_size': totalsize,
            'warnings': warnings,
            'pkg_sizes': {i: dict(zip(pkgs_dirs[i], pkgsizes[i])) for i in pkgs_dirs},
        }
        rm_pkgs(args, pkgs_dirs,  warnings, totalsize, pkgsizes,
                verbose=not (context.json or context.quiet))

    if args.source_cache or args.all:
        json_result['source_cache'] = find_source_cache()
        rm_source_cache(args, **json_result['source_cache'])

    if not any((args.lock, args.tarballs, args.index_cache, args.packages,
                args.source_cache, args.all)):
        from ..exceptions import ArgumentError
        raise ArgumentError("One of {--lock, --tarballs, --index-cache, --packages, "
                            "--source-cache, --all} required")

    if context.json:
        stdout_json(json_result)
