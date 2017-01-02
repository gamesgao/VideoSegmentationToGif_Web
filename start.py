from __future__ import print_function
import sys
import IO
from graph_segmentation import *

if len(sys.argv) == 1:
    source = readSource = 'pre.avi'
else:
    source = sys.argv[1]
    isGoogle = int(sys.argv[2])
# groundTruth = False
# visualize = False
    readSource = "./videoTemp/" + source

video = IO.readVideo(readSource)
if(isGoogle == 1) sevideo = IO.readVideo(readSource+".avi")
else:
    flowVideo = IO.readFlowVideo(readSource)
    flowVideo = IO.readFlowVideoFromFile("./flowTemp/")

if(isGoogle != 1):
    assert video.getFrameNumber() > 0
    assert video.getFrameNumber() == flowVideo.getFrameNumber()
    M = 300
    L = 9
    c = 0.2
    beta = 0.2
    alpha = 1 - beta

    magic = GraphSegmentationMagicThreshold(c)
    distance = GraphSegmentationEuclideanRGBFlowAngle(alpha, beta)
    segmenter = GraphSegmentation(distance, magic)
    # timer

fig = []



# If you want to use the google version, use this:#
if(isGoogle == 1):
    segmenter.buildAndLabelAndPrint(video, sevideo, source, fig)
else:
    pass
    # Or you can use our version:
    segmenter.buildGraph(video, flowVideo)
    segmenter.buildEdges()
    print("----- Level 0")
    segmenter.oversegmentGraph()
    print("Oversegmented graph")
    segmenter.enforceMinimumSegmentSize(M)
    print("Enforced minimum region size")
    svVideo = segmenter.deriveLabels()
    IO.writeColoredSegmentationVideo(0, svVideo, fig, None, False,source)
    # save

    hmagic = GraphSegmentationHierarchyMagicThreshold(c, 4)
    hdistance = GraphSegmentationHierarchyRGBChiSquareFlowAngle(alpha, beta)
    segmenter.setHierarchyMagic(hmagic)
    segmenter.setHierarchyDistance(hdistance)

    for l in range(L):
        segmenter.buildRegionGraph()
        print("----- Level " + str(l + 1))
        segmenter.addHierarchyLevel()
        print("print Segmented region graph")
        segmenter.enforceMinimumSegmentSize(l / (2.0) * M)
        # M = l / 2 * M
        print("Enforce minimum segment size")
        svVideo = segmenter.deriveLabels()
        if (l < L - 1):
            IO.writeColoredSegmentationVideo(l + 1, svVideo, fig, None, False,source)
        else:
            IO.writeColoredSegmentationVideo(l + 1, svVideo, fig, video, True,source)
        sys.stdout.flush()
        # save

print("all Finished! ")
