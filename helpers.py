############# General helpers

def load_config(as_object=True):
    import json
    from types import SimpleNamespace
    with open("./config.json", "r", encoding="utf-8") as jsonfile:
        if as_object:
            config = json.load(jsonfile, object_hook=lambda d: SimpleNamespace(**d))
            # Extract the condition mapping from configuration namespace.
            # Needs to be a dictionary, with ints as keys (not strings).
            condmap_as_dict = { int(k): v for k, v in vars(config.condition_mapping).items() }
            config.condition_mapping = condmap_as_dict
        else:
            config = json.load(jsonfile)
    return config

Config = load_config()


# def remove_subjects(df, below=None, above=None, exact=[]):
#     if below is not None:
#         df = df[ df["run_id"].gt(below) ]
#     if above is not None:
#         df = df[ df["run_id"].lt(above) ]
#     for s in exact:
#         df = df[ ~df["run_id"].isin(exact) ]
#     return df.copy()



############# Plotting helpers

def load_matplotlib_settings():
    from matplotlib.pyplot import rcParams
    rcParams["savefig.dpi"] = 600
    rcParams["interactive"] = True
    rcParams["font.family"] = "Times New Roman"
    # rcParams["font.sans-serif"] = "Arial"
    rcParams["mathtext.fontset"] = "custom"
    rcParams["mathtext.rm"] = "Times New Roman"
    rcParams["mathtext.cal"] = "Times New Roman"
    rcParams["mathtext.it"] = "Times New Roman:italic"
    rcParams["mathtext.bf"] = "Times New Roman:bold"
    rcParams["font.size"] = 8
    rcParams["axes.titlesize"] = 8
    rcParams["axes.labelsize"] = 8
    rcParams["axes.labelsize"] = 8
    rcParams["xtick.labelsize"] = 8
    rcParams["ytick.labelsize"] = 8
    rcParams["legend.fontsize"] = 8
    rcParams["legend.title_fontsize"] = 8


def no_leading_zeros(x, pos):
    # a custom tick formatter for matplotlib
    # to show decimals without a leading zero
    val_str = "{:g}".format(x)
    if abs(x) > 0 and abs(x) < 1:
        return val_str.replace("0", "", 1)
    else:
        return val_str


def save_hires_figs(png_fname, hires_extensions=[".svg", ".eps", ".pdf"]):
    # replace the extension and go down into a "hires" folder which should be there
    import os
    from matplotlib.pyplot import savefig
    png_dir, png_bname = os.path.split(png_fname)
    hires_dir = os.path.join(png_dir, "hires")
    for ext in hires_extensions:
        hires_bname = png_bname.replace(".png", ext)
        hires_fname = os.path.join(hires_dir, hires_bname)
        savefig(hires_fname)
