from keras.models import load_model
from keras.utils import np_utils
import numpy as np
import pandas as pd
import os
import sys
import cairocffi as cairo

class QdRecognition:
    def __init__(self):
        self.img_height = 28
        self.img_width = 28
        self.img_size = self.img_height * self.img_width
        self.img_dim = 1
        self.num_classes = 1
        self.model_path = os.path.join(sys.path[0], 'resources/model.h5')
        self.model = load_model(self.model_path, custom_objects={"top_3_acc": self.top_3_acc})
        self.labels = pd.read_csv(os.path.join(sys.path[0], 'resources/labels.csv'), index_col=0, header=None,squeeze=True).to_dict()

    def top_3_acc(self, y_true, y_pred):
        return metrics.top_k_categorical_accuracy(y_true, y_pred, k=3)

    def prepare(self, bitmaps):
        bitmaps = np.array(bitmaps)
        bitmaps = bitmaps.astype('float16') / 255.
        bitmaps_to_analyse = np.empty([self.num_classes, len(bitmaps), self.img_size ])
        bitmaps_to_analyse[0] = bitmaps
        bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0] * bitmaps_to_analyse.shape[1], self.img_size)
        bitmaps_to_analyse = bitmaps_to_analyse.reshape(bitmaps_to_analyse.shape[0],self.img_width, self.img_height, self.img_dim)
        return bitmaps_to_analyse

    def vector_to_raster(self, vector_images, side=28, line_diameter=16, padding=16, bg_color=(0,0,0), fg_color=(1,1,1)):
        """
        padding and line_diameter are relative to the original 256x256 image.
        """
        
        original_side = 256.
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_BEST)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(line_diameter)

        # scale to match the new size
        # add padding at the edges for the line_diameter
        # and add additional padding to account for antialiasing
        total_padding = padding * 2. + line_diameter
        new_scale = float(side) / float(original_side + total_padding)
        ctx.scale(new_scale, new_scale)
        ctx.translate(total_padding / 2., total_padding / 2.)

        raster_images = []
        for vector_image in vector_images:
            # clear background
            ctx.set_source_rgb(*bg_color)
            ctx.paint()
            
            bbox = np.hstack(vector_image).max(axis=1)
            offset = ((original_side, original_side) - bbox) / 2.
            offset = offset.reshape(-1,1)
            centered = [stroke + offset for stroke in vector_image]

            # draw strokes, this is the most cpu-intensive part
            ctx.set_source_rgb(*fg_color)        
            for xv, yv in centered:
                ctx.move_to(xv[0], yv[0])
                for x, y in zip(xv, yv):
                    ctx.line_to(x, y)
                ctx.stroke()

            data = surface.get_data()
            raster_image = np.copy(np.asarray(data)[::4])
            raster_images.append(raster_image)
        
        return raster_images
    
    def recognize(self, drawing):
        drawings = []
        drawings.append(drawing)

        rastered_drawings = self.vector_to_raster(drawings)
        prepared_drawings = self.prepare(rastered_drawings)
        predictions = self.model.predict(prepared_drawings)
        return self.labels[predictions[0].argmax()]

    # def convert_strokes_list(self, strokes):
        
    #     new_strokes = []
    #     for stroke in strokes:
    #         xx = []
    #         yy = []
    #         print(stroke)
    #         for coordinates in stroke:
    #             pass
    #             # print(coordinates)
    #             # [xx.append(x) for x,y in coordinates]
    #             # [yy.append(y) for x,y in coordinates]
    #         new_stroke = [xx, yy]
    #         new_strokes.append(new_stroke)
    #     print(new_strokes)
    
    def convert_strokes_list(self, strokes):
        new_strokes = []
        for i in strokes:
            xx = []
            yy = [] 
            new_stroke = []
            for j in i:
                    xx.append(j[0])
                    yy.append(j[1])
            new_stroke.append(xx)
            new_stroke.append(yy)
            new_strokes.append(new_stroke)
        return new_strokes           
       
        
if __name__ == '__main__':
    #proper type
    image_data = [((7, 14, 22, 38, 90, 147, 175, 201, 233, 250, 255, 245, 175, 73, 0), (4, 38, 49, 60, 80, 88, 88, 79, 51, 29, 14, 11, 9, 0, 1)), ((71, 69, 72, 96, 179, 184, 182), (80, 96, 101, 111, 119, 114, 98)), ((74, 39, 20, 15, 11, 10, 19, 35, 211, 224, 229, 221, 178), (105, 105, 107, 110, 116, 142, 155, 160, 169, 148, 127, 122, 119))]
    
    # improper type
    image_strokes = [[(7, 4), (14, 38), (22, 49), (38, 60), (90, 80), (147, 88), (175, 88), (201, 79), (233, 51), (250, 29), (255, 14), (245, 11), (175, 9), (73, 0), (0, 1)], [(71, 80), (69, 96), (72, 101), (96, 111), (179, 119), (184, 114), (182, 98)], [(74, 105), (39, 105), (20, 107), (15, 110), (11, 116), (10, 142), (19, 155), (35, 160), (211, 169), (224, 148), (229, 127), (221, 122), (178, 119)]]
    
    
    # dog_draft = [[(299, 112), (300, 112), (301, 112), (302, 112), (303, 113), (304, 113), (305, 113), (306, 113), (307, 113), (308, 113), (308, 112), (308, 111), (308, 110), (308, 109), (307, 109), (306, 109), (305, 109), (304, 109), (303, 109), (302, 109)],[(299, 112), (300, 112), (301, 112), (302, 112), (303, 113), (304, 113), (305, 113), (306, 113), (307, 113), (308, 113), (308, 112), (308, 111), (308, 110), (308, 109), (307, 109), (306, 109), (305, 109), (304, 109), (303, 109), (302, 109)]]
    
    phone_real_draft = [[(103, 96), (103, 98), (103, 102), (103, 106), (103, 107), (103, 108), (103, 110), (103, 110), (103, 111), (103, 113), (103, 114), (103, 115), (103, 118), (103, 120), (103, 121), (103, 123), (103, 125), (103, 125), (104, 128), (104, 129), (104, 130), (104, 132), (104, 133), (104, 134), (104, 135), (104, 136), (104, 137), (104, 138), (104, 138), (104, 140), (104, 140), (104, 141), (104, 143), (104, 144), (104, 146), (104, 147), (104, 151), (104, 153), (104, 155), (104, 160), (104, 162), (104, 167), (104, 176), (104, 179), (104, 183), (104, 185), (104, 186), (104, 191), (104, 192), (104, 196), (104, 197), (104, 201), (104, 203), (104, 205), (104, 205), (104, 206), (104, 208), (104, 209), (104, 212), (104, 212), (104, 214), (104, 215), (104, 216), (104, 219), (104, 219), (104, 222), (104, 222), (104, 225), (104, 225), (104, 225), (104, 227), (104, 228), (104, 228), (104, 231), (104, 232), (104, 234), (104, 235), (104, 236), (104, 239), (104, 240), (104, 242), (104, 242), (104, 243), (104, 244), (104, 245), (104, 246), (104, 251), (104, 253), (104, 256), (104, 258), (104, 259), (104, 260), (104, 262), (104, 263), (104, 266), (104, 267), (104, 270), (104, 270), (104, 271), (104, 273), (104, 274), (104, 274), (104, 277), (104, 278), (104, 279), (104, 280), (104, 281), (104, 284), (104, 285), (104, 289), (104, 290), (104, 295), (104, 297), (104, 301), (104, 302), (104, 303), (104, 306), (104, 307), (104, 309), (104, 310), (104, 312), (104, 314), (104, 315), (104, 318), (104, 318), (105, 321), (106, 322), (107, 325), (108, 326), (109, 327), (111, 328), (111, 329), (112, 329), (115, 331), (116, 332), (120, 334), (122, 334), (127, 335), (128, 336), (132, 337), (133, 337), (134, 337), (134, 337), (135, 337), (135, 337), (136, 337), (136, 337), (137, 337), (137, 337), (140, 337), (141, 337), (143, 337), (145, 336), (145, 336), (147, 335), (148, 335), (150, 335), (151, 335), (154, 335), (154, 334), (155, 334), (157, 334), (158, 334), (158, 334), (161, 334), (161, 333), (163, 333), (163, 333), (164, 333), (167, 333), (168, 333), (171, 333), (172, 333), (174, 333), (175, 333), (178, 333), (179, 333), (181, 333), (185, 335), (187, 335), (193, 337), (195, 337), (200, 339), (201, 339), (203, 339), (208, 339), (209, 340), (212, 340), (212, 340), (215, 340), (216, 340), (216, 340), (217, 340), (218, 340), (219, 340), (221, 340), (222, 340), (223, 341), (224, 341), (225, 341), (226, 341), (227, 341), (229, 341), (229, 341), (231, 341), (231, 341), (232, 341), (232, 341), (233, 341), (233, 341), (234, 341), (235, 341), (236, 341), (236, 341), (237, 341), (239, 340), (240, 340), (242, 338), (244, 337), (247, 336), (247, 336), (248, 335), (249, 335), (249, 335), (249, 335), (249, 335), (249, 334), (249, 334), (249, 334), (249, 333), (249, 333), (249, 330), (249, 328), (249, 322), (249, 319), (249, 313), (249, 311), (249, 309), (247, 305), (246, 303), (246, 301), (244, 294), (243, 292), (242, 288), (242, 286), (241, 284), (241, 280), (241, 278), (240, 277), (239, 271), (239, 267), (237, 259), (236, 256), (235, 244), (235, 242), (235, 239), (235, 232), (234, 230), (234, 225), (234, 223), (234, 222), (234, 217), (234, 215), (234, 211), (234, 210), (234, 205), (234, 204), (234, 198), (234, 197), (234, 195), (234, 191), (234, 189), (234, 186), (234, 185), (234, 183), (234, 182), (234, 181), (234, 177), (234, 176), (234, 173), (234, 172), (234, 169), (234, 168), (234, 165), (234, 164), (234, 162), (235, 157), (235, 153), (235, 149), (236, 147), (236, 145), (236, 142), (236, 141), (237, 139), (239, 133), (240, 130), (241, 125), (242, 124), (242, 121), (242, 120), (243, 119), (243, 117), (243, 116), (243, 114), (243, 111), (243, 110), (243, 108), (243, 107), (243, 103), (243, 101), (241, 92), (241, 90), (239, 84), (239, 83), (237, 79), (237, 78), (236, 77), (235, 75), (235, 75), (235, 74), (235, 74), (234, 73), (234, 73), (233, 73), (232, 73), (229, 72), (228, 72), (226, 71), (221, 70), (220, 69), (217, 69), (216, 69), (215, 69), (214, 69), (213, 69), (210, 69), (210, 69), (206, 69), (205, 69), (200, 69), (198, 69), (196, 69), (193, 69), (192, 69), (191, 69), (187, 69), (186, 69), (184, 69), (183, 69), (182, 69), (180, 69), (179, 69), (178, 69), (177, 69), (175, 69), (174, 69), (172, 69), (171, 69), (170, 69), (168, 69), (168, 69), (165, 69), (164, 69), (162, 69), (159, 69), (158, 69), (156, 69), (149, 70), (146, 70), (139, 70), (137, 71), (130, 72), (128, 72), (127, 72), (123, 72), (122, 72), (119, 72), (118, 72), (115, 72), (114, 72), (113, 72), (109, 72), (108, 72), (105, 72), (104, 73), (101, 73), (100, 73), (99, 74), (97, 74), (96, 75), (95, 75), (95, 75), (95, 75), (95, 76), (95, 76), (95, 77), (95, 77), (95, 78), (95, 78), (95, 78), (96, 79), (96, 79), (96, 79), (97, 80), (97, 80), (99, 85), (99, 86), (100, 88), (100, 89), (101, 90), (101, 91), (101, 91), (101, 92), (101, 92), (101, 92), (101, 92), (101, 92), (102, 92), (102, 93), (102, 93), (102, 94), (102, 95), (103, 98), (103, 99), (103, 100), (103, 101), (103, 101), (104, 101)],[(116, 97), (116, 104), (116, 114), (116, 117), (116, 125), (116, 127), (116, 129), (116, 133), (116, 134), (116, 135), (116, 138), (116, 139), (116, 140), (116, 141), (116, 142), (116, 143), (116, 147), (116, 148), (116, 151), (116, 151), (116, 154), (116, 155), (116, 156), (115, 157), (115, 158), (115, 159), (115, 161), (115, 162), (115, 164), (115, 164), (115, 167), (115, 168), (115, 170), (115, 171), (115, 175), (115, 175), (115, 176), (115, 177), (115, 179), (115, 180), (115, 185), (115, 188), (115, 193), (115, 195), (115, 198), (115, 206), (115, 208), (115, 211), (115, 212), (115, 214), (115, 215), (115, 216), (115, 216), (115, 217), (115, 218), (115, 218), (115, 219), (115, 220), (115, 221), (115, 221), (115, 222), (115, 222), (115, 223), (115, 224), (115, 224), (116, 225), (116, 226), (116, 227), (116, 227), (117, 228), (117, 229), (117, 229), (118, 231), (118, 231), (119, 233), (119, 234), (119, 234), (120, 236), (120, 237), (120, 238), (121, 239), (121, 241), (121, 244), (121, 246), (122, 250), (122, 251), (122, 253), (124, 257), (124, 258), (124, 260), (124, 261), (124, 262), (124, 264), (124, 265), (124, 266), (124, 269), (124, 269), (124, 271), (124, 272), (124, 272), (125, 272), (125, 272), (126, 273), (127, 274), (127, 274), (127, 274), (128, 274), (128, 274), (128, 274), (129, 274), (129, 274), (131, 274), (132, 274), (136, 275), (137, 276), (138, 276), (139, 276), (140, 276), (141, 276), (142, 276), (143, 276), (145, 276), (146, 276), (147, 276), (149, 277), (151, 277), (153, 277), (153, 277), (156, 277), (156, 277), (157, 277), (159, 277), (159, 277), (160, 277), (162, 278), (162, 278), (164, 278), (164, 278), (165, 278), (166, 279), (167, 279), (169, 279), (169, 279), (171, 279), (173, 279), (176, 280), (177, 280), (178, 280), (179, 280), (180, 280), (180, 280), (181, 280), (181, 280), (183, 280), (183, 280), (184, 280), (186, 280), (187, 280), (190, 280), (191, 280), (194, 280), (195, 280), (196, 280), (197, 280), (198, 280), (198, 280), (199, 280), (200, 280), (200, 280), (200, 280), (201, 280), (201, 280), (202, 280), (203, 279), (203, 279), (203, 278), (204, 278), (204, 277), (205, 277), (206, 276), (206, 276), (207, 276), (207, 275), (208, 274), (208, 274), (209, 273), (209, 272), (210, 272), (210, 272), (210, 271), (210, 271), (211, 271), (211, 271), (212, 269), (212, 269), (213, 268), (213, 267), (213, 267), (213, 266), (213, 265), (213, 264), (213, 263), (213, 262), (214, 261), (214, 261), (214, 258), (214, 258), (214, 254), (214, 252), (214, 247), (214, 245), (214, 241), (214, 240), (214, 237), (213, 235), (213, 233), (213, 230), (213, 228), (213, 227), (213, 224), (213, 223), (213, 222), (212, 221), (212, 220), (212, 218), (212, 217), (212, 216), (212, 213), (212, 213), (212, 209), (212, 209), (212, 207), (211, 206), (211, 204), (211, 203), (211, 202), (211, 201), (211, 198), (211, 197), (211, 194), (211, 193), (211, 189), (211, 188), (211, 184), (211, 183), (211, 179), (211, 177), (211, 175), (211, 172), (211, 171), (211, 169), (211, 166), (211, 165), (211, 164), (211, 163), (211, 163), (211, 161), (211, 160), (211, 156), (211, 155), (211, 150), (211, 148), (211, 145), (211, 144), (211, 143), (211, 140), (211, 139), (211, 138), (211, 136), (211, 135), (211, 133), (211, 131), (211, 131), (211, 130), (211, 128), (211, 128), (211, 126), (211, 126), (211, 124), (211, 124), (211, 124), (211, 122), (211, 121), (211, 121), (211, 118), (211, 117), (211, 114), (211, 113), (211, 112), (211, 111), (211, 110), (211, 105), (211, 103), (211, 99), (211, 99), (210, 96), (210, 95), (210, 95), (209, 94), (209, 93), (209, 93), (209, 92), (208, 92), (208, 92), (208, 91), (208, 91), (207, 90), (207, 90), (207, 90), (206, 90), (206, 90), (205, 90), (204, 90), (203, 90), (197, 88), (195, 88), (191, 86), (187, 86), (186, 86), (183, 86), (182, 85), (180, 85), (180, 85), (177, 85), (176, 85), (175, 84), (174, 84), (172, 84), (172, 84), (171, 84), (171, 84), (168, 84), (168, 84), (167, 84), (165, 84), (164, 84), (163, 84), (160, 84), (160, 84), (158, 84), (157, 84), (155, 84), (155, 84), (154, 84), (154, 84), (153, 84), (153, 85), (153, 85), (152, 85), (152, 85), (152, 85), (152, 85), (151, 85), (151, 85), (150, 86), (147, 86), (145, 86), (141, 87), (135, 89), (133, 89), (132, 89), (131, 89), (131, 89), (131, 89), (131, 89), (130, 89), (130, 89), (129, 90), (128, 90), (127, 90), (125, 91), (123, 91), (122, 92), (121, 92), (120, 92), (120, 93), (120, 93)],[(163, 301), (162, 301), (161, 301), (159, 301), (158, 302), (158, 302), (158, 302), (158, 303), (158, 303), (158, 303), (158, 304), (158, 304), (158, 304), (158, 304), (158, 305), (158, 306), (158, 306), (158, 307), (158, 307), (159, 308), (159, 308), (159, 309), (159, 309), (159, 310), (159, 310), (159, 310), (160, 310), (160, 311), (160, 311), (161, 312), (162, 312), (162, 313), (164, 314), (164, 315), (165, 315), (166, 316), (166, 316), (167, 316), (167, 316), (168, 316), (168, 316), (169, 317), (169, 317), (169, 317), (170, 317), (170, 317), (171, 317), (172, 317), (173, 317), (174, 317), (176, 317), (177, 317), (178, 317), (179, 316), (180, 316), (182, 315), (182, 315), (183, 314), (183, 314), (184, 313), (185, 313), (185, 312), (185, 312), (185, 312), (185, 311), (185, 311), (185, 311), (185, 310), (185, 310), (185, 310), (185, 307), (185, 306), (185, 304), (185, 301), (185, 299), (185, 297), (185, 293), (185, 293), (185, 292), (185, 291), (185, 291), (185, 291), (184, 291), (184, 291), (184, 291), (184, 291), (183, 291), (182, 290), (178, 289), (176, 289), (175, 289), (172, 289), (171, 289), (171, 289), (171, 289), (171, 289), (171, 289), (171, 290), (171, 290), (170, 290), (170, 291), (170, 291), (169, 292), (169, 293), (168, 294), (168, 294), (167, 295), (167, 296), (167, 297), (166, 297), (166, 297), (166, 298), (166, 299), (166, 299), (165, 301), (165, 301), (165, 302), (164, 302), (164, 303)]]
    
    qd = QdRecognition()
    # print(qd.recognize(image_data))
    converted = qd.convert_strokes_list(phone_real_draft)
    print(qd.recognize(converted))
    