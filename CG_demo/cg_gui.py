#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QColorDialog,
    QInputDialog,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QSlider,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QToolBar,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF, Qt
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.dot_num=0
        self.start_xy=None
        self.plist=None
        self.angel=0
        self.offset_x=0
        self.offset_y=0

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id, dot_num):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.dot_num = dot_num

    def set_dot_num(self, algorithm, dot_num):
        if(self.temp_algorithm == algorithm):
            self.dot_num = dot_num

    def start_translate(self):
        if self.selected_id=='':
            return
        self.status = 'translate'
        self.temp_item=self.item_dict[self.selected_id]
        self.plist=self.temp_item.p_list

    def start_rotate(self):
        if self.selected_id=='':
            return
        if self.item_dict[self.selected_id].item_type == 'ellipse':
            self.status=''
            return
        self.status = 'rotate'
        self.temp_item=self.item_dict[self.selected_id]
        self.plist=self.temp_item.p_list
        self.angel=0

    def start_scale(self):
        if self.selected_id=='':
            return
        self.status = 'scale'
        self.temp_item=self.item_dict[self.selected_id]
        self.plist=self.temp_item.p_list

    def start_clip(self, algorithm):
        if self.selected_id=='':
            return
        if self.item_dict[self.selected_id].item_type != 'line':
            self.status=''
            return
        self.status = 'clip'
        self.temp_item=self.item_dict[self.selected_id]
        self.plist=self.temp_item.p_list
        self.temp_algorithm = algorithm

    def start_select(self):
        self.status = 'select'

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.temp_item = None

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
        
    def clear_canvas(self):
        if(self.temp_item==None or self.status=='' or self.status=='translate' or self.status=='rotate' or self.status=='scale' or self.status=='clip'):
            pass
        else:
            self.scene().removeItem(self.temp_item)
        for item in self.item_dict:
            self.scene().removeItem(self.item_dict[item])
        self.updateScene([self.sceneRect()])
        self.item_dict={}
        self.selected_id=''
        self.status=''
        self.temp_item = None

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        if selected=='':
            return
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.col)
            self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.col)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if(self.temp_item == None):
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.col)
                self.scene().addItem(self.temp_item)
            else:
                x0,y0=self.temp_item.p_list[0]
                if(((x0-x)**2+(y0-y)**2)<40 and len(self.temp_item.p_list)>=3):
                    self.temp_item.finish_draw=True
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append([x,y])
        elif self.status == 'curve':
            if(self.temp_item == None):
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.col)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x,y])
        elif self.status == 'translate':
            self.start_xy=[x,y]
        elif self.status == 'rotate':
            if event.button() == Qt.LeftButton:
                self.start_xy=[x,y]
            else:
                self.plist =self.temp_item.p_list    
                self.status=''
        elif self.status == 'scale':
            self.start_xy=[x,y]
        elif self.status == 'clip':
            self.start_xy=[x,y]
        elif self.status == 'select':
            selected=self.scene().itemAt(pos,QtGui.QTransform())
            for item in self.item_dict:
                if(self.item_dict[item]==selected):
                    if self.selected_id != '':
                        self.item_dict[self.selected_id].selected = False
                        self.item_dict[self.selected_id].update()
                        self.updateScene([self.sceneRect()])
                    self.selected_id = item
                    self.item_dict[item].selected = True
                    self.item_dict[item].update()

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            if (self.temp_item == None):
                pass
            else:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'ellipse':
            if (self.temp_item == None):
                pass
            else:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon':
            if (self.temp_item == None):
                pass
            else:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'curve':
            if (self.temp_item == None):
                pass
            else:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            self.temp_item.p_list=alg.translate(self.plist,x-self.start_xy[0],y-self.start_xy[1])
        elif self.status == 'scale':
            s = ((x - self.start_xy[0])**2+(y - self.start_xy[1])**2) / 10000
            self.temp_item.p_list=alg.scale(self.plist,self.start_xy[0],self.start_xy[1],s)
        elif self.status == 'clip':
            self.temp_item.p_list=alg.clip(self.plist,self.start_xy[0],self.start_xy[1],x,y,self.temp_algorithm)
        self.updateScene([self.sceneRect()])
        #self.prepareGeometryChange()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            if (self.temp_item == None):
                pass
            else:
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                self.temp_item.p_list[-1] = [x, y]
                self.updateScene([self.sceneRect()])
        elif self.status == 'curve':
            if (self.temp_item == None):
                pass
            else:
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                self.temp_item.p_list[-1] = [x, y]
                self.updateScene([self.sceneRect()])
                if(len(self.temp_item.p_list)==self.dot_num):
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
        elif self.status == 'translate':
            self.plist =self.temp_item.p_list
        elif self.status == 'scale':
            self.plist =self.temp_item.p_list
        elif self.status == 'rotate':
            self.plist =self.temp_item.p_list
        elif self.status == 'clip':
            self.plist =self.temp_item.p_list    
            self.status=''
        super().mouseReleaseEvent(event)

    def wheelEvent (self, event):
        if self.status == 'rotate':
            if(event.angleDelta().y()<0):
                self.angel=self.angel-1
            else:
                self.angel=self.angel+1
            self.temp_item.p_list=alg.rotate(self.plist,self.start_xy[0],self.start_xy[1],self.angel)
        self.updateScene([self.sceneRect()])
        #super(). wheelEvent(event)



class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', col: QColor = QColor(0,0,0),parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.col=col
        self.finish_draw=False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.col)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            if(self.finish_draw==True):
                item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            else:
                item_pixels = alg.draw_part_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.col)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.setPen(self.col)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            if(len(self.p_list)<=3 and self.algorithm=='B-spline'):
                item_pixels = alg.draw_part_polygon(self.p_list, 'Bresenham')
            else:
                item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.col)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon':
            x, y = self.p_list[0]
            x0, y0 = x, y
            x1, y1 = x, y
            for i in range(1,len(self.p_list)):
                x, y = self.p_list[i]
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            w = x1 - x0
            h = y1 - y0
            return QRectF(x0 - 1, y0 - 1, w + 2, h + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            x, y = self.p_list[0]
            x0, y0 = x, y
            x1, y1 = x, y
            for i in range(1,len(self.p_list)):
                x, y = self.p_list[i]
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            w = x1 - x0
            h = y1 - y0
            return QRectF(x0 - 1, y0 - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        self.col=QColor(0, 0, 0)
        self.w=1000
        self.h=1000
        self.bezier_num=3
        self.bspline_num=4

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.w, self.h)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.w, self.h)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        self.canvas_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff) 

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        select_item = edit_menu.addAction('选择图元')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        select_item.triggered.connect(self.select_item_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(self.w, self.h)
        self.setWindowTitle('CG Demo')

        setbar=QToolBar()
        self.addToolBar(Qt.LeftToolBarArea,setbar)
 
        self.bezier_box = QSpinBox()
        self.bezier_box.setRange(3, 20)
        self.bezier_box.setSingleStep(1)
        self.bezier_box.setValue(self.bezier_num)
        setbar.addWidget(QLabel("Bezier控制点数"))
        setbar.addWidget(self.bezier_box)
        setbar.addSeparator()
        self.bspline_box = QSpinBox()
        self.bspline_box.setRange(4, 20)
        self.bspline_box.setSingleStep(1)
        self.bspline_box.setValue(self.bspline_num)
        setbar.addWidget(QLabel("B样条阶数"))
        setbar.addWidget(self.bspline_box)
        self.bezier_box.valueChanged.connect(self.set_bezier_num)
        self.bspline_box.valueChanged.connect(self.set_bspline_num)

        self.w=600
        self.h=600
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.w, self.h)
        self.canvas_widget.resize(self.w,self.h)
        self.canvas_widget.setFixedSize(self.w, self.h)
        self.statusBar().showMessage('空闲')
        self.setMaximumHeight(self.h)
        self.setMaximumWidth(self.w)
        self.resize(self.w, self.h)

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_bezier_num(self):
        self.bezier_num=self.bezier_box.value()
        self.canvas_widget.set_dot_num('Bezier',self.bezier_num)

    def set_bspline_num(self):
        self.bspline_num=self.bspline_box.value()
        self.canvas_widget.set_dot_num('B-spline',self.bspline_num)

    def set_pen_action(self):
        self.statusBar().showMessage('设置画笔')
        col = QColorDialog.getColor()
        if col.isValid():
            self.col=col
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def reset_canvas_action(self):
        self.item_cnt=0
        self.canvas_widget.clear_canvas()
        self.statusBar().showMessage('重置画布')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.list_widget.clear()
        
        dialog = QDialog()
        dialog.setWindowTitle('重置画布')
        formlayout = QFormLayout(dialog)
        box1 = QSpinBox(dialog)
        box1.setRange(100, 1000)
        box1.setSingleStep(1)
        box1.setValue(self.w)
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(100, 1000)
        slider1.setSingleStep(1)
        slider1.setValue(self.w)
        slider1.setTickPosition(QSlider.TicksBelow)
        slider1.setTickInterval(100)
        box2 = QSpinBox(dialog)
        box2.setRange(100, 1000)
        box2.setSingleStep(1)
        box2.setValue(self.h)
        slider2 = QSlider(Qt.Horizontal)
        slider2.setRange(100, 1000)
        slider2.setSingleStep(1)
        slider2.setValue(self.h)
        slider2.setTickPosition(QSlider.TicksBelow)
        slider2.setTickInterval(100)
        slider1.valueChanged.connect(box1.setValue)
        box1.valueChanged.connect(slider1.setValue)
        slider2.valueChanged.connect(box2.setValue)
        box2.valueChanged.connect(slider2.setValue)
        formlayout.addRow('Width:', box1)
        formlayout.addRow(slider1)
        formlayout.addRow('Height:', box2)
        formlayout.addRow(slider2)
    
        box3 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box3.accepted.connect(dialog.accept)
        box3.rejected.connect(dialog.reject)
        formlayout.addRow(box3)
        
        if dialog.exec():
            if(box1.value()<100 or box1.value()>1000 or box2.value()<100 or box2.value()>1000):
                QMessageBox.about(self, "提示", "修改失败,请保证输入的数字大于等于100小于等于1000")
            else:
                self.w = box1.value()
                self.h = box2.value()
            self.scene = QGraphicsScene(self)
            self.scene.setSceneRect(0, 0, self.w, self.h)
            self.canvas_widget.resize(self.w,self.h)
            self.canvas_widget.setFixedSize(self.w, self.h)
            self.statusBar().showMessage('空闲')
            self.setMaximumHeight(self.h)
            self.setMaximumWidth(self.w)
            self.resize(self.w, self.h)
    
    def save_canvas_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.statusBar().showMessage('保存画布')
        dialog=QFileDialog()
        filename=dialog.getSaveFileName(filter="Image Files(*.jpg *.png *.bmp)")
        if filename[0]:
            res=self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            res.save(filename[0])

    def line_naive_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_bresenham_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('中点圆生成算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        '''text, ok = QInputDialog.getText(self, 'Bezier算法绘制曲线', '请输入控制点数目:')
        if ok:
            n=int(str(text))
        else:
            return
        if(n<=1):
            QMessageBox.about(self, "提示", "请保证输入的数字大于1")
            return'''

        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_curve('Bezier', self.get_id(), self.bezier_num)
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        '''text, ok = QInputDialog.getText(self, 'B-spline算法绘制曲线', '请输入控制点数目:')
        if ok:
            n=int(str(text))
        else:
            return
        if(n<=3):
            QMessageBox.about(self, "提示", "请保证输入的数字大于3")
            return'''

        if(self.item_cnt>0):
            self.item_cnt-=1
        self.canvas_widget.start_draw_curve('B-spline', self.get_id(), self.bspline_num)
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('裁剪')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('裁剪')

    def select_item_action(self):
        self.canvas_widget.start_select()
        self.statusBar().showMessage('选择图元')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
