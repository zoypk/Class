import time
import random
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from data.test_generator import TestGenerator
from pre_processing.pre_processor import PreProcessor
from segmentation.line_segmentor import LineSegmentor
from features.feature_extractor import FeatureExtractor
from utils.utils import *
from utils.constants import *


#
# Variables
#
result_file = None
total_time = 0.0
testcase_time = []

# =====================================================================
#
# Pipeline functions
#
# =====================================================================

def myapp():
        # Set global variables
    global result_file, total_time, testcase_time

    # Start timer
    start = time.time()

    # Open files
    result_file = open(PREDICTED_RESULTS_PATH, 'w')
    
    return process_testcase(TESTCASES_PATH + '001' + '/')
    
   
def run():
    # Set global variables
    global result_file, total_time, testcase_time

    # Start timer
    start = time.time()

    # Open files
    result_file = open(PREDICTED_RESULTS_PATH, 'w')

    # Iterate on every testcase
    for root, dirs, files in os.walk(TESTCASES_PATH):
        for d in dirs:
            print('Running test iteration \'%s\'...' % d)

            # Start timer of test iteration
            t = time.time()

            # Solve test iteration
            process_testcase(TESTCASES_PATH + d + '/')

            # Finish timer of test iteration
            t = (time.time() - t)
            testcase_time.append(t)

            print('Finish test iteration \'%s\' in %.02f seconds\n' % (d, t))
        break

    # Close files
    result_file.close()

    # End timer
    total_time = (time.time() - start)


def process_testcase(path):
    features, labels = [], []

    
    for root, dirs, files in os.walk(path):
        for d in dirs:
            print('    Processing writer \'%s\'...' % d)
            x, y = get_writer_features(path + d + '/', d)
            features.extend(x)
            labels.extend(y)

    # Train the SVM model
    classifier = SVC(C=5.0, gamma='auto', probability=True)
    classifier.fit(features, labels)

    
    filename = "test_image1.jpg"
    print(path+filename)
    # Extract the features of the test image
    x = get_features(path + filename)

            # Get the most likely writer
    p = classifier.predict_proba(x)
    p = np.sum(p, axis=0)
    r = classifier.classes_[np.argmax(p)]

    
            # Write result

    return  r
    



def get_writer_features(path, writer_id):
    # All lines of the writer
    total_gray_lines, total_bin_lines = [], []

    # Read and append all lines of the writer
    for root, dirs, files in os.walk(path):
        for filename in files:
            gray_img = cv.imread(path + filename, cv.IMREAD_GRAYSCALE)
            gray_img, bin_img = PreProcessor.process(gray_img)
            gray_lines, bin_lines = LineSegmentor(gray_img, bin_img).segment()
            total_gray_lines.extend(gray_lines)
            total_bin_lines.extend(bin_lines)
        break

    # Extract features of every line separately
    x, y = [], []
    for g, b in zip(total_gray_lines, total_bin_lines):
        f = FeatureExtractor([g], [b]).extract()
        x.append(f)
        y.append(writer_id)

    return x, y


def get_features(path):
    # Read and pre-process the image
    gray_img = cv.imread(path, cv.IMREAD_GRAYSCALE)
    gray_img, bin_img = PreProcessor.process(gray_img)
    gray_lines, bin_lines = LineSegmentor(gray_img, bin_img).segment()

    # Extract features of every line separately
    x = []
    for g, b in zip(gray_lines, bin_lines):
        f = FeatureExtractor([g], [b]).extract()
        x.append(f)

    # Return list of features for every line in the image
    return x


if DEBUG_SAVE_WRONG_TESTCASES:
    print_wrong_testcases()
    save_wrong_testcases()
