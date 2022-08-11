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
    # rcParams["figure.dpi"] = 600
    rcParams["savefig.dpi"] = 600
    rcParams["interactive"] = True
    rcParams["figure.constrained_layout.use"] = True
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
    rcParams["axes.linewidth"] = 0.8 # edge line width
    rcParams["axes.axisbelow"] = True
    rcParams["axes.grid"] = True
    rcParams["axes.grid.axis"] = "y"
    rcParams["axes.grid.which"] = "major"
    rcParams["axes.labelpad"] = 4
    rcParams["xtick.top"] = True
    rcParams["ytick.right"] = True
    rcParams["xtick.direction"] = "in"
    rcParams["ytick.direction"] = "in"
    rcParams["grid.color"] = "gainsboro"
    rcParams["grid.linewidth"] = 1
    rcParams["grid.alpha"] = 1
    rcParams["legend.frameon"] = False
    rcParams["legend.edgecolor"] = "black"
    rcParams["legend.fontsize"] = 8
    rcParams["legend.title_fontsize"] = 8
    rcParams["legend.borderpad"] = .4
    rcParams["legend.labelspacing"] = .2 # the vertical space between the legend entries
    rcParams["legend.handlelength"] = 2 # the length of the legend lines
    rcParams["legend.handleheight"] = .7 # the height of the legend handle
    rcParams["legend.handletextpad"] = .2 # the space between the legend line and legend text
    rcParams["legend.borderaxespad"] = .5 # the border between the axes and legend edge
    rcParams["legend.columnspacing"] = 1 # the space between the legend line and legend text


def load_subject_palette(separate_by_task=True):
    """Load from utils for not just convenience
    but also to make sure colors are consistent across
    plots (ie, even if a subj is removed from a later analysis).
    So load earliest possible dataframe here.
    glasbey colormaps: https://colorcet.holoviz.org/user_guide/Categorical.html
    """
    import os
    import pandas as pd
    import colorcet as cc
    emp_fname = os.path.join(Config.data_directory, "derivatives", "empathy-data.csv")
    bct_fname = os.path.join(Config.data_directory, "derivatives", "bct-data_presses.csv")
    df_emp = pd.read_csv(emp_fname).sort_values("participant_id")
    df_bct = pd.read_csv(bct_fname).sort_values("participant_id")
    if separate_by_task:
        unique_rest_subjects = df_emp.query("task_condition=='rest'")["participant_id"].unique()
        unique_bct_subjects1 = df_emp.query("task_condition=='bct'")["participant_id"].unique()
        unique_bct_subjects2 = df_bct["participant_id"].unique()
        unique_bct_subjects = sorted(list(set(unique_bct_subjects1) & set(unique_bct_subjects2)))
        bct_subj_palette = { subj: cc.cm.glasbey_cool(i) for i, subj in enumerate(unique_bct_subjects) }
        rest_subj_palette = { subj: cc.cm.glasbey_warm(i) for i, subj in enumerate(unique_rest_subjects) }
        assert 0 == len(bct_subj_palette.keys() & rest_subj_palette.keys()), "Should not have overlapping subjects."
        subj_palette = bct_subj_palette | rest_subj_palette
    else: # glasbey_bw or glasbey_dark
        unique_subjects1 = df_emp["participant_id"].unique()
        unique_subjects2 = df_bct["participant_id"].unique()
        unique_subjects = sorted(list(set(unique_subjects1) & set(unique_subjects2)))
        subj_palette = { subj: cc.cm.glasbey_dark(i) for i, subj in enumerate(unique_subjects) }
    return subj_palette


def no_leading_zeros(x, pos):
    # a custom tick formatter for matplotlib
    # to show decimals without a leading zero
    val_str = "{:g}".format(x)
    if abs(x) > 0 and abs(x) < 1:
        return val_str.replace("0", "", 1)
    else:
        return val_str


def save_hires_copies(png_fname, formats=["pdf"]):
    """Saves out hi-resolution matplotlib figures.
    Assumes there is a "hires" subdirectory within the path
    of the filename passed in, which must be also be a png filename.
    """
    assert png_fname.endswith(".png"), f"Must pass a .png filename, you passed {png_fname}"
    import os
    from matplotlib.pyplot import savefig
    png_dir, png_bname = os.path.split(png_fname)
    hires_dir = os.path.join(png_dir, "hires")
    for f in formats:
        ext = "." + f
        hires_bname = png_bname.replace(".png", ext)
        hires_fname = os.path.join(hires_dir, hires_bname)
        savefig(hires_fname)
