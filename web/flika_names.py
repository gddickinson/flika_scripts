"""Names of FLIKA process functions, used to recognise FLIKA steps in a script (e.g. `subtract(100)`).

Taken from `flika.process` of FLIKA 0.3.0 (the version in George's flika_new environment), plus the older names
`slicekeeper` and `open_file_gui` that the 2014-2015 scripts use.
"""
FLIKA_PROCESS = frozenset({
    "Split_channels", "absolute_value", "adaptive_threshold", "analyze_particles", "area_closing", "area_opening",
    "background_sub", "background_subtract", "bake_overlays_process", "batch_export", "bilateral_filter",
    "binary_dilation", "binary_erosion", "bleach_correction", "blend_channels", "blob_detection_doh",
    "blob_detection_log", "boxcar_differential_filter", "butterworth_filter", "calcium_analysis",
    "canny_edge_detector", "change_datatype", "channel_alignment", "channel_compositor", "clear_border", "close",
    "concatenate_stacks", "connected_components", "convert_color_space", "corner_detection", "counting_tool",
    "deinterleave", "detect_particles", "difference_filter", "difference_of_gaussians", "distance_transform",
    "divide", "divide_trace", "duplicate", "expand_labels", "find_boundaries", "find_contours_process",
    "flash_remover", "flip_image", "flood_fill_process", "fourier_filter", "frame_binning", "frame_remover",
    "frangi_vesselness", "frap_analysis", "fret_analysis", "gabor_filter", "gaussian_blur",
    "gaussian_gradient_magnitude_filter", "gaussian_laplace_filter", "generate_phantom_volume", "generate_psf",
    "generate_random_image", "generate_rois", "grayscale", "grayscale_closing", "grayscale_opening", "grid_overlay",
    "h_maxima", "h_minima", "hessian_filter", "histogram_equalize", "hough_circles", "hough_lines",
    "hysteresis_threshold", "image_calculator", "laplacian_filter", "linescan", "link_particles_process",
    "local_binary_pattern_process", "local_maxima_detect", "logically_combine", "mask_editor", "maximum_filter",
    "mean_filter", "medial_axis_process", "median_filter", "meijering_neuriteness", "minimum_filter",
    "morphological_gradient", "morphometry_analysis", "motion_correction", "multi_otsu_threshold", "multiply",
    "normalize", "open_file", "open_file_from_gui", "open_image_sequence_from_gui", "open_points", "peak_local_max",
    "percentile_filter", "pixel_binning", "power", "random_walker_seg", "ratio", "region_properties",
    "remove_small_blobs", "remove_small_holes", "resize", "richardson_lucy", "rotate_90", "rotate_custom",
    "sato_tubeness", "save_file", "save_movie_gui", "save_points", "save_rois", "scale_bar",
    "scaled_average_subtract", "set_value", "shear_transform", "simulate", "skeleton_analysis", "skeletonize_process",
    "slic_superpixels", "sobel_filter", "spectral_unmixing", "split_channels", "spt_analysis", "sqrt",
    "stitch_images", "structure_tensor_analysis", "subtract", "subtract_trace", "template_match", "threshold",
    "time_stamp", "trim", "tv_denoise", "variance_filter", "video_exporter", "watershed", "watershed_segmentation",
    "wavelet_filter", "wiener_deconvolution", "zproject", "slicekeeper", "open_file_gui",
})
