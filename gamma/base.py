import os.path as pth
import functools as ft
import subprocess as sub
import shlex

from glob import iglob
from sys import path
from os.path import join as pjoin

import json
import utils as ut

__all__ = (
    "gamma", "progs", "Project", "DataFile", "SLC", "Lookup"
)


exe = "gamma"
cmds = {"select", "import", "batch", "move", "make", "stat", "like"}

gamma = ut.subcmommands(exe, cmds, prefix="-")

class Project(object):
    default_options = {}

    # defaultConfig = Config{
        # General: GeneralOpt{
            # Pol: "vv",
            # OutputDir: ".",
            # MasterDate: "",
            # CachePath: "/mnt/storage_A/istvan/cache",
            # Looks: RngAzi{
                # Rng: 1,
                # Azi: 1,
            # },
        # },

        # PreSelect: PreSelectOpt{
            # CheckZips:  false,
        # },

        # Geocoding: GeocodeOpt{
            # DEMPath: "/mnt/storage_B/szucs_e/SRTMGL1/SRTM.vrt",
            # Iter: 1,
            # nPixel: 8,
            # LanczosOrder: 5,
            # NPoly: 1,
            # MLIOversamp: 2,
            # CCThresh: 0.1,
            # BandwithFrac: 0.8,
            # AreaFactor: 20.0,
            # RngOversamp: 2.0,
            # DEMOverlap: RngAzi{
                # Rng: 100,
                # Azi: 100,
            # },
            # DEMOverSampling: LatLon{
                # Lat: 2.0,
                # Lon: 2.0,
            # },
            # OffsetWindows: RngAzi{
                # Rng: 500,
                # Azi: 500,
            # },
        # },

        # IFGSelect: IfgSelectOpt{
            # Bperp:  Minmax{Min: 0.0, Max: 150.0},
            # DeltaT: Minmax{Min: 0.0, Max: 15.0},
        # },

        # CalcCoherence: CoherenceOpt{
            # WeightType:             "gaussian",
            # Box:                    Minmax{Min: 3.0, Max: 9.0},
            # SlopeCorrelationThresh: 0.4,
            # SlopeWindow:            5,
        # },
    # }
    
    def __init__(self, *args, **kwargs):
        self.general = kwargs
        
    def select(self, path, *args, **kwargs):
        datas = ','.join(iglob(pth.join(path, "*.zip")))
        
        gamma.select(*args, **self.general, **kwargs, dataFiles=datas)
    
    def data_import(self, *args, **kwargs):
        getattr(gamma, "import")(*args, **self.general, **kwargs)
    

class DataFile(object):
    __slots__ = ("metafile",)
    
    datfile_ext = "dat"
    parfile_ext = "par"
    
    def __init__(self):
        self.metafile = path
    
    @classmethod
    def new(cls, **kwargs):
        meta, dat = kwargs.pop("meta", None), kwargs.pop("dat", None)
        
        if meta is None and dat is None:
            tmp = util.tmp_file()
        
        if meta is None:
            meta = "%s.json" % tmp
        
        if dat is None:
            dat = "%s.%s" % (tmp, self.datfile_ext)
        
        with open(meta, "w") as f:
            json.dump({"dat" : dat}, f)
        
        return cls(meta)
        
    @classmethod
    def like(cls, other, name=None, **kwargs):
        if name is None:
            name = utils.tmp_file(ext="json")
        
        kwargs["in"] = other.metafile
        gamma.like(out=name, **kwargs)
        
        return cls(**kwargs)
    
    def move(self, dirPath):
        gamma.move(meta=self.meta, out=dirPath)
        self.meta = path.join(dirPath, self.meta)
    
    def stat(self, **kwargs):
        return gamma.stat(self.metafile, **kwargs)


class SLC(DataFile):
    datfile_ext = "slc"
    
    def SplitInterferometry(self):
        pass


class Lookup(DataFile):
    def geocode(self, mode, infile, outfile=None, like=None, **kwargs):
        kwargs["infile"] = infile
        
        if like is not None:
            outfile = like.like(**kwargs)
        
        kwargs["outfile"] = outfile
        kwargs["lookup"] = self.metafile

        gamma.geocode(**kwargs)
    
    def radar2geo(self, **kwargs):
        kwargs["mode"] = "togeo"
        
        return gamma.geocode(**kwargs)

    def geo2radar(self, **kwargs):
        kwargs["mode"] = "toradar"
        
        return gamma.geocode(**kwargs)
