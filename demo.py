import os
import copy
import math
import json

import numpy
import cv2

def get_board_json_path(board_id):
    return f'20231219/Board578.json'

def get_save_image_path(board_id):
    return f'20231219/Board578.png'

# 生成指定数量的彩虹渐变色
def get_rainbow_color(number):
    colors = []
    hue_values = numpy.linspace(0, 0, number, dtype = numpy.uint8)
    saturation = 255
    value = 255
    for hue in hue_values:
        hsv = numpy.array([[[hue, saturation, value]]], dtype = numpy.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        rgb = tuple(map(int, rgb[0][0]))
        colors.append(rgb)

    return colors

# 获取某一结点的bounding box
def get_bbox(node):
    x = numpy.zeros(1, dtype = float)
    y = numpy.zeros(1, dtype = float)

    for polyline in node['Self']:
        #print(polyline)
        polyline = numpy.array(polyline)
        x = numpy.concatenate((x, polyline[:, 0]))
        y = numpy.concatenate((y, polyline[:, 1]))

    max_x = math.ceil(numpy.max(x))
    max_y = math.ceil(numpy.max(y))    

    for child_node in node['InsideParts']:
        max_x_child, max_y_child = get_bbox(child_node)
        max_x = max(max_x, max_x_child)
        max_y = max(max_y, max_y_child)

    return max_x, max_y

# 递归绘制某一结点
def draw_node(image, node, depth, colors):
    for polyline in node['Self']:
        image = cv2.polylines(
            image, 
            [numpy.round(numpy.array(polyline)).astype(int)], 
            color = colors[depth % len(colors)],
            isClosed = True)
        
    for child_node in node['InsideParts']:
        image = draw_node(image, child_node, depth + 1, colors)
    return image 

# 读取排版信息并可视化
def load_board_and_visualize(board_id, mode):

    # 读取排版信息
    with open(get_board_json_path(board_id), 'r') as board_file:
        root_list = json.loads(board_file.read())
    
    # 计算bounding box并创建背景图像
    max_x = 0
    max_y = 0
    for root_node in root_list:
        max_x_node, max_y_node = get_bbox(root_node)
        max_x = max(max_x, max_x_node)
        max_y = max(max_y, max_y_node)
    board_image = numpy.ones((max_y, max_x, 3), numpy.uint8) * 255

    # 创建用于表达嵌套层次的彩虹渐变色
    colors = get_rainbow_color(10)

    # 递归绘制
    for root_node in root_list:
        board_image = draw_node(board_image, root_node, 0, colors)

    # 显示或保存        
    match mode:
        case 'show':
            cv2.imshow('test', board_image)
            cv2.waitKey()
        case 'save':
            cv2.imencode('.png', board_image)[1].tofile(get_save_image_path(board_id))

if __name__ == '__main__':
    load_board_and_visualize(578, 'save')
    # for board_id in range(1004):
    #     load_board_and_visualize(board_id, 'show')
