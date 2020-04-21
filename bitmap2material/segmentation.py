from skimage import io, color
from skimage.future import graph
from skimage.filters import threshold_li
from skimage.segmentation import slic, mark_boundaries
from skimage.util import img_as_float

import numpy as np
from fit_square import fit_square

def show_foreground(img, labels, foreground_labels):
    mask = np.isin(labels, foreground_labels) * 1.0

    io.imshow(mark_boundaries(mask, labels))
    io.show()


def simple_edge_threshold(edges, eps=1e-4):
    return 1 - eps

def simple_edge_resolver(edge, threshold, RAG):
    return edge[2]['weight'] > threshold

def default_filter(foreground_labels, labels, RAG):

    while True:
        filtered = next(
            filter(
                lambda node: node not in foreground_labels and
                    sum(1 for e in RAG.edges(node) if e[1] not in foreground_labels) <= 1,
                RAG.nodes()),
            False)
        if filtered is False:
            break
        foreground_labels.append(filtered)

    while True:
        filtered = next(
            filter(
                lambda node: node in foreground_labels and
                    sum(1 for e in RAG.edges(node) if e[1] in foreground_labels) <= 1,
                RAG.nodes()),
            False)
        if not filtered:
            break
        foreground_labels.remove(filtered)

    sure_bg = []
    outside_labels = list(labels[0])
    outside_labels.extend(labels[-1])
    outside_labels.extend(labels[:,0])
    outside_labels.extend(labels[:,-1])
    for node in RAG.nodes():

        if node in sure_bg:
            continue

        is_fg = node in foreground_labels
        blob = [node,]

        # blob building
        for n in blob:
            blob.extend(
                filter(lambda x:
                    x not in blob and
                    ((x in foreground_labels) == is_fg),
                RAG.neighbors(n)))

        # blob resolving
        if any(np.isin(blob, outside_labels)) and not is_fg:
            sure_bg.extend(blob)
            continue
        elif any(np.isin(blob, outside_labels)) and is_fg:
            for label in blob:
                foreground_labels.remove(label)
            continue
        elif not is_fg:
            foreground_labels.extend(blob)
        
    return foreground_labels



def find_foreground(img, labels, RAG, eps=1e-4, calculate_edge_threshold=simple_edge_threshold,
                    resolve_edge=simple_edge_resolver, post_filter=default_filter, verbose=False,
                     interactive=False, binary=False, isPlotting=False):

    center = labels[labels.shape[0]//2, labels.shape[1]//2]
    queue = [center,]
    banned = []
    counter = 0

    if verbose:
        print('Constructing foreground mask...', flush=True)

    for label in queue:

        if verbose:
            pass
            #print('Proccessing #' + str(label))

        edges = RAG.edges(label, data=True)
        weightes = list(map(lambda e: e[2]['weight'], edges))

        threshold = calculate_edge_threshold(edges, eps=eps)

        if verbose: 
            pass
            #print('Edge thresh:\t' + str(threshold))
            #print('Min edge:\t' + str(min(weightes)))
            #print('Max edge:\t' + str(max(weightes)))
        
        for edge in edges:
            if edge[1] in queue or edge[1] in banned:
                continue
            
            if resolve_edge(edge, threshold, RAG):
                if verbose:
                    pass
                    #print(str(edge) + ' Signing in...')
                queue.append(edge[1])
            else:
                banned.append(edge[1])
                if verbose:
                    pass
                    #print(str(edge) + ' Above thresh...')

        if interactive:
            if counter and counter <= len(queue):
                counter = 0
            elif counter:
                #print('<%s/%s/%s/%s> ::> ' % (queue.index(label) + 1, len(queue), len(banned), labels.max()))
                continue
        
            cmd = input('<%s/%s/%s/%s> ::> ' % (queue.index(label) + 1, len(queue), len(banned), labels.max()))
            if cmd == 'show':
                if isPlotting:
                    show_foreground(img, labels, queue)
            if cmd == 'queue':
                pass
                #print(queue)
            if 'till' in cmd:
                counter = int(cmd.split(' ')[1])

    if verbose:
        if isPlotting:
            show_foreground(img, labels, queue)
        print('Filtering mask...', flush=True)

    foreground = post_filter(queue, labels, RAG)

    if verbose:
        if isPlotting:
            show_foreground(img, labels, foreground)

    if binary:
        return np.isin(labels, foreground)
    else:
        return np.isin(labels, foreground) * 1.0


def generate_texture(img, slic_n=200, slic_compactness=25,
                     rag_from_binary=False, edge_threshold=1e-4, verbose=False, isPlotting=False):
    img = img_as_float(img)

    if rag_from_binary:
        if verbose:
            print('Applying initial thresholding...', flush=True)
        grey_img = color.rgb2grey(img)
        binary_mask = (grey_img > threshold_li(grey_img)) * 1.0

    if verbose:
        print('Constructing superpixels...', flush=True)
    segments = slic(img, n_segments=slic_n, compactness=slic_compactness)
    if verbose:
        out_avg = color.label2rgb(segments, img, kind='avg')  
        if(isPlotting):      
            io.imshow(out_avg)
            io.show()

    if verbose:
        print('Building RAG...', flush=True)
    if rag_from_binary:
        RAG = graph.rag_mean_color(binary_mask, segments, mode='similarity')
    else:
        RAG = graph.rag_mean_color(img, segments, mode='similarity')
    if verbose:
        if(isPlotting):
            graph.show_rag(segments, RAG, img, border_color=(1,0.7,0))
            io.show()

    foreground_mask = find_foreground(img, segments, RAG, eps=edge_threshold, verbose=verbose)

    if foreground_mask.any():
        vertex, side = fit_square(foreground_mask, verbose=verbose)
        texture_patch = img[vertex[0]:vertex[0]+side+1,vertex[1]:vertex[1]+side+1]
        if verbose:
            if(isPlotting):
                io.imshow(texture_patch)
                io.show()
        return texture_patch
    else:
        print('Texture can\'t be generated, try different parameters')
        return np.array([])


if __name__ == "__main__":

    path = input('Enter image name/path: ')

    try:
        img = io.imread(path)
    except FileNotFoundError:
        print('File don\'t exist!')

    generate_texture(img, verbose=True)

