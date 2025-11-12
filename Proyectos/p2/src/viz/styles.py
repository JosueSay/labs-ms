import matplotlib as mpl
import matplotlib.pyplot as plt

def applyPlotStyle():
    mpl.rcParams.update({
        # tamaño por defecto
        "figure.figsize": (10, 5),

        # texto
        "font.size": 11,
        "axes.titlesize": 14, "axes.titleweight": "bold",
        "axes.labelsize": 12, "axes.labelweight": "bold",

        # ejes y spines
        "axes.spines.right": False, "axes.spines.top": False,
        "axes.linewidth": 1.2,
        "xtick.major.width": 1.0, "ytick.major.width": 1.0,

        # grid sutil
        "axes.grid": True, "grid.alpha": 0.2, "grid.linestyle": "-",

        # leyenda
        "legend.frameon": False,

        # ciclo de colores agradable
        "axes.prop_cycle": plt.cycler(color=plt.cm.Set2.colors),

        # márgenes automáticos
        "figure.autolayout": True,
    })

def getAxes(title=None, xlabel=None, ylabel=None):
    if mpl.rcParams.get("axes.prop_cycle", None) is None:
        applyPlotStyle()
    fig, ax = plt.subplots()
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    return fig, ax

def saveOrShow(fig, path=None, dpi=200):
    if path:
        fig.savefig(path, bbox_inches="tight", dpi=dpi)
        plt.close(fig)
    else:
        plt.show()

