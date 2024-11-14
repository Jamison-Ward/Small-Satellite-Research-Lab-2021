import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo

def linear_fit(bins, intercept, slope):
    return intercept + slope*bins

def plot_fit(x_data, y_data, x_fit, y_fit):
    fig, ax = plt.subplots()
    ax.plot(x_fit, y_fit, label="fit")
    ax.scatter(x_data, y_data, label="data")
    fig.tight_layout()
    plt.show()

def main():
    fn = 'source_data.txt'
    bins, peak_energies = np.loadtxt(fn, delimiter=',', unpack=True)
    # print(bins)
    # print(peak_energies)

    # the covariance matrix encodes uncertainty in parameters as well as 
    # correlated uncertainty.
    linear_params, linear_cov_mat = spo.curve_fit(linear_fit, bins, peak_energies)
    print(linear_params)
    # take the square root of its diagonal entries to get independent uncertainties.
    # in other words, assume that the parameters are uncorrelated.
    linear_uncert = np.sqrt(np.diag(linear_cov_mat))

    # do the same here
    x_fit = np.linspace(0, 4096, num=100)
    plot_fit(bins, peak_energies, x_fit, linear_fit(x_fit, *linear_params))

if __name__ == '__main__': main()
