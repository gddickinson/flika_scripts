"""Topic grouping for the catalogue: the one hand-curated part of the site.

Each script is put in the first topic whose rule matches its path. Topic blurbs only say what kind of files are in
the group (from folder names, file names and the scripts' own docstrings); they make no claims about results.
"""
import re

# (id, title, blurb, rule) — rule is a regex on the repo-relative path; first match wins.
TOPICS = [
    ("wf3-pre", "PIEZO1 tracking, workflow 3: preprocessing",
     "Prepare recordings before localisation: frame binning, cropping, bit-depth conversion and removing "
     "autofluorescent regions (folder piezo1_analysis/workFlow_3/1_preprocessing).",
     r"^piezo1_analysis/workFlow_3/1_preprocessing/"),
    ("wf3-analysis", "PIEZO1 tracking, workflow 3: analysis steps",
     "Numbered steps from localisations to annotated tracks: ThunderSTORM localisation via an ImageJ macro, linking "
     "and SVM classification, nearest neighbours, diffusion, velocity, neighbour counts, background-subtracted "
     "intensity, localisation error and distance to actin (folder 2_analysis).",
     r"^piezo1_analysis/workFlow_3/2_analysis/"),
    ("wf3-post", "PIEZO1 tracking, workflow 3: postprocessing",
     "Filter, compile and summarise track tables: SVM and intensity filters, per-experiment compilations, "
     "direction of travel, densities and running sums (folder 3_postprocessing).",
     r"^piezo1_analysis/workFlow_3/3_postprocessing/"),
    ("wf3-testing", "PIEZO1 tracking, workflow 3: tests and sketches",
     "Exploratory and test scripts kept beside workflow 3 (folder testing_misc): trackpy trials, peak detection on "
     "intensity traces, smoothing, plotting and array-orientation checks.",
     r"^piezo1_analysis/workFlow_3/testing_misc/"),
    ("wf2-old", "PIEZO1 tracking, workflow 2: superseded steps",
     "Earlier versions of workflow-2 steps kept in workFlow_2/old.",
     r"^piezo1_analysis/workFlow_2/old/"),
    ("wf2", "PIEZO1 tracking, workflow 2",
     "The second version of the tracking pipeline (folder piezo1_analysis/workFlow_2): steps 1-17 with repeated "
     "relinking and SVM classification passes for the remaining tracks.",
     r"^piezo1_analysis/workFlow_2/"),
    ("wf1", "PIEZO1 tracking, workflow 1",
     "The first version of the tracking pipeline (folder piezo1_analysis/workFlow): binning, ThunderSTORM "
     "localisation, linking, radius of gyration and track features, SVM classification and export.",
     r"^piezo1_analysis/workFlow/"),
    ("peaks", "Peak analysis",
     "Analysis scripts written for collaborators (folder peakAnalysis/forLuca and peakAnalysis/forMike).",
     r"^peakAnalysis/"),
    ("puffs", "Calcium puffs and FLIKA macros",
     "Calcium-imaging scripts from 2014-2015: FLIKA command sequences (baseline subtraction, F/F0 ratio, filters, "
     "thresholds), puff-site regrouping and duplicate removal in FLIKA's Excel output, movies and Gaussian fits.",
     r"^(20\d\d\.|puff|move_puffsites|nocodozole|trial\d?_|trial_\d|guassian_fit|SDscript|scaledAverage)"),
    ("nn", "Nearest-neighbour analysis",
     "Nearest-neighbour and all-neighbour distances between point sets or ROIs (scikit-learn KDTree / "
     "NearestNeighbors).",
     r"^(NN-|nearestNeighbour|AllNeig)"),
    ("overlay", "Image and localisation overlays",
     "Plotting STORM localisations and puff sites over images, including an animated version and an OpenCV variant.",
     r"^plot_image_and_scatter"),
    ("lightsheet", "Light-sheet, 3D and multi-colour display",
     "Displaying volumes and 4D arrays, shear (affine) transforms of light-sheet scans, multi-colour stacks and "
     "calling the light-sheet volume converter.",
     r"^(4dArray|pyqtgraph_3D|testAffineTransform|light_sheet|multiColour|callProcess)"),
    ("io", "Loading files",
     "Readers for camera and imaging formats: Princeton Instruments SPE (WinSpec), TIFF axis handling and an MRI "
     "volume.",
     r"^(load_SPE|pyWinSpec|loadMRI|testLoadofTiff)"),
    ("pynsight", "pynsight particle tracking",
     "Scripts that drive the pynsight FLIKA plugin and extract track intensities.",
     r"^(pyInsight|pyinsight|pynsight)"),
    ("misc", "Examples and utilities",
     "Small examples and one-liners: connected components, local histogram equalisation, a matplotlib slider demo, "
     "a VPython plot, a PCA + SVM tutorial and a window-shape helper.",
     r".*"),
]
_RULES = [(t[0], re.compile(t[3])) for t in TOPICS]


def topic_of(path: str) -> str:
    """Topic id for a repo-relative path."""
    return next(tid for tid, rx in _RULES if rx.search(path))


def topic_list() -> list[dict]:
    return [{"id": t[0], "title": t[1], "blurb": t[2]} for t in TOPICS]
