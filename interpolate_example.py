import matplotlib.pyplot as plt
import numpy as np
import nai_nonlinear

def main():
    energies = np.arange(1, 1000, 0.1)
    ratios = nai_nonlinear.interpolated_ratio(energies)
    fig, ax = plt.subplots()
    ax.plot(energies, ratios)
    ax.set_xscale('log')
    plt.show()


if __name__ == '__main__': main()
