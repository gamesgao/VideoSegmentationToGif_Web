from __future__ import print_function

import IO
from graph_segmentation import *

if len(sys.argv) == 1:
    source = readSource = '13.mp4'
else:
    source = sys.argv[1]
# groundTruth = False
# visualize = False
    readSource = "./videoTemp/" + source

video = IO.readVideo(readSource)
flowVideo = IO.readFlowVideo(readSource)

assert video.getFrameNumber() > 0
assert video.getFrameNumber() == flowVideo.getFrameNumber()
M = 300
L = 13
c = 0.2
beta = 0.2
alpha = 1 - beta

magic = GraphSegmentationMagicThreshold(c)
distance = GraphSegmentationEuclideanRGBFlowAngle(alpha, beta)
segmenter = GraphSegmentation(distance, magic)
# timer

fig = []

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

hmagic = GraphSegmentationHierarchyMagicThreshold(c, 2)
hdistance = GraphSegmentationHierarchyRGBChiSquareFlowAngle(alpha, beta)
segmenter.setHierarchyMagic(hmagic)
segmenter.setHierarchyDistance(hdistance)

for l in range(L):
    segmenter.buildRegionGraph()
    print("----- Level " + str(l + 1))
    segmenter.addHierarchyLevel()
    print("print Segmented region graph")
    segmenter.enforceMinimumSegmentSize(l / 2 * M)
    # M = l / 2 * M
    print("Enforce minimum segment size")
    svVideo = segmenter.deriveLabels()
    if (l < L - 1):
        IO.writeColoredSegmentationVideo(l + 1, svVideo, fig, None, False,source)
    else:
        IO.writeColoredSegmentationVideo(l + 1, svVideo, fig, video, True,source)
    # save

print("all Finished! ")
