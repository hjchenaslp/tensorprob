import numpy as np
from nose.tools import raises
from numpy.testing import assert_almost_equal
import scipy.stats as st

import tensorprob as tp

def test_creation():
    model = tp.Model()
    with model:
        pass


@raises(tp.model.ModelError)
def test_scalar_creation_outside_with():
    tp.Parameter(name='mu')


@raises(tp.model.ModelError)
def test_distribution_creation_outside_with():
    with tp.Model():
        mu = tp.Parameter(name='mu')
        sigma = tp.Parameter(name='sigma', lower=0)
    tp.Normal(mu, sigma)


@raises(tp.model.ModelError)
def test_nesting_models():
    with tp.Model():
        with tp.Model():
            # Make coveralls ignore this line
            raise NotImplementedError


def test_observed():
    with tp.Model() as model:
        mu = tp.Parameter()
        sigma = tp.Parameter()
        X = tp.Normal(mu, sigma)
    model.observed(X)
    assert(X in model._observed)


@raises(ValueError)
def test_observed_erorr_on_non_distribution():
    with tp.Model() as model:
        mu = tp.Parameter()
        sigma = tp.Parameter()
        X = tp.Normal(mu, sigma)
    model.observed(X, int(42))


@raises(tp.model.ModelError)
def test_prepare_without_observed():
    with tp.Model() as model:
        mu = tp.Parameter()
    model.initialize({mu: 42})


def test_nll():
    with tp.Model() as model:
        mu = tp.Parameter()
        sigma = tp.Parameter()
        X = tp.Normal(mu, sigma)
    model.observed(X)

    xs = np.linspace(-5, 5, 100)
    out1 = -sum(st.norm.logpdf(xs, 0, 1))
    model.initialize({
        mu: 0,
        sigma: 1
    })
    out2 = model.nll(xs)
    assert_almost_equal(out1, out2, 10)


def test_fit():
    model = tp.Model()
    with model:
        mu = tp.Parameter(lower=-5, upper=5)
        sigma = tp.Parameter(lower=0)
        X = tp.Normal(mu, sigma)

    model.observed(X)
    model.initialize({mu: 2, sigma: 2})
    np.random.seed(0)
    data = np.random.normal(0, 1, 100)
    results = model.fit(data)
    assert results.success


def test_assign():
    model = tp.Model()
    with model:
        mu = tp.Parameter(lower=-5, upper=5)
        sigma = tp.Parameter(lower=0)
        X = tp.Normal(mu, sigma)

    model.observed(X)
    feed = {mu: 42, sigma: 1}
    model.initialize(feed)
    model.assign({mu: 1, sigma:0})
    model.assign({mu: -100, sigma:0})
    assert model.state == {mu: -100, sigma:0}
    model.assign(feed)
    assert model.state == feed


@raises(ValueError)
def test_assign_empty_dict():
    model = tp.Model()
    with model:
        mu = tp.Parameter(lower=-5, upper=5)
        sigma = tp.Parameter(lower=0)
        X = tp.Normal(mu, sigma)
    model.observed(X)
    model.assign({})


@raises(ValueError)
def test_assign_wrong_container():
    model = tp.Model()
    with model:
        mu = tp.Parameter(lower=-5, upper=5)
        sigma = tp.Parameter(lower=0)
        X = tp.Normal(mu, sigma)
    model.observed(X)
    model.assign([1,2,3])

@raises(tp.model.ModelError)
def test_observed_in_model():
    model = tp.Model()
    with model:
        mu = tp.Parameter(lower=-5, upper=5)
        sigma = tp.Parameter(lower=0)
        X = tp.Normal(mu, sigma)
        model.observed(X)

