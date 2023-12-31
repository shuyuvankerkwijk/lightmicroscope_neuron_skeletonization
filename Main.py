import logging
import os
from ImageJ_processing import ImageJ_processing
from Skeletonization_processing import Skeletonization_processing
from Manual_processing import Manual_processing

root_folderpath = 'path here'
num_slices_to_remove = 5 #number of slices to remove from start of image stack

skipfirststeps = False #'True' skips ImageJ processing and skeletonization (useful if you just want to run the GUIs or you crashed at that stage and don't want to redo image processing)

threshold1 = {
    'blur_sigma': [2, 2, 2],  # x, y, z
    'sb_radius': 15, #sliding paraboloid radius
    'rawthresh': 2, #thresholding method 1 is an abs global threshold
    'minsize': 250, #all objects less than this pixel area will be removed after thresholding
}

threshold2 = {
    'blur_sigma': [2, 2, 2],  # x, y, z
    'sb_radius': 15, #sliding paraboloid radius
    'threshtype': 'Triangle', #thresholding method for 2
    'minsize': 250, #all objects less than this pixel area will be removed after thresholding
}

threshold3 = {
    'blur_sigma': [2, 2, 2],  # x, y, z
    'sb_radius': 15, #sliding paraboloid radius
    'threshtype': 'Default', #thresholding method for 2
    'minsize': 250, #all objects less than this pixel area will be removed after thresholding
}

remove_nuclei = False
remove_nuclei_parameters = { #if remove_nuclei is set to False, it doesn't matter what these parameters are set to
    'minArea' : 5000, 
    'maxArea' : 20000,
    'minCircularity' : 0.25,
    'maxCircularity' : 1,
    'minConvexity' : 0.2,
    'maxConvexity' : 1,
    'minInertia' : 0.1,
    'maxInertia' : 1
}

branching_parameters = {
    'remove_overlap' : 2, #minimum distance between nodes to reduce clutter (adjacent nodes under threshold will be removed)
    'num_nearestneighbours' : 3, #number of k-nearest neighbours to consider for branching
    'min_unconnected_nodes' : 5, #minimum number of nodes for an unconnected cluster to be considered important enough to attach to the main branch
    'max_unconnected_distance' : 50 #maximum distance from main branch for an unconnected cluster to be considered important enough to be added to the main branch
}

#configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if skipfirststeps == False:
    '''
    Section 1: Run image processing using ImageJ 
    - preprocessing, i.e. intensity normalization, conversion to 8-bit data
    - 3d gaussian blur with sigma defined above
    - subtract background function using sliding paraboloid with radius defined above
    - thresholding using method and value defined above
    - removal of all small objects lower than minimum size defined above
    - save processed and thresholded image in new /Processed folder as .tif
    '''
    processed_folderpath = ImageJ_processing(
        folderpath=root_folderpath,
        threshold1=threshold1,
        threshold2=threshold2,
        threshold3=threshold3,
        num_slices_to_remove=num_slices_to_remove
        )
    logging.info("Done Section 1: ImageJ processing on all images")

    '''
    Section 2: Skeletonize processed images
    - run optional cv2 Blob Detection with parameters to remove nuclei (which in some cases may be more circular than other 'branch' blobs)
    - skeletonize thresholded images using Ske`letonize3D from scikit-image
    - save resulting skeleton as a point cloud in .npy file
    '''
    coords_folderpath = Skeletonization_processing(
        folderpath=processed_folderpath,
        remove_nuclei=remove_nuclei,
        remove_nuclei_parameters=remove_nuclei_parameters)
    logging.info("Done Section 2: Skeletonization of all processed images")
else:
    processed_folderpath = os.path.join(root_folderpath, "Processed")
    coords_folderpath = os.path.join(processed_folderpath, "Coords")

'''
Section 3: Manual processing
- first GUI lets you choose root, start, end nodes, and remove points
- branching is run using data from first GUI
- second GUI lets you correct processed branching
- third GUI lets you make measurements
'''
Manual_processing(folderpath = coords_folderpath, branching_parameters = branching_parameters)