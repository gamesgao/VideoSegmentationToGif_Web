from __future__ import division

import math
import random
import sys
import cv2
import time
import json
import imageio

from video import *
from video_graph import *


class GraphSegmentationDistance:
    def __init__(self):
        self._weights = []
        pass

    def __del__(self):
        pass

    def __eq__(self, distance):
        self._weights = distance._weights
        pass

    def __call__(self, n, m):
        pass


class GraphSegmentationManhattenRGB(GraphSegmentationDistance):
    def __init__(self):
        GraphSegmentationDistance.__init__(self)
        self.__D = 255 + 255 + 255

    def __call__(self, n, m):
        dr = abs(n.r - m.r)
        dg = abs(n.g - m.g)
        db = abs(n.b - m.b)
        return (dr + dg + db) / self.__D


class GraphSegmentationEuclideanRGB(GraphSegmentationDistance):
    def __init__(self):
        GraphSegmentationDistance.__init__(self)
        # Normalization.
        self.__D = math.sqrt(255 * 255 + 255 * 255 + 255 * 255)

    # Evaluate the distance given 2 nodes.
    def __call__(self, n, m):
        dr = int(n.r) - int(m.r)
        dg = int(n.g) - int(m.g)
        db = int(n.b) - int(m.b)
        return math.sqrt(dr * dr + dg * dg + db * db) / self.__D


class GraphSegmentationEuclideanRGBFlowAngle(GraphSegmentationDistance):
    def __init__(self, alpha, beta):
        GraphSegmentationDistance.__init__(self)
        self._weights.append(alpha)
        self._weights.append(beta)
        self.__D = math.sqrt(255 * 255 + 255 * 255 + 255 * 255)
        pass

    def __call__(self, n, m):
        assert (len(self._weights) == 2)
        dr = int(n.r) - int(m.r)
        dg = int(n.g) - int(m.g)
        db = int(n.b) - int(m.b)
        #dr = (n.r) - (m.r)
        #dg = (n.g) - (m.g)
        #db = (n.b) - (m.b)
        if n.t == m.t:
            # Use flow within frames.
            n_f = math.sqrt(n.fx * n.fx + n.fy * n.fy)
            m_f = math.sqrt(m.fx * m.fx + m.fy * m.fy)
            #if n_f * m_f >= 1e-6:
            cos_a = min(1.0, max(-1.0, float(n.fx * m.fx + n.fy * m.fy) / (n_f * m_f)))
            #else:
                #cos_a = 1
            a = math.acos(cos_a)
            pi = math.pi + 1e-4
            assert (0 <= a <= pi)
            return self._weights[0] * math.sqrt(int(dr * dr) + int(dg * dg) + int(db * db)) / float(self.__D) + self._weights[
                                                                                                     1] * a / pi
        else:
            return math.sqrt(int(dr * dr) + int(dg * dg) + int(db * db)) / self.__D


class GraphSegmentationMagic:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def __call__(self, S_n, S_m, e):
        pass


class GraphSegmentationMagicSimpleThreshold(GraphSegmentationMagic):
    def __init__(self, _c):
        GraphSegmentationMagic.__init__(self)
        self.__c = _c

    def __call__(self, S_n, S_m, e):
        # threshold = min(S_n.max_w + self.__c / S_n.n, S_m.max_w + self.__c / S_m.n)
        if e.w < self.__c:
            return True
        else:
            return False


class GraphSegmentationMagicThreshold(GraphSegmentationMagic):
    def __init__(self, _c):
        GraphSegmentationMagic.__init__(self)
        self.__c = _c

    def __call__(self, S_n, S_m, e):
        threshold = min((S_n.max_w + self.__c / S_n.n), (S_m.max_w + self.__c / S_m.n))
        if e.w < threshold:
            return True
        else:
            return False


class GraphSegmentationHierarchyDistance:
    # Constructs a distance without weights.
    def __init__(self):
        self._weights = []
        pass

    def __del__(self):
        pass

    # Assignment operator
    def __eq__(self, hdistance):
        self._weights = hdistance._weights

        # Evaluate the distance given 2 nodes.


class GraphSegmentationHierarchyRGBChiSquare(GraphSegmentationHierarchyDistance):
    def __init__(self):
        GraphSegmentationHierarchyDistance.__init__(self)

    # Evaluate the distance given 2 nodes.
    def __call__(self, n, m):
        assert (n.H == m.H)
        assert (n.n > 0 and m.n > 0)
        distance = 0
        n_n = n.n
        m_n = m.n
        for i in range(n.H):
            n_h = n.h[i] / n_n
            m_h = m.h[i] / m_n
            if (n_h > 0 or m_h > 0):
                distance += (n_h - m_h) * (n_h - m_h) / (n_h + m_h)
        return distance


class GraphSegmentationHierarchyRGBChiSquareFlowAngle(GraphSegmentationHierarchyDistance):
    def __init__(self, alpha, gamma):
        GraphSegmentationHierarchyDistance.__init__(self)
        self._weights.append(alpha)
        self._weights.append(gamma)

    # Evaluate the distance given 2 nodes.
    def __call__(self, n, m):
        assert (len(self._weights) == 2)
        assert (n.H == m.H)
        assert (n.n > 0 and m.n > 0)
        distance = 0.0
        n_n = n.n
        m_n = m.n
        for i in range(n.H):
            n_h = n.h[i] * 1.0 / n_n
            m_h = m.h[i] * 1.0 / m_n
            if (n_h > 0 or m_h > 0):
                distance += (n_h - m_h) * (n_h - m_h) / (n_h + m_h)

        if (n.t == m.t):
            # Use flow cues only within frame.
            n_f = math.sqrt(n.fx * n.fx + n.fy * n.fy)
            m_f = math.sqrt(m.fx * m.fx + m.fy * m.fy)
            if ((n_f * m_f)>=1e-6):
                cos_a = min(1.0, max(-1.0, (n.fx * m.fx + n.fy * m.fy) / (n_f * m_f)))
            else:
                cos_a = 1
            a = math.acos(cos_a)
            pi = math.pi + 1e-4
            assert (a >= 0 and a <= pi)
            return self._weights[0] * distance + self._weights[1] * a / pi
        else:
            # Only color cues.
            return distance


class GraphSegmentationHierarchyMagic:
    def __init__(self):
        pass

    def __del__(self):
        pass


        # Go up alevel, that is raise the threshold.

        # Decide whether to merge these two components or not.


class GraphSegmentationHierarchyMagicSimpleThreshold(GraphSegmentationHierarchyMagic):
    def __init__(self, _c, _r=2):
        GraphSegmentationHierarchyMagic.__init__(self)
        self.__c = _c
        self.__r = _r

    # Go up alevel, that is raise the threshold.
    def Raise(self):
        self.__c *= self.__r

    def __call__(self, S_n, S_m, e):
        if (e.w < self.__c):
            return True
        return False


class GraphSegmentationHierarchyMagicThreshold(GraphSegmentationHierarchyMagic):
    def __init__(self, _c, _r=2):
        GraphSegmentationHierarchyMagic.__init__(self)
        self.__c = _c
        self.__r = _r

    def Raise(self):
        self.__c *= self.__r

    # decide whether to merge these two components or not.
    def __call__(self, S_n, S_m, e):
        threshold = min(S_n.max_w + self.__c / S_n.n, S_m.max_w + self.__c / S_m.n)
        if (e.w < threshold):
            return True
        return False


class GraphSegmentationRandomness:
    def __init__(self):
        pass


class GraphSegmentationRandomnessNone(GraphSegmentationRandomness):
    def __init__(self):
        GraphSegmentationRandomness.__init__(self)
        pass

    def __call__(self, e):
        return True


class GraphSegmentationRandomnessSimple(GraphSegmentationRandomness):
    def __init__(self, _p):
        GraphSegmentationRandomness.__init__(self)
        self.__p = _p

    def __call__(self, e):
        # float
        r = random.random
        if (r <= self.__p):
            return True
        else:
            return False


class GraphSegmentation:
    def __init__(self, _distance=GraphSegmentationManhattenRGB(), _magic=GraphSegmentationMagicThreshold(25),
                 _random=GraphSegmentationRandomnessNone()):
        self.__distance = _distance
        self.__magic = _magic
        self.__random = _random
        # self.__hdistance = 0
        self.__hdistance = None
        # self.__hmagic = GraphSegmentationMagic(0)
        self.__hmagic = None
        self.__T = None
        self.__H = None
        self.__W = None
        self.__graph = None

    def __del__(self):
        pass

    def setDistance(self, _distance):
        self.__distance = _distance

    def setMagic(self, _magic):
        self.__magic = _magic

    def setHierarchyDistance(self, _hdistance):
        self.__hdistance = _hdistance

    def setHierarchyMagic(self, _hmagic):
        self.__hmagic = _hmagic

    def setRandomness(self, _random):
        self.__random = _random

    def buildGraph(self, video, flow):
        assert (video.getFrameNumber() > 0)
        assert (video.getFrameHeight() > 0)
        assert (video.getFrameWidth() > 0)

        if (flow != 0):
            assert (video.getFrameNumber() == flow.getFrameNumber())
            assert (video.getFrameHeight() == flow.getFrameHeight())
            assert (video.getFrameWidth() == flow.getFrameWidth())

        self.__T = video.getFrameNumber()
        self.__H = video.getFrameHeight()
        self.__W = video.getFrameWidth()

        self.__N = self.__T * self.__H * self.__W
        self.__graph = VideoGraph(N=self.__N)

        for t in range(self.__T):
            for i in range(self.__H):
                for j in range(self.__W):
                    n = self.__H * self.__W * t + self.__W * i + j
                    node = self.__graph.getNode(n)
                    node.i = i
                    node.j = j
                    node.t = t

                    bgr = video.get(t, i, j)

                    node.b = bgr[0]
                    node.g = bgr[1]
                    node.r = bgr[2]
                    node.H = 36
                    # Color histogram.
                    # if node.H == 0:
                    #     denominator = -2147483648
                    # else:
                    denominator = math.ceil(256. / ((float)(node.H / 3.0)))
                    # int
                    h_b = int(node.b / denominator)
                    # int
                    h_g = int(node.g / denominator)
                    # int
                    h_r = int(node.r / denominator)

                    # node.h = std::vector < int > (node.H, 0);
                    node.h = [0] * node.H

                    node.h[h_b] += 1
                    node.h[h_g] += 1
                    node.h[h_r] += 1

                    # Flow.
                    # if (t < T - 1)
                    if (flow != 0):
                        node.fx = flow.get(t, i, j)[0]
                        node.fy = flow.get(t, i, j)[1]
                        node.f = math.sqrt(node.fx * node.fx + node.fy * node.fy)
                    # else
                    # node.fx = 0
                    # node.fy = 0
                    # node.f = 0

                    # Initialize label.
                    node.l = n
                    node.id = n
                    node.n = 1

                    assert (self.__graph.getNode(n).id == n)

    def buildEdges(self):
        assert (self.__graph.getNumNodes() > 0)
        # int
        invalid = 0
        # Now add all edges and weights.
        for t in range(self.__T):
            for i in range(self.__H):
                for j in range(self.__W):
                    # int
                    n = int(self.__H * self.__W * t + self.__W * i + j)
                    node = self.__graph.getNode(n)
                    if (t < self.__T - 1):
                        # int
                        k = int(i + node.fy)
                        # int
                        l = int(j + node.fx)
                        if (k >= 0 and k < self.__H and l >= 0 and l < self.__W):
                            # int
                            m = int(self.__H * self.__W * (t + 1) + self.__W * k + l)
                            other = self.__graph.getNode(m)

                            assert (m == other.id)

                            edge = VideoEdge()
                            edge.n = n
                            edge.m = m
                            edge.w = (self.__distance)(node, other)
                            edge.r = False
                            self.__graph.addEdge(edge)
                        else:
                            invalid += 1
                    if (i < self.__H - 1):
                        # int
                        m = int(self.__H * self.__W * t + self.__W * (i + 1) + j)
                        other = self.__graph.getNode(m)
                        assert (m == other.id)
                        edge = VideoEdge()
                        edge.n = n
                        edge.m = m
                        edge.w = self.__distance(node, other)
                        edge.r = False
                        self.__graph.addEdge(edge)

                    if (j < self.__W - 1):
                        # int
                        m = int(self.__H * self.__W * t + self.__W * i + (j + 1))
                        other = self.__graph.getNode(m)
                        assert (m == other.id)
                        edge = VideoEdge()
                        edge.n = n
                        edge.m = m
                        edge.w = self.__distance(node, other)
                        edge.r = False
                        self.__graph.addEdge(edge)

    def oversegmentGraph(self):
        assert (self.__graph.getNumNodes() > 0)
        assert (self.__graph.getNumEdges() > 0)

        # int
        N = self.__graph.getNumNodes()
        # int
        E = self.__graph.getNumEdges()

        # Sort edges.
        self.__graph.sortEdges()

        for e in range(E):
            # VideoEdge
            edge = self.__graph.getEdge(e)
            if self.__random(edge):
                # VideoNode
                n = self.__graph.getNode(edge.n)
                # VideoNode
                m = self.__graph.getNode(edge.m)
                # VideoNode
                S_n = self.__graph.findNodeComponent(n)
                # VideoNode
                S_m = self.__graph.findNodeComponent(m)
                # Are the nodes in different components?
                if (S_m.id != S_n.id):
                    # Here comes the magic!
                    if (self.__magic)(S_n, S_m, edge):
                        self.__graph.merge(S_n, S_m, edge)

                else:
                    # Nodes already are in same component!
                    edge.r = True

    def enforceMinimumSegmentSize(self, M):
        assert (self.__graph.getNumNodes() > 0)
        # assert (graph.getNumEdges() > 0)
        # int
        N = self.__graph.getNumNodes()
        # int
        E = self.__graph.getNumEdges()
        for e in range(E):
            # VideoEdge
            edge = self.__graph.getEdge(e)
            if (not edge.r):
                # VideoNode
                n = self.__graph.getNode(edge.n)
                # VideoNode
                m = self.__graph.getNode(edge.m)
                # VideoNode
                S_n = self.__graph.findNodeComponent(n)
                # VideoNode
                S_m = self.__graph.findNodeComponent(m)

                if S_n.l != S_m.l:
                    if S_n.n < M or S_m.n < M:
                        self.__graph.merge(S_n, S_m, edge)

                else:
                    # Already merged nodes.
                    edge.r = True

    def buildRegionGraph(self):
        assert (self.__graph.getNumNodes() > 0)
        assert (self.__graph.getNumEdges() > 0)
        assert (self.__hdistance != 0)
        assert (self.__hmagic != 0)
        # int
        N = self.__graph.getNumNodes()
        # int
        E = self.__graph.getNumEdges()
        # Some minor checks and resets.
        for n in range(N):
            # VideoNode
            node = self.__graph.getNode(n)
            node.max_w = 0

        for e in range(E):
            # VideoEdge
            edge = self.__graph.getEdge(e)

            if not edge.r:
                # VideoNode
                n = self.__graph.getNode(edge.n)
                # VideoNode
                m = self.__graph.getNode(edge.m)

                # VideoNode
                S_n = self.__graph.findNodeComponent(n)
                # VideoNode
                S_m = self.__graph.findNodeComponent(m)

                if S_n.l != S_m.l:
                    edge.w = self.__hdistance(S_n, S_m)
                else:
                    # This edge has already been merged.
                    edge.r = True

    def addHierarchyLevel(self):
        assert (self.__graph.getNumNodes() > 0)
        # assert (graph.getNumEdges() > 0);

        assert (self.__hdistance != 0)
        assert (self.__hmagic != 0)
        self.__hmagic.Raise()

        # int
        N = self.__graph.getNumNodes()
        # int
        E = self.__graph.getNumEdges()

        for e in range(E):
            # VideoEdge
            edge = self.__graph.getEdge(e)

            if self.__random(edge):
                if (not edge.r):
                    # VideoNode
                    n = self.__graph.getNode(edge.n)
                    # VideoNode
                    m = self.__graph.getNode(edge.m)

                    # VideoNode
                    S_n = self.__graph.findNodeComponent(n)
                    # VideoNode
                    S_m = self.__graph.findNodeComponent(m)

                    # Are the nodes in different components?
                    if (S_m.id != S_n.id):
                        # Here comes the magic!
                        if self.__hmagic(S_n, S_m, edge):
                            self.__graph.merge(S_n, S_m, edge)
                    else:
                        # This edge has already beenprocessed and merged.
                        edge.r = True

    def deriveLabels(self):
        assert (self.__graph.getNumNodes() > 0)
        # // assert (graph.getNumEdges() > 0);
        # SegmentationVideo
        video = SegmentationVideo()
        for t in range(self.__T):
            # cv::Mat frame(H, W, CV_32SC1, cv::Scalar(0))
            # intersectionMatrix \
            frame = np.zeros((self.__H, self.__W), np.int32)
            for i in range(self.__H):
                for j in range(self.__W):
                    # int
                    n = int(self.__H * self.__W * t + self.__W * i + j)

                    # VideoNode
                    node = self.__graph.getNode(n)
                    # VideoNode
                    S_node = self.__graph.findNodeComponent(node)
                    max = sys.maxint
                    assert (S_node.id <= max)
                    frame[i][j] = S_node.id
            video.addFrame(frame)

        assert (video.getFrameNumber() > 0)
        assert (video.getFrameHeight() > 0)
        assert (video.getFrameWidth() > 0)
        video.relabel()
        return video

    def deriveLabelsNew(self):
        assert (self.__graph.getNumNodes() > 0)
        # // assert (graph.getNumEdges() > 0);
        # SegmentationVideo
        video = SegmentationVideo()
        clrToN = {}
        cnt = 0
        for t in range(self.__T):
            for i in range(self.__H):
                for j in range(self.__W):
                    n = int(self.__H * self.__W * t + self.__W * i + j)
                    node = self.__graph.getNode(n)
                    if (not (clrToN.has_key((node.r, node.b, node.g)))):
                        cnt += 1
                        clrToN[(node.r, node.b, node.g)] = cnt

        for t in range(self.__T):
            # cv::Mat frame(H, W, CV_32SC1, cv::Scalar(0))
            # intersectionMatrix \
            frame = np.zeros((self.__H, self.__W), np.int32)
            for i in range(self.__H):
                for j in range(self.__W):
                    # int
                    n = int(self.__H * self.__W * t + self.__W * i + j)

                    # VideoNode
                    node = self.__graph.getNode(n)
                    # VideoNode
                    #S_node = self.__graph.findNodeComponent(node)
                    #max = sys.maxint
                    #assert (S_node.id <= max)
                    frame[i][j] = clrToN[(node.r, node.b, node.g)]
            video.addFrame(frame)

        assert (video.getFrameNumber() > 0)
        assert (video.getFrameHeight() > 0)
        assert (video.getFrameWidth() > 0)
        #video.relabel()
        return video

    def buildAndLabelAndPrint(self, video, sevideo, source, fig):
        assert (video.getFrameNumber() > 0)
        assert (video.getFrameHeight() > 0)
        assert (video.getFrameWidth() > 0)
        self.__T = min(video.getFrameNumber(), sevideo.getFrameNumber())
        self.__H = video.getFrameHeight()
        self.__W = video.getFrameWidth()
        self.__N = self.__T * self.__H * self.__W
        clrToN = {}
        clrToWhether = {}
        cnt = 0
        for t in range(self.__T):
            for i in range(self.__H):
                for j in range(self.__W):
                    n = self.__H * self.__W * t + self.__W * i + j
                    bgr = sevideo.get(t, i, j)
                    b = bgr[0]
                    g = bgr[1]
                    r = bgr[2]
                    if (not (clrToN.has_key((r, b, g)))):
                        cnt += 1
                        clrToN[(r, b, g)] = cnt
        cv2.imwrite("./public/images/result/" + source + '.jpg', sevideo.getFrame(0))
        sys.stdout.flush()
        time.sleep(1)
        print (source)
        sys.stdout.flush()
        name = raw_input("")
        fig = json.loads(name)
        bgLabels = cv2.imread("./videoTemp/" + source.split(".")[0] + '.bg')
        bgHeight = len(bgLabels)
        bgWidth = len(bgLabels[0])
        gif = []
        for t in range(self.__T):
            coloredLabels = np.zeros((self.__H, self.__W, 3), dtype=np.uint8)
            if (t == 0):
                for i in range(self.__H):
                    for j in range(self.__W):
                        if (fig[i][j] == 1):
                            bgr = sevideo.get(t, i, j)
                            b = bgr[0]
                            g = bgr[1]
                            r = bgr[2]
                            clrToWhether[(b, g, r)] = 1
            for i in range(self.__H):
                for j in range(self.__W):
                    bgr = sevideo.get(t, i, j)
                    b = bgr[0]
                    g = bgr[1]
                    r = bgr[2]
                    if clrToWhether.has_key((b, g, r)):
                        coloredLabels[i][j][0] = video.get(t, i, j)[2]
                        coloredLabels[i][j][1] = video.get(t, i, j)[1]
                        coloredLabels[i][j][2] = video.get(t, i, j)[0]

                    else:
                        coloredLabels[i][j][0] = bgLabels[i % bgHeight][j % bgWidth][2]
                        coloredLabels[i][j][1] = bgLabels[i % bgHeight][j % bgWidth][1]
                        coloredLabels[i][j][2] = bgLabels[i % bgHeight][j % bgWidth][0]
            gif.append(coloredLabels[:])

        imageio.mimsave("./public/images/result/" + source + '.gif', gif)
