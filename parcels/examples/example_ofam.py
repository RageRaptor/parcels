from parcels import FieldSet, ParticleSet, ScipyParticle, JITParticle, AdvectionRK4
from datetime import timedelta as delta
import pytest
import xarray as xr
from os import path


ptype = {'scipy': ScipyParticle, 'jit': JITParticle}


def set_ofam_fieldset(full_load=False, use_xarray=False):
    filenames = {'U': path.join(path.dirname(__file__), 'OFAM_example_data', 'OFAM_simple_U.nc'),
                 'V': path.join(path.dirname(__file__), 'OFAM_example_data', 'OFAM_simple_V.nc')}
    variables = {'U': 'u', 'V': 'v'}
    dimensions = {'lat': 'yu_ocean', 'lon': 'xu_ocean', 'depth': 'st_ocean',
                  'time': 'Time'}
    if use_xarray:
        ds = xr.open_mfdataset([filenames['U'], filenames['V']])
        return FieldSet.from_xarray_dataset(ds, variables, dimensions, allow_time_extrapolation=True, full_load=full_load)
    else:
        return FieldSet.from_netcdf(filenames, variables, dimensions, allow_time_extrapolation=True, full_load=full_load)


@pytest.mark.parametrize('use_xarray', [True, False])
def test_ofam_fieldset_fillvalues(use_xarray):
    fieldset = set_ofam_fieldset(full_load=True, use_xarray=use_xarray)
    # V.data[0, 0, 150] is a landpoint, that makes NetCDF4 generate a masked array, instead of an ndarray
    assert(fieldset.V.data[0, 0, 150] == 0)


@pytest.mark.parametrize('use_xarray', [True, False])
@pytest.mark.parametrize('mode', ['scipy', 'jit'])
def test_ofam_particles(mode, use_xarray):
    fieldset = set_ofam_fieldset(use_xarray=use_xarray)

    lonstart = [180]
    latstart = [10]
    depstart = [2.5]  # the depth of the first layer in OFAM

    pset = ParticleSet(fieldset, pclass=ptype[mode], lon=lonstart, lat=latstart, depth=depstart)

    pset.execute(AdvectionRK4, runtime=delta(days=10), dt=delta(minutes=5))

    assert(abs(pset[0].lon - 173) < 1)
    assert(abs(pset[0].lat - 11) < 1)
