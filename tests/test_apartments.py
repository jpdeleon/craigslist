# -*- coding: utf-8 -*-
import sys
import matplotlib.pyplot as pl
from matplotlib.axes import Axes
import pandas as pd

sys.path.append("..")
from apartments import Base

bc = Base(
    location="tokyo",
    max_price=200000,
    max_sqft=100,
    npages=1,
    verbose=True,
    save_csv=False,
    save_fig=False,
)


def test_init():
    assert isinstance(bc.apts, pd.DataFrame)


def test_plots():
    if True:
        ax = bc.plot_price()
        assert isinstance(ax, Axes)
    if False:
        ax = bc.plot_regression()
        assert isinstance(ax, Axes)
    if False:
        ax = bc.plot_boxplot()
        assert isinstance(ax, Axes)
